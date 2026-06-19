"""Workflow execution API endpoints."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import logging

from app.database import get_db
from app.models import ResearchSession, WorkflowStep, ResearchReport
from app.schemas import (
    StartWorkflowRequest,
    WorkflowProgressResponse,
    WorkflowStateResponse,
    SessionStatus,
)
from app.workflows.graph import workflow_manager, ResearchWorkflow
from app.workflows.states import ResearchState, WorkflowConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.post("/start", response_model=Dict[str, str])
async def start_workflow(
    request: StartWorkflowRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Start a research workflow for a session.
    
    Args:
        request: Workflow start request with session ID
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Confirmation with workflow ID
        
    Raises:
        HTTPException: If session not found or already running
    """
    try:
        # Get session
        session = db.query(ResearchSession).filter(
            ResearchSession.id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.status in ["running", "completed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Session is already {session.status}"
            )
        
        # Create workflow
        workflow = workflow_manager.create_workflow(request.session_id)
        
        # Update session status
        session.status = "running"
        session.updated_at = datetime.utcnow()
        db.commit()
        
        # Create initial state
        initial_state = ResearchState(
            session_id=request.session_id,
            company_name=session.company_name,
            company_website=session.company_website,
            research_objective=session.research_objective,
            processing_status="started",
            retry_count=0,
            max_retries=3,
        )
        
        # Execute workflow in background
        background_tasks.add_task(
            execute_workflow_task,
            session.id,
            initial_state,
            workflow
        )
        
        logger.info(f"Started workflow for session {request.session_id}")
        
        return {"status": "started", "session_id": request.session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start workflow")


async def execute_workflow_task(
    session_id: str,
    initial_state: ResearchState,
    workflow: ResearchWorkflow
) -> None:
    """
    Execute the workflow in the background.
    
    Args:
        session_id: ID of the session
        initial_state: Initial workflow state
        workflow: Workflow instance
    """
    from app.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Execute workflow
        final_state = await workflow.execute(initial_state)
        
        # Save results to database
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if session:
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            session.updated_at = datetime.utcnow()
            session.workflow_state = dict(final_state)
            
            # Create report
            if final_state.get("final_report"):
                report = ResearchReport(
                    session_id=session_id,
                    company_overview=final_state.get("analyzed_overview"),
                    products_services=final_state.get("analyzed_products"),
                    target_customers=final_state.get("analyzed_customers"),
                    business_signals=final_state.get("analyzed_signals"),
                    risks_challenges=final_state.get("analyzed_risks"),
                    discovery_questions=final_state.get("discovery_questions"),
                    outreach_strategy=final_state.get("outreach_strategy"),
                    unknowns=final_state.get("unknowns"),
                    sources=final_state.get("sources_used"),
                    quality_score=final_state.get("quality_score"),
                    full_report=final_state.get("final_report"),
                )
                db.add(report)
            
            db.commit()
            logger.info(f"Workflow completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"Workflow execution failed for {session_id}: {str(e)}")
        
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if session:
            session.status = "failed"
            session.error_message = str(e)
            session.updated_at = datetime.utcnow()
            db.commit()
    
    finally:
        workflow_manager.cleanup(session_id)
        db.close()


@router.get("/{session_id}/progress", response_model=WorkflowProgressResponse)
async def get_workflow_progress(
    session_id: str,
    db: Session = Depends(get_db)
) -> WorkflowProgressResponse:
    """
    Get current workflow progress.
    
    Args:
        session_id: ID of the session
        db: Database session
        
    Returns:
        Current workflow progress
        
    Raises:
        HTTPException: If session not found
    """
    try:
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get workflow steps
        steps = db.query(WorkflowStep).filter(
            WorkflowStep.session_id == session_id
        ).all()
        
        completed_steps = sum(1 for s in steps if s.status == "completed")
        total_steps = 5  # Fixed: planner, researcher, analyzer, quality_check, reporter
        
        progress_percentage = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
        
        # Determine current step
        current_step = "pending"
        if session.status == "running":
            for step in steps:
                if step.status == "running":
                    current_step = step.step_name
                    break
        
        return WorkflowProgressResponse(
            session_id=session_id,
            current_step=current_step,
            steps_completed=completed_steps,
            total_steps=total_steps,
            progress_percentage=progress_percentage,
            status=SessionStatus(session.status),
            message=session.error_message or f"Processing: {current_step}",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting progress for {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get progress")


@router.get("/{session_id}/state", response_model=WorkflowStateResponse)
async def get_workflow_state(
    session_id: str,
    db: Session = Depends(get_db)
) -> WorkflowStateResponse:
    """
    Get the current workflow state.
    
    Args:
        session_id: ID of the session
        db: Database session
        
    Returns:
        Current workflow state data
        
    Raises:
        HTTPException: If session not found
    """
    try:
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state_data = session.workflow_state or {}
        
        return WorkflowStateResponse(
            session_id=session_id,
            current_step=state_data.get("processing_status", "pending"),
            state_data=state_data,
            last_update=session.updated_at,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting state for {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get workflow state")


@router.post("/{session_id}/retry")
async def retry_workflow(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Retry a failed workflow.
    
    Args:
        session_id: ID of the session
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Confirmation of retry
        
    Raises:
        HTTPException: If session not found or not failed
    """
    try:
        session = db.query(ResearchSession).filter(
            ResearchSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.status != "failed":
            raise HTTPException(
                status_code=400,
                detail="Can only retry failed workflows"
            )
        
        # Reset session status
        session.status = "running"
        session.error_message = None
        session.updated_at = datetime.utcnow()
        db.commit()
        
        # Recreate workflow with previous state
        workflow = workflow_manager.create_workflow(session_id)
        
        initial_state = ResearchState(
            session_id=session_id,
            company_name=session.company_name,
            company_website=session.company_website,
            research_objective=session.research_objective,
            processing_status="retrying",
            retry_count=0,
        )
        
        background_tasks.add_task(
            execute_workflow_task,
            session_id,
            initial_state,
            workflow
        )
        
        logger.info(f"Retrying workflow for session {session_id}")
        
        return {"status": "retrying", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retry workflow")
