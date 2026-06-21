"""SQLAlchemy database models."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class ResearchSession(Base):
    """Research session model."""

    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String(255), nullable=False, index=True)
    company_website = Column(String(512), nullable=True)
    research_objective = Column(Text, nullable=False)
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True
    )  # pending, running, completed, failed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Workflow state
    workflow_state = Column(JSON, nullable=True)
    workflow_outputs = Column(JSON, nullable=True)
    
    # Relationships
    workflow_steps = relationship("WorkflowStep", back_populates="session", cascade="all, delete-orphan")
    report = relationship("ResearchReport", back_populates="session", uselist=False, cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ResearchSession(id={self.id}, company={self.company_name}, status={self.status})>"


class WorkflowStep(Base):
    """Workflow execution step."""

    __tablename__ = "workflow_steps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("research_sessions.id"), nullable=False, index=True)
    step_name = Column(String(255), nullable=False)
    status = Column(
        String(50),
        nullable=False,
        default="pending"
    )  # pending, running, completed, failed, skipped
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    session = relationship("ResearchSession", back_populates="workflow_steps")

    def __repr__(self) -> str:
        return f"<WorkflowStep(step={self.step_name}, status={self.status})>"


class ResearchReport(Base):
    """Generated research report."""

    __tablename__ = "research_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("research_sessions.id"), nullable=False, unique=True, index=True)
    
    # Report content
    company_overview = Column(Text, nullable=True)
    products_services = Column(Text, nullable=True)
    target_customers = Column(Text, nullable=True)
    business_signals = Column(Text, nullable=True)
    risks_challenges = Column(Text, nullable=True)
    discovery_questions = Column(JSON, nullable=True)  # List of questions
    outreach_strategy = Column(Text, nullable=True)
    unknowns = Column(JSON, nullable=True)  # List of unknowns
    sources = Column(JSON, nullable=True)  # List of sources
    
    # Report metadata
    quality_score = Column(Integer, nullable=True)  # 0-100
    confidence_score = Column(Float, nullable=True)  # 0-1
    research_depth = Column(String(50), nullable=True)  # basic, intermediate, comprehensive
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Token usage
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    
    # Full report
    full_report = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("ResearchSession", back_populates="report")

    def __repr__(self) -> str:
        return f"<ResearchReport(session_id={self.session_id})>"


class ChatMessage(Base):
    """Chat message in follow-up conversation."""

    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("research_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, system, error
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Context
    context_used = Column(JSON, nullable=True)  # References to report sections used
    
    # Relationships
    session = relationship("ResearchSession", back_populates="chat_messages")

    def __repr__(self) -> str:
        return f"<ChatMessage(session={self.session_id}, role={self.role})>"


class AuditLog(Base):
    """Audit log for tracking operations."""

    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True, index=True)
    action = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # success, failure
    details = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<AuditLog(event={self.event_type}, action={self.action})>"