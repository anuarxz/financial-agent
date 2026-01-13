"""API routes."""

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_agent, get_db_connection
from src.api.schemas import ChatRequest, ChatResponse, HealthResponse
from src.agent import FinancialAgent

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    db_status = "healthy"

    try:
        db = get_db_connection()
        with db.get_cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        db_status = "unhealthy"

    return HealthResponse(
        status="healthy",
        database=db_status,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    agent: FinancialAgent = Depends(get_agent),
) -> ChatResponse:
    try:
        response = agent.chat(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/reset")
def reset_conversation(
    agent: FinancialAgent = Depends(get_agent),
) -> dict[str, str]:
    agent.reset_conversation()
    return {"message": "Conversación reiniciada correctamente"}


@router.get("/traces")
def get_traces(
    agent: FinancialAgent = Depends(get_agent),
) -> dict:
    return {
        "count": len(agent.get_traces()),
        "traces": agent.get_traces(),
    }
