from fastapi import FastAPI
from app.core.logging_config import setup_logging

setup_logging()

app = FastAPI(title="Notification Service")


@app.get("/api/notification/health")
def health():
    return {"status": "ok"}