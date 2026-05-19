from fastapi import APIRouter
from pydantic import BaseModel
from database import db_query

router = APIRouter(prefix="/templates", tags=["Templates"])

class TemplateData(BaseModel):
    user_id: int
    name: str
    content: str

@router.get("/{user_id}")
def get_templates(user_id: int):
    templates = db_query("SELECT name, content FROM templates WHERE user_id=?", (user_id,), fetch=True)
    return [{"name": t[0], "content": t[1]} for t in templates]

@router.post("/")
def add_template(tmpl: TemplateData):
    db_query("INSERT OR REPLACE INTO templates VALUES (?,?,?)", (tmpl.user_id, tmpl.name, tmpl.content))
    return {"status": "success"}

@router.delete("/{user_id}/{name}")
def delete_template(user_id: int, name: str):
    db_query("DELETE FROM templates WHERE user_id=? AND name=?", (user_id, name))
    return {"status": "success"}