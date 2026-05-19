from fastapi import APIRouter, Header, HTTPException, Body
import requests

router = APIRouter(prefix="/dns", tags=["DNS"])

def scw_headers(token: str):
    return {"X-Auth-Token": token, "Content-Type": "application/json"}

@router.get("/zones")
def get_zones(x_auth_token: str = Header(...)):
    r = requests.get("https://api.scaleway.com/domain/v2beta1/dns-zones?page_size=100", headers=scw_headers(x_auth_token))
    if r.status_code == 200: return r.json().get("dns_zones", [])
    raise HTTPException(status_code=r.status_code, detail="Erreur Scaleway API")

@router.get("/zones/{domain}/records")
def get_records(domain: str, x_auth_token: str = Header(...)):
    r = requests.get(f"https://api.scaleway.com/domain/v2beta1/dns-zones/{domain}/records?page_size=100", headers=scw_headers(x_auth_token))
    if r.status_code == 200: return r.json().get("records", [])
    raise HTTPException(status_code=r.status_code, detail="Erreur Scaleway API")

@router.patch("/zones/{domain}/records")
def modify_records(domain: str, payload: dict = Body(...), x_auth_token: str = Header(...)):
    # payload attendu : {"changes": [...]} correspondant au format Scaleway (add ou set)
    r = requests.patch(f"https://api.scaleway.com/domain/v2beta1/dns-zones/{domain}/records", json=payload, headers=scw_headers(x_auth_token))
    if r.status_code == 200: return {"status": "success"}
    raise HTTPException(status_code=r.status_code, detail=r.text)