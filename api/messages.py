from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from chat import database as db, agent

router = APIRouter()


class MessageRequest(BaseModel):
    message: str


@router.post("/v1/conversations/{cid}/messages")
def send_message(cid: str, body: MessageRequest):
    conv = db.get_conversation(cid)
    if not conv:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")

    history = db.get_context_messages(cid)
    db.add_message(cid, "user", body.message)

    try:
        response = agent.chat(cid, history, body.message)
    except Exception as e:
        response = f"오류가 발생했습니다: {str(e)}"

    msg = db.add_message(cid, "assistant", response)
    return {"message": msg}
