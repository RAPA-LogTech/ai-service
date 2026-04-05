"""Minimal ai-service demo for verifying runtime environment variables."""

from __future__ import annotations

import os
from importlib import import_module
from typing import Any

FastAPI = import_module("fastapi").FastAPI

app = FastAPI(title="ai-service demo")

DEMO_ENV_VARS = [
    "AWS_REGION_NAME",
    "BEDROCK_MODEL_ID",
    "AGENTCORE_MEMORY_ID",
    "CHATBOT_CONVERSATIONS_TABLE",
    "CHATBOT_MESSAGES_TABLE",
]


def _env_value(key: str) -> str:
    value = os.getenv(key)
    if not value:
        return ""
    return value


@app.get("/")
def root() -> dict[str, str]:
    """Return a small status payload for a quick smoke test."""

    return {
        "service": "ai-service-demo",
        "message": "ai-service demo is running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Return a basic health check response."""

    return {"status": "ok"}


@app.get("/debug/env")
def debug_env() -> dict[str, Any]:
    """Expose the key environment variables used by the demo."""

    return {
        "port": 8083,
        "env": {key: _env_value(key) for key in DEMO_ENV_VARS},
    }
