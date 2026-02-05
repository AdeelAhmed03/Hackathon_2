"""Chat API routes for AI-powered task management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from ..database.session import get_session
from ..models.user import User
from ..models.conversation import Conversation, ConversationRead
from ..models.message import Message, MessageRole, MessageRead
from ..middleware.auth import get_current_user
from ..services.chat_service import (
    format_history_for_cohere,
    truncate_history,
    call_cohere_chat,
)
from ..services.tool_service import run_tool_loop
from ..tools.definitions import ALL_TOOLS

router = APIRouter()


# Request/Response schemas
class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[int] = None


class ChatMessageResponse(BaseModel):
    """Response schema for a chat message."""
    role: str
    content: str


class ToolResultResponse(BaseModel):
    """Response schema for tool execution result."""
    tool_name: str
    success: bool
    result: str


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: int
    message: ChatMessageResponse
    tool_executed: bool = False
    tool_results: Optional[List[ToolResultResponse]] = None


class ConversationListResponse(BaseModel):
    """Response schema for listing conversations."""
    conversations: List[ConversationRead]
    total: int


# Helper functions
def get_or_create_conversation(
    session: Session,
    user_id: int,
    conversation_id: Optional[int] = None
) -> Conversation:
    """
    Get existing conversation or create a new one.

    Args:
        session: Database session
        user_id: Authenticated user ID
        conversation_id: Optional existing conversation ID

    Returns:
        Conversation object
    """
    if conversation_id:
        # Get existing conversation (must belong to user)
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return conversation

    # Create new conversation
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def get_conversation_messages(
    session: Session,
    conversation_id: int,
    limit: int = 50
) -> List[Message]:
    """
    Get messages for a conversation in chronological order.

    Args:
        session: Database session
        conversation_id: Conversation ID
        limit: Maximum messages to retrieve

    Returns:
        List of Message objects
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = session.exec(statement).all()
    return list(reversed(messages))  # Return in chronological order


def save_message(
    session: Session,
    conversation_id: int,
    role: MessageRole,
    content: Optional[str] = None,
    tool_calls: Optional[dict] = None,
    tool_results: Optional[dict] = None
) -> Message:
    """
    Save a message to the database.

    Args:
        session: Database session
        conversation_id: Conversation ID
        role: Message role (user/assistant/tool)
        content: Message text content
        tool_calls: Tool calls data (if any)
        tool_results: Tool results data (if any)

    Returns:
        Created Message object
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_results=tool_results
    )
    session.add(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(message)
    return message


# API Routes
@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Send a message to the AI chatbot and receive a response.

    The chatbot can execute task management tools based on the message.
    Requires JWT authentication.
    """
    # Validate message is not empty
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    try:
        # Get or create conversation
        conversation = get_or_create_conversation(
            session=session,
            user_id=current_user.id,
            conversation_id=request.conversation_id
        )

        # Load conversation history
        messages = get_conversation_messages(
            session=session,
            conversation_id=conversation.id
        )

        # Truncate history if needed
        messages = truncate_history(messages)

        # Format history for Cohere
        chat_history = format_history_for_cohere(messages)

        # Save user message
        save_message(
            session=session,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message
        )

        # Run tool loop (handles Cohere calls and tool execution)
        result = await run_tool_loop(
            initial_message=request.message,
            chat_history=chat_history,
            tools=ALL_TOOLS,
            user_id=current_user.id,
            session=session,
            call_cohere_func=call_cohere_chat
        )

        # Save assistant response
        save_message(
            session=session,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=result["text"],
            tool_calls=result["tool_calls"],
            tool_results=result["tool_results"]
        )

        # Format tool results for response
        tool_results_response = None
        if result["tool_results"]:
            tool_results_response = [
                ToolResultResponse(
                    tool_name=tc["name"] if isinstance(tc, dict) else "unknown",
                    success=tr["success"],
                    result=str(tr["result"])
                )
                for tc, tr in zip(result["tool_calls"] or [], result["tool_results"])
            ]

        return ChatResponse(
            conversation_id=conversation.id,
            message=ChatMessageResponse(
                role="assistant",
                content=result["text"]
            ),
            tool_executed=bool(result["tool_calls"]),
            tool_results=tool_results_response
        )

    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is temporarily unavailable. Please try again later."
        )
    except RuntimeError as e:
        if "Rate limit" in str(e):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request."
        )


@router.get("/chat/conversations", response_model=ConversationListResponse)
def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all conversations for the authenticated user."""
    # Get conversations
    statement = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    conversations = session.exec(statement).all()

    # Get total count
    count_statement = select(Conversation).where(Conversation.user_id == current_user.id)
    total = len(session.exec(count_statement).all())

    return ConversationListResponse(
        conversations=[ConversationRead(
            id=c.id,
            user_id=c.user_id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at
        ) for c in conversations],
        total=total
    )


@router.get("/chat/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    message_limit: int = 50,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific conversation with its messages."""
    # Get conversation (must belong to user)
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    conversation = session.exec(statement).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get messages
    messages = get_conversation_messages(
        session=session,
        conversation_id=conversation_id,
        limit=message_limit
    )

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": [
            MessageRead(
                id=m.id,
                conversation_id=m.conversation_id,
                role=m.role,
                content=m.content,
                tool_calls=m.tool_calls,
                tool_results=m.tool_results,
                created_at=m.created_at
            )
            for m in messages
        ]
    }


@router.delete("/chat/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a conversation and all its messages."""
    # Get conversation (must belong to user)
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    conversation = session.exec(statement).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Delete all messages first
    messages_statement = select(Message).where(Message.conversation_id == conversation_id)
    messages = session.exec(messages_statement).all()
    for message in messages:
        session.delete(message)

    # Delete conversation
    session.delete(conversation)
    session.commit()

    return {"message": "Conversation deleted successfully"}
