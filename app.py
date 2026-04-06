from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from api.conversations import router as conversations_router
from api.messages import router as messages_router

app = FastAPI(title="ai-service")

app.include_router(conversations_router)
app.include_router(messages_router)


@app.get("/health")
def health():
    return {"status": "ok"}
