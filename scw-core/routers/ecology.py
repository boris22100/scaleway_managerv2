from fastapi import APIRouter, Header, HTTPException
from datetime import datetime
import requests

router = APIRouter(prefix="/ecology", tags=["Écologie"])

@router.get("/metrics")
def get_metrics(x_auth_token: str = Header(...)):
    headers = {"X-Auth-Token": x_auth_token, "Content-Type": "application/json"}
    
    # 1. Récupérer l'ID de l'organisation
    r_org = requests.get("https://api.scaleway.com/account/v3/organizations", headers=headers)
    if r_org.status_code != 200 or not r_org.json().get('organizations'):
        raise HTTPException(status_code=400, detail="Organisation introuvable")
    
    org_id = r_org.json()['organizations'][0]['id']
    
    # 2. Récupérer les métriques du mois en cours
    now = datetime.now()
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    end_date = now.isoformat() + "Z"
    
    metrics_url = "https://api.scaleway.com/environmental-impact/v1alpha1/usage/dashboard/metrics"
    params = {"organization_id": org_id, "start_date": start_date, "end_date": end_date}
    
    r_metrics = requests.get(metrics_url, params=params, headers=headers)
    if r_metrics.status_code == 200:
        return r_metrics.json().get("metrics", [])
    
    raise HTTPException(status_code=r_metrics.status_code, detail=r_metrics.text)