"""Pydantic models for request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class SessionStatus(str, Enum):
    """Session status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStepStatus(str, Enum):
    """Workflow step status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# Session Schemas
class CreateSessionRequest(BaseModel):
    """Request to create a new research session."""
    company_name: str = Field(..., min_length=1, max_length=255, description="Name of the company")
    company_website: Optional[str] = Field(None, max_length=512, description="Company website URL")
    research_objective: str = Field(..., min_length=10, description="Research objective/goal")

    @validator("company_website")
    def validate_url(cls, v):
        """Validate URL format if provided."""
        if v and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Website must start with http:// or https://")
        return v


class SessionResponse(BaseModel):
    """Response containing session information."""
    id: str
    company_name: str
    company_website: Optional[str]
    research_objective: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    """Detailed session response with workflow and report."""
    workflow_steps: List["WorkflowStepResponse"] = []
    report: Optional["ReportResponse"] = None


class SessionListResponse(BaseModel):
    """List of sessions."""
    sessions: List[SessionResponse]
    total: int
    page: int
    page_size: int


# Workflow Step Schemas
class WorkflowStepResponse(BaseModel):
    """Response containing workflow step information."""
    id: str
    step_name: str
    status: WorkflowStepStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    error_message: Optional[str]
    retry_count: int

    class Config:
        from_attributes = True


class WorkflowProgressResponse(BaseModel):
    """Real-time workflow progress."""
    session_id: str
    current_step: str
    steps_completed: int
    total_steps: int
    progress_percentage: int
    status: SessionStatus
    message: str


# Report Schemas
class DiscoveryQuestion(BaseModel):
    """Discovery question for the sales team."""
    question: str
    category: str
    priority: str  # high, medium, low


class ReportResponse(BaseModel):
    """Response containing generated report."""
    id: str
    session_id: str
    company_overview: Optional[str]
    products_services: Optional[str]
    target_customers: Optional[str]
    business_signals: Optional[str]
    risks_challenges: Optional[str]
    discovery_questions: Optional[List[DiscoveryQuestion]]
    outreach_strategy: Optional[str]
    unknowns: Optional[List[str]]
    sources: Optional[List[str]]
    quality_score: Optional[int]
    generated_at: datetime

    class Config:
        from_attributes = True


# Chat Schemas
class ChatMessageRequest(BaseModel):
    """Request to send a chat message."""
    content: str = Field(..., min_length=1, max_length=5000)


class ChatMessageResponse(BaseModel):
    """Response containing chat message."""
    id: str
    session_id: str
    role: str
    content: str
    message_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Chat conversation history."""
    messages: List[ChatMessageResponse]
    total: int


# Workflow Execution Schemas
class StartWorkflowRequest(BaseModel):
    """Request to start workflow execution."""
    session_id: str
    resume_from_step: Optional[str] = None


class WorkflowStateResponse(BaseModel):
    """Current workflow state."""
    session_id: str
    current_step: str
    state_data: Dict[str, Any]
    last_update: datetime


# Error Response
class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health Check
class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    database: str
    llm_configured: bool


# Add to ReportResponse class:

class ReportResponse(BaseModel):
    """Response containing generated report."""
    id: str
    session_id: str
    company_overview: Optional[str]
    products_services: Optional[str]
    target_customers: Optional[str]
    business_signals: Optional[str]
    risks_challenges: Optional[str]
    discovery_questions: Optional[List[DiscoveryQuestion]]
    outreach_strategy: Optional[str]
    unknowns: Optional[List[str]]
    sources: Optional[List[str]]
    quality_score: Optional[int]
    confidence_score: Optional[float]
    prompt_tokens: int = 0
    completion_tokens: int = 0
    generated_at: datetime

    class Config:
        from_attributes = True

# Update forward references
SessionDetailResponse.model_rebuild()
