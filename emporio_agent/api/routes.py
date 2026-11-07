import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from emporio_agent.config import settings
from emporio_agent.db.database import get_db
from emporio_agent.db.models import ConversationSession, ConversationMessage, Product
from emporio_agent.rag.vector_store import get_vector_store
from emporio_agent.agent.core import get_agent
from emporio_agent.agent.tools import query_products
from emporio_agent.api.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    ConversationDetail,
    MessageItem,
    HealthResponse,
)

router = APIRouter(prefix="/api")


@router.post("/chat", response_model=ChatResponse)
def handle_chat(payload: ChatRequest):
    """Send a user message to the agent and receive the response with tool call traces."""
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        agent = get_agent()
        res = agent.chat(payload.message, conversation_id=payload.conversation_id)
        return ChatResponse(
            conversation_id=res["conversation_id"],
            message=res["message"],
            tool_calls=res.get("tool_calls", []),
            created_at=res["created_at"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=List[ConversationSummary])
def list_conversations(db: Session = Depends(get_db)):
    """List all persisted conversation sessions."""
    sessions = db.query(ConversationSession).order_by(ConversationSession.updated_at.desc()).all()
    result = []
    for s in sessions:
        count = db.query(ConversationMessage).filter(ConversationMessage.conversation_id == s.id).count()
        result.append(
            ConversationSummary(
                id=s.id,
                title=s.title or "Nova Conversa",
                message_count=count,
                created_at=s.created_at.isoformat() if s.created_at else "",
                updated_at=s.updated_at.isoformat() if s.updated_at else "",
            )
        )
    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation_history(conversation_id: str, db: Session = Depends(get_db)):
    """Fetch complete message history of a given session."""
    session = db.query(ConversationSession).filter(ConversationSession.id == conversation_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Conversation session not found.")

    msgs = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.created_at.asc()).all()

    formatted_msgs = []
    for m in msgs:
        parsed_tools = None
        if m.tool_calls:
            try:
                parsed_tools = json.loads(m.tool_calls)
            except Exception:
                pass

        formatted_msgs.append(
            MessageItem(
                id=m.id,
                role=m.role,
                content=m.content,
                tool_calls=parsed_tools,
                created_at=m.created_at.isoformat() if m.created_at else "",
            )
        )

    return ConversationDetail(
        id=session.id,
        title=session.title or "Nova Conversa",
        messages=formatted_msgs,
    )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a conversation session and all its messages."""
    session = db.query(ConversationSession).filter(ConversationSession.id == conversation_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Conversation session not found.")

    db.delete(session)
    db.commit()
    return {"status": "success", "message": f"Conversation {conversation_id} deleted."}


@router.get("/products")
def list_products(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
):
    """Direct product catalog endpoint."""
    return query_products(category_name=category, max_price=max_price, search_text=search, limit=20)


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """System health check, Qdrant index count, and product count."""
    vs = get_vector_store()
    policy_count = vs.count()
    product_count = db.query(Product).count()

    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        model=settings.GEMINI_MODEL,
        database="connected",
        qdrant="connected",
        total_indexed_policies=policy_count,
        total_products=product_count,
    )
