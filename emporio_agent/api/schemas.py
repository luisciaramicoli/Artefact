from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message text")
    conversation_id: Optional[str] = Field(None, description="Existing session UUID, or null for new")


class ToolCallInfo(BaseModel):
    tool: str
    arguments: Dict[str, Any]


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    tool_calls: List[ToolCallInfo] = []
    created_at: str


class ConversationSummary(BaseModel):
    id: str
    title: str
    message_count: int
    created_at: str
    updated_at: str


class MessageItem(BaseModel):
    id: int
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    created_at: str


class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: List[MessageItem]


class HealthResponse(BaseModel):
    status: str
    version: str
    model: str
    database: str
    qdrant: str
    total_indexed_policies: int
    total_products: int
