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
    """Lightweight health check for k8s probes"""
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    """Readiness check"""
    return {"status": "ok", "service": "ai-service"}


@app.get("/")
def root():
    return {"status": "ok"}
