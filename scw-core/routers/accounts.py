from fastapi import APIRouter
from pydantic import BaseModel
from database import db_query

router = APIRouter(prefix="/accounts", tags=["Comptes"])

class AccountData(BaseModel):
    user_id: int
    name: str
    access_key: str
    secret_key: str
    project_id: str

@router.get("/{user_id}")
def get_accounts(user_id: int):
    accounts = db_query("SELECT name, access_key, secret_key, project_id FROM accounts WHERE user_id=?", (user_id,), fetch=True)
    return [{"name": a[0], "access_key": a[1], "secret_key": a[2], "project_id": a[3]} for a in accounts]

@router.post("/")
def add_account(acc: AccountData):
    db_query("INSERT OR REPLACE INTO accounts VALUES (?,?,?,?,?)", 
             (acc.user_id, acc.name, acc.access_key, acc.secret_key, acc.project_id))
    return {"status": "success"}

@router.delete("/{user_id}/{name}")
def delete_account(user_id: int, name: str):
    db_query("DELETE FROM accounts WHERE user_id=? AND name=?", (user_id, name))
    return {"status": "success"}