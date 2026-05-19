from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import requests

router = APIRouter(prefix="/instances", tags=["Instances & Déploiement"])

def scw_headers(token: str): return {"X-Auth-Token": token, "Content-Type": "application/json"}

@router.get("/{zone}/servers")
def get_servers(zone: str, x_auth_token: str = Header(...)):
    r = requests.get(f"https://api.scaleway.com/instance/v1/zones/{zone}/servers", headers=scw_headers(x_auth_token))
    if r.status_code == 200: return r.json().get("servers", [])
    raise HTTPException(status_code=r.status_code, detail="Erreur API")

@router.post("/{zone}/servers/{server_id}/action")
def server_action(zone: str, server_id: str, action: str, x_auth_token: str = Header(...)):
    # action = "backup", "terminate", "poweron", etc.
    r = requests.post(f"https://api.scaleway.com/instance/v1/zones/{zone}/servers/{server_id}/action", 
                      json={"action": action}, headers=scw_headers(x_auth_token))
    if r.status_code in [200, 202]: return {"status": "success"}
    raise HTTPException(status_code=r.status_code, detail="Erreur action serveur")

class DeployRequest(BaseModel):
    zone: str
    name: str
    commercial_type: str
    project_id: str
    docker_compose_yml: str

@router.post("/deploy")
def deploy_instance(req: DeployRequest, x_auth_token: str = Header(...)):
    # 1. Créer l'instance
    payload = {
        "name": req.name, "commercial_type": req.commercial_type, 
        "image": "debian_bookworm", "project": req.project_id, "dynamic_ip_required": True
    }
    r = requests.post(f"https://api.scaleway.com/instance/v1/zones/{req.zone}/servers", 
                      json=payload, headers=scw_headers(x_auth_token))
    
    if r.status_code == 201:
        sid = r.json()['server']['id']
        yml = req.docker_compose_yml.replace("\n", "\n      ")
        ci = f"#cloud-config\npackage_update: true\npackages: [docker.io, docker-compose-v2]\nwrite_files:\n  - path: /app/docker-compose.yml\n    content: |\n      {yml}\nruncmd:\n  - systemctl enable --now docker\n  - cd /app && docker compose up -d"
        
        # 2. Injecter le cloud-init
        requests.patch(f"https://api.scaleway.com/instance/v1/zones/{req.zone}/servers/{sid}/user_data/cloud-init", 
                       data=ci, headers={"X-Auth-Token": x_auth_token, "Content-Type": "text/plain"})
        
        # 3. Démarrer
        requests.post(f"https://api.scaleway.com/instance/v1/zones/{req.zone}/servers/{sid}/action", 
                      json={"action": "poweron"}, headers=scw_headers(x_auth_token))
        return {"status": "success", "server_id": sid}
    
    raise HTTPException(status_code=r.status_code, detail=r.text)