from time import time
from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel

from src.generator import answer_question
from src.logger import log_query, read_logs


app = FastAPI(
    title="Enterprise RAG Support Automation API",
    description="RAG-based IT support assistant with ticket classification and routing",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str


@app.get("/")
def root() -> Dict:
    return {
        "message": "Enterprise RAG Support Automation API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check() -> Dict:
    return {
        "status": "healthy",
        "service": "enterprise-rag-support-platform",
    }


@app.post("/ask")
def ask_question(request: AskRequest) -> Dict:
    start_time = time()

    response = answer_question(request.question)

    latency_ms = round((time() - start_time) * 1000, 2)

    api_response = {
        "question": response["question"],
        "answer": response["answer"],
        "sources": response["sources"],
        "ticket": response["ticket"],
        "fallback_triggered": response["fallback_triggered"],
        "latency_ms": latency_ms,
    }

    log_query(api_response)

    return api_response


@app.get("/logs")
def get_logs() -> Dict:
    logs = read_logs()

    return {
        "total_logs": len(logs),
        "logs": logs[-20:],
    }