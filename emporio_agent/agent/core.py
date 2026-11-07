import json
import logging
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types
from google.genai.errors import ClientError
from sqlalchemy.orm import Session

from emporio_agent.config import settings
from emporio_agent.db.database import SessionLocal
from emporio_agent.db.models import ConversationSession, ConversationMessage
from emporio_agent.agent.persona import EMPORIO_SYSTEM_PROMPT
from emporio_agent.agent.tools import (
    get_categories,
    search_store_policies,
    query_products,
    get_product_details,
    check_order_status,
    get_store_info,
)

logger = logging.getLogger(__name__)


class EmporioAgent:
    """
    Intelligent conversational agent for Empório da Música.
    Orchestrates Gemini 2.5 Flash with Tool Calling, Qdrant Vector RAG, and SQLite persistence.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.fallback_model = "gemini-2.5-flash-lite"

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided via environment or settings.")

        self.client = genai.Client(
            api_key=self.api_key,
            http_options={"api_version": "v1beta"}
        )

        self.tools = [
            get_categories,
            search_store_policies,
            query_products,
            get_product_details,
            check_order_status,
            get_store_info,
        ]

    def _get_or_create_session(self, db: Session, conversation_id: Optional[str] = None) -> ConversationSession:
        """Fetch existing conversation session or initialize a new one."""
        if conversation_id:
            session = db.query(ConversationSession).filter(ConversationSession.id == conversation_id).first()
            if session:
                return session

        # Create new conversation
        new_id = conversation_id or str(uuid.uuid4())
        session = ConversationSession(id=new_id, title="Nova Conversa")
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def _build_history_contents(self, db: Session, conversation_id: str) -> List[types.Content]:
        """Reconstruct previous conversation turns into Gemini Content objects."""
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(ConversationMessage.created_at.asc()).all()

        contents = []
        for msg in messages:
            role = "user" if msg.role == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg.content)]
                )
            )
        return contents

    def _execute_turn_with_retry(
        self,
        chat: Any,
        message: str,
        retries: int = 3,
    ) -> Any:
        """Execute chat turn with exponential backoff for 429 (quota) and 503 (high demand) transient errors."""
        for attempt in range(retries + 1):
            try:
                return chat.send_message(message)
            except (ClientError, Exception) as e:
                err_str = str(e)
                is_transient = (
                    "RESOURCE_EXHAUSTED" in err_str or
                    "429" in err_str or
                    "503" in err_str or
                    "UNAVAILABLE" in err_str or
                    "high demand" in err_str
                )
                if is_transient and attempt < retries:
                    backoff = 3 * (attempt + 1)
                    logger.warning(f"Transient error on attempt {attempt + 1}: {err_str[:120]}... Backing off {backoff}s")
                    time.sleep(backoff)
                    continue
                raise

    def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message, run tool calling if needed, persist history and return reply.
        """
        db: Session = SessionLocal()
        try:
            session = self._get_or_create_session(db, conversation_id)
            conv_id = session.id

            # Save user message to DB
            user_msg = ConversationMessage(
                conversation_id=conv_id,
                role="user",
                content=message.strip(),
            )
            db.add(user_msg)
            db.commit()

            # Load history
            history = self._build_history_contents(db, conv_id)
            # Remove the last message from history since we are sending it via chat.send_message
            if history:
                history = history[:-1]

            # Create Gemini chat
            chat_session = self.client.chats.create(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=EMPORIO_SYSTEM_PROMPT,
                    tools=self.tools,
                    temperature=0.3,
                ),
                history=history
            )

            # Send message and get response
            response = self._execute_turn_with_retry(chat_session, message)

            # Extract tool calls from session history
            executed_tools = []
            for item in chat_session.get_history():
                if getattr(item, "parts", None):
                    for p in item.parts:
                        fc = getattr(p, "function_call", None)
                        if fc:
                            executed_tools.append({
                                "tool": getattr(fc, "name", ""),
                                "arguments": getattr(fc, "args", {}),
                            })

            reply_text = getattr(response, "text", "") or ""
            if not reply_text:
                # In case response text is in candidates
                candidates = getattr(response, "candidates", None)
                if candidates and len(candidates) > 0:
                    cand_content = getattr(candidates[0], "content", None)
                    cand_parts = getattr(cand_content, "parts", None)
                    if cand_parts:
                        for part in cand_parts:
                            pt_text = getattr(part, "text", None)
                            if pt_text:
                                reply_text += pt_text

            if not reply_text:
                reply_text = "Olá! Como posso ajudar você hoje com os instrumentos musicais da Empório da Música?"

            # Update conversation title if first message
            if session.title == "Nova Conversa" and message:
                truncated_title = message[:40] + ("..." if len(message) > 40 else "")
                session.title = truncated_title
                session.updated_at = datetime.utcnow()

            # Save assistant message to DB
            assistant_msg = ConversationMessage(
                conversation_id=conv_id,
                role="assistant",
                content=reply_text,
                tool_calls=json.dumps(executed_tools, ensure_ascii=False) if executed_tools else None,
            )
            db.add(assistant_msg)
            db.commit()

            return {
                "conversation_id": conv_id,
                "message": reply_text,
                "tool_calls": executed_tools,
                "created_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing chat message: {e}", exc_info=True)
            db.rollback()
            raise
        finally:
            db.close()


# Singleton
_agent = None


def get_agent() -> EmporioAgent:
    global _agent
    if _agent is None:
        _agent = EmporioAgent()
    return _agent
