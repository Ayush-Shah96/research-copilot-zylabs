"""Chat API endpoints for follow-up conversations."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging

from app.database import get_db
from app.models import ResearchSession, ChatMessage, ResearchReport
from app.schemas import ChatMessageRequest, ChatMessageResponse, ChatHistoryResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sessions/{session_id}/chat", tags=["chat"])


@router.post("", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: str,
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
) -> ChatMessageResponse:
    """
    Send a chat message to the research copilot.
    
    Args:
        session_id: ID of the session
        request: Chat message request
        db: Database session
        
    Returns:
        Chat message response from assistant
        
    Raises:
        HTTPException: If session not found or not completed
    """
    try:
        # Verify session exists and is completed
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.status != "completed":
            raise HTTPException(
                status_code=400,
                detail="Session must be completed before chatting"
            )
        
        # Get the report for context
        report = db.query(ResearchReport).filter(
            ResearchReport.session_id == session_id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Save user message
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="user",
            content=request.content,
            message_type="text",
            created_at=datetime.utcnow(),
        )
        
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Generate assistant response based on report context
        response_content = generate_chat_response(request.content, report)
        
        # Save assistant message
        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="assistant",
            content=response_content,
            message_type="text",
            created_at=datetime.utcnow(),
        )
        
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        logger.info(f"Chat message sent for session {session_id}")
        
        return ChatMessageResponse.from_orm(assistant_message)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending chat message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.get("", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> ChatHistoryResponse:
    """
    Get chat history for a session.
    
    Args:
        session_id: ID of the session
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        db: Database session
        
    Returns:
        Chat message history
        
    Raises:
        HTTPException: If session not found
    """
    try:
        # Verify session exists
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get messages
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.asc()).offset(offset).limit(limit).all()
        
        total = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).count()
        
        return ChatHistoryResponse(
            messages=[ChatMessageResponse.from_orm(m) for m in messages],
            total=total,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")


@router.delete("/{message_id}", status_code=204)
async def delete_chat_message(
    session_id: str,
    message_id: str,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a chat message.
    
    Args:
        session_id: ID of the session
        message_id: ID of the message to delete
        db: Database session
        
    Raises:
        HTTPException: If message not found
    """
    try:
        message = db.query(ChatMessage).filter(
            ChatMessage.id == message_id,
            ChatMessage.session_id == session_id
        ).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        db.delete(message)
        db.commit()
        
        logger.info(f"Deleted message {message_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete message")


@router.post("/clear", status_code=204)
async def clear_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
) -> None:
    """
    Clear all chat messages for a session.
    
    Args:
        session_id: ID of the session
        db: Database session
        
    Raises:
        HTTPException: If session not found
    """
    try:
        # Verify session exists
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete all messages
        db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).delete()
        
        db.commit()
        
        logger.info(f"Cleared chat history for session {session_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to clear chat history")


def generate_chat_response(user_message: str, report: ResearchReport) -> str:
    """
    Generate an intelligent response based on the research report.
    
    In production, this would use an LLM with report context.
    
    Args:
        user_message: User's question
        report: Research report for context
        
    Returns:
        Response from the copilot
    """
    message_lower = user_message.lower()
    
    # Simple pattern matching for demo purposes
    if any(word in message_lower for word in ["product", "service"]):
        return (
            f"Based on our research, {report.session_id[:8]}'s main offerings include: "
            f"{report.products_services or 'Information pending'}. "
            f"Would you like to know more about their specific use cases?"
        )
    
    elif any(word in message_lower for word in ["customer", "target", "market"]):
        return (
            f"Our research indicates that the target customers are: "
            f"{report.target_customers or 'Information pending'}. "
            f"This is valuable information for crafting your outreach strategy."
        )
    
    elif any(word in message_lower for word in ["risk", "challenge", "concern"]):
        return (
            f"Key risks and challenges we identified: "
            f"{report.risks_challenges or 'No major risks identified'}. "
            f"Consider these in your sales approach."
        )
    
    elif any(word in message_lower for word in ["signal", "growth", "momentum"]):
        return (
            f"Positive business signals include: "
            f"{report.business_signals or 'Steady market presence'}. "
            f"This suggests good timing for outreach."
        )
    
    elif any(word in message_lower for word in ["question", "discover"]):
        if report.discovery_questions:
            questions = ", ".join([q.get("question", "") for q in report.discovery_questions[:3]])
            return f"Great discovery questions to ask: {questions}"
        return "Prepare questions that uncover their specific needs and challenges."
    
    elif any(word in message_lower for word in ["outreach", "approach", "strategy"]):
        return (
            f"Recommended approach: {report.outreach_strategy or 'Start with a personalized introduction highlighting relevant insights'}. "
            f"Focus on value and relevance to their business."
        )
    
    elif any(word in message_lower for word in ["unknown", "missing", "gap"]):
        if report.unknowns:
            unknowns = ", ".join(report.unknowns[:3])
            return f"Information gaps we identified: {unknowns}. You may want to explore these during initial conversations."
        return "We have comprehensive coverage of available public information."
    
    else:
        # Generic response
        return (
            f"Based on our comprehensive research of the company, I can help you prepare for your meeting. "
            f"Feel free to ask about their products, market position, customers, risks, or recommended outreach strategy. "
            f"What would you like to know more about?"
        )
