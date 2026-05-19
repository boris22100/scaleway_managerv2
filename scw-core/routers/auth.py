from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import hashlib
from database import db_query

router = APIRouter(prefix="/auth", tags=["Authentification & Admin"])

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    res = db_query("SELECT id, password, role, approved FROM users WHERE username=?", (req.username,), fetch=True)
    if res and check_hashes(req.password, res[0][1]):
        if res[0][3] == 1 or res[0][2] == 'admin':
            return {"id": res[0][0], "username": req.username, "role": res[0][2]}
        raise HTTPException(status_code=403, detail="Compte en attente d'approbation.")
    raise HTTPException(status_code=401, detail="Identifiants incorrects.")

@router.post("/register")
def register(req: LoginRequest):
    count = db_query("SELECT COUNT(*) FROM users", fetch=True)[0][0]
    role, appr = ('admin', 1) if count == 0 else ('user', 0)
    try:
        db_query("INSERT INTO users (username, password, role, approved) VALUES (?,?,?,?)", 
                 (req.username, make_hashes(req.password), role, appr))
        return {"status": "success", "message": "Demande enregistrée"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris ou erreur DB.")

# --- Gouvernance Admin ---
@router.get("/users")
def get_users():
    users = db_query("SELECT id, username, role, approved FROM users", fetch=True)
    return [{"id": u[0], "username": u[1], "role": u[2], "approved": bool(u[3])} for u in users]

@router.post("/users/{user_id}/approve")
def approve_user(user_id: int):
    db_query("UPDATE users SET approved=1 WHERE id=?", (user_id,))
    return {"status": "success"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    db_query("DELETE FROM users WHERE id=?", (user_id,))
    return {"status": "success"}