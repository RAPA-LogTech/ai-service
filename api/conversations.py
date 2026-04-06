from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from chat import database as db

router = APIRouter()


class ConversationCreate(BaseModel):
    message: str = ""


@router.get("/v1/conversations")
def list_conversations():
    return db.list_conversations()


@router.post("/v1/conversations")
def create_conversation(body: ConversationCreate):
    return db.create_conversation(body.message)


@router.get("/v1/conversations/{cid}")
def get_conversation(cid: str):
    conv = db.get_conversation(cid)
    if not conv:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")
    messages = db.get_messages(cid)
    return {"conversation": conv, "messages": messages}


@router.delete("/v1/conversations/{cid}")
def delete_conversation(cid: str):
    from chat import agent
    db.delete_conversation(cid)
    agent.delete_session(cid)
    return {"ok": True}
