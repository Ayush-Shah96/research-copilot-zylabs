"""Session management API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging

from app.database import get_db
from app.models import ResearchSession, ChatMessage
from app.schemas import (
    CreateSessionRequest,
    SessionResponse,
    SessionDetailResponse,
    SessionListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
) -> SessionResponse:
    """
    Create a new research session.
    
    Args:
        request: Session creation request with company details
        db: Database session
        
    Returns:
        Created session details
    """
    try:
        session = ResearchSession(
            id=str(uuid.uuid4()),
            company_name=request.company_name,
            company_website=request.company_website,
            research_objective=request.research_objective,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Created session {session.id} for {session.company_name}")
        
        return SessionResponse.from_orm(session)
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db)
) -> SessionListResponse:
    """
    List all research sessions with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of sessions per page
        status: Filter by session status
        db: Database session
        
    Returns:
        Paginated list of sessions
    """
    try:
        query = db.query(ResearchSession).order_by(ResearchSession.created_at.desc())
        
        if status:
            query = query.filter(ResearchSession.status == status)
        
        total = query.count()
        
        sessions = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return SessionListResponse(
            sessions=[SessionResponse.from_orm(s) for s in sessions],
            total=total,
            page=page,
            page_size=page_size,
        )
        
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    db: Session = Depends(get_db)
) -> SessionDetailResponse:
    """
    Get detailed information about a specific session.
    
    Args:
        session_id: ID of the session
        db: Database session
        
    Returns:
        Detailed session information with workflow and report
        
    Raises:
        HTTPException: If session not found
    """
    try:
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionDetailResponse.from_orm(session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a research session.
    
    Args:
        session_id: ID of the session to delete
        db: Database session
        
    Raises:
        HTTPException: If session not found
    """
    try:
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        db.delete(session)
        db.commit()
        
        logger.info(f"Deleted session {session_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
) -> SessionResponse:
    """
    Update a research session.
    
    Args:
        session_id: ID of the session to update
        request: Updated session data
        db: Database session
        
    Returns:
        Updated session details
        
    Raises:
        HTTPException: If session not found
    """
    try:
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update fields
        session.company_name = request.company_name
        session.company_website = request.company_website
        session.research_objective = request.research_objective
        session.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(session)
        
        logger.info(f"Updated session {session_id}")
        
        return SessionResponse.from_orm(session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update session")
