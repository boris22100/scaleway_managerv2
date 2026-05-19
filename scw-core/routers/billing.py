from fastapi import APIRouter, Header, HTTPException
import requests

router = APIRouter(prefix="/billing", tags=["Facturation"])

@router.get("/invoices")
def get_invoices(project_id: str, x_auth_token: str = Header(...)):
    headers = {"X-Auth-Token": x_auth_token, "Content-Type": "application/json"}
    r = requests.get(f"https://api.scaleway.com/billing/v2beta1/invoices?project_id={project_id}", headers=headers)
    
    if r.status_code == 200:
        return r.json().get("invoices", [])
    
    raise HTTPException(status_code=r.status_code, detail="Erreur lors de la récupération des factures")