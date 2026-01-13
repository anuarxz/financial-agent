"""API request/response schemas."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message to the agent")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent response")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    database: str = Field(..., description="Database connection status")
