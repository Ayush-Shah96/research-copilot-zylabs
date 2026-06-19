# Architecture Documentation

## System Overview

The AI Research Copilot is a production-grade full-stack application designed to automate company research and generate comprehensive briefings for sales professionals.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                               │
│                   (React 18 SPA)                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Pages: Home, Create, Detail  │  Components: UI Elements   │  │
│  │  Hooks: useApi, useSession, useWorkflow, useChat        │  │
│  │  Services: API Client with Axios                        │  │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                           ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                    SERVER LAYER                                 │
│                 (FastAPI + Python)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  API Routes:                                           │   │
│  │  • /api/sessions - Session management                 │   │
│  │  • /api/workflows - Workflow execution                │   │
│  │  • /api/sessions/{id}/chat - Chat functionality      │   │
│  │  • /health - Health check                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Business Logic:                                       │   │
│  │  • Session Management Service                         │   │
│  │  • Workflow Orchestration (LangGraph)                │   │
│  │  • Research Service                                   │   │
│  │  • LLM Integration Service                            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                           ↓ SQL
┌─────────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                    │
│              (SQLAlchemy + Database)                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Models:                                               │   │
│  │  • ResearchSession - Core session data               │   │
│  │  • WorkflowStep - Workflow execution steps           │   │
│  │  • ResearchReport - Generated reports               │   │
│  │  • ChatMessage - Chat history                        │   │
│  │  • AuditLog - Audit trail                            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Architecture

```
src/
├── components/           # React UI Components
│   ├── Layout.jsx       # Main layout wrapper
│   └── ... other components
├── pages/               # Page components
│   ├── HomePage.jsx     # Session list
│   ├── SessionCreatePage.jsx  # Create new session
│   └── SessionDetailPage.jsx  # Session details & progress
├── hooks/               # Custom React hooks
│   └── index.js        # useApi, useSession, useWorkflow, useChat
├── services/            # API and external service clients
│   └── api.js          # Axios instance with interceptors
├── styles/              # CSS files
│   ├── index.css       # Global styles
│   ├── layout.css      # Layout component styles
│   ├── pages.css       # Page and component styles
│   └── App.css         # App level styles
└── App.jsx             # Main app component
```

### Backend Architecture

```
backend/
├── app/
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database setup (SQLAlchemy)
│   ├── models.py                  # ORM models
│   ├── schemas.py                 # Pydantic validation models
│   ├── middleware.py              # Custom middleware
│   ├── logger.py                  # Logging configuration
│   │
│   ├── api/                       # API Routes
│   │   ├── sessions.py           # Session management endpoints
│   │   ├── workflow.py           # Workflow execution endpoints
│   │   └── chat.py               # Chat endpoints
│   │
│   ├── workflows/                # LangGraph Workflow
│   │   ├── graph.py              # Workflow orchestration
│   │   ├── states.py             # State definitions
│   │   └── nodes.py              # Workflow nodes
│   │
│   ├── services/                 # Business Logic
│   │   ├── research_service.py
│   │   ├── llm_service.py
│   │   └── storage_service.py
│   │
│   └── tests/                    # Unit tests
│
├── scripts/                       # Database utilities
│   ├── init_db.py
│   └── seed_data.py
│
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment template
```

## Data Models

### ResearchSession
- **Purpose**: Stores research project metadata
- **Key Fields**:
  - `id`: Unique session identifier
  - `company_name`: Target company
  - `research_objective`: Research goals
  - `status`: pending | running | completed | failed
  - `workflow_state`: JSON state of current workflow
  - `created_at`, `updated_at`: Timestamps

### WorkflowStep
- **Purpose**: Tracks each step of the research workflow
- **Key Fields**:
  - `step_name`: Name of the workflow step
  - `status`: Current step status
  - `input_data`: Step input (JSON)
  - `output_data`: Step output (JSON)
  - `duration_seconds`: Execution time
  - `retry_count`: Number of retries

### ResearchReport
- **Purpose**: Stores generated research findings
- **Key Fields**:
  - `company_overview`: Executive summary
  - `products_services`: Product analysis
  - `target_customers`: Customer segment info
  - `business_signals`: Market indicators
  - `risks_challenges`: Risk assessment
  - `discovery_questions`: Sales questions
  - `outreach_strategy`: Recommended approach
  - `quality_score`: Report quality metric (0-100)

### ChatMessage
- **Purpose**: Stores follow-up chat conversation
- **Key Fields**:
  - `role`: "user" or "assistant"
  - `content`: Message text
  - `context_used`: JSON references to report sections

## API Design

### Session APIs
```
POST   /api/sessions                    # Create session
GET    /api/sessions                    # List sessions (paginated)
GET    /api/sessions/{id}               # Get session details
PUT    /api/sessions/{id}               # Update session
DELETE /api/sessions/{id}               # Delete session
```

### Workflow APIs
```
POST   /api/workflows/start              # Start workflow
GET    /api/workflows/{id}/progress      # Get progress
GET    /api/workflows/{id}/state         # Get state
POST   /api/workflows/{id}/retry         # Retry failed workflow
```

### Chat APIs
```
POST   /api/sessions/{id}/chat           # Send message
GET    /api/sessions/{id}/chat           # Get chat history
POST   /api/sessions/{id}/chat/clear     # Clear history
DELETE /api/sessions/{id}/chat/{msg_id}  # Delete message
```

## LangGraph Workflow

### Workflow Steps

1. **Planner Node** (60s timeout)
   - Input: Company name, website, objective
   - Output: Research questions, search keywords, data sources
   - Timeout: 60 seconds
   - Critical: Yes

2. **Researcher Node** (300s timeout)
   - Input: Research plan and keywords
   - Output: Raw company data, website content, news, social media
   - Timeout: 300 seconds
   - Retryable: Yes

3. **Analyzer Node** (240s timeout)
   - Input: Raw research data
   - Output: Analyzed overview, products, customers, signals, risks
   - Timeout: 240 seconds
   - Retryable: Yes

4. **Quality Check Node** (120s timeout)
   - Input: Analyzed data
   - Output: Quality score (0-100), pass/fail decision
   - Timeout: 120 seconds
   - Critical: Yes
   - **Conditional Routing**: If quality < threshold and retries available → Retry Researcher
   - Otherwise → Continue to Reporter

5. **Reporter Node** (180s timeout)
   - Input: High-quality analyzed data
   - Output: Discovery questions, outreach strategy, final report
   - Timeout: 180 seconds
   - Critical: Yes

### Workflow State Management

```python
ResearchState(TypedDict):
    # Input
    session_id: str
    company_name: str
    company_website: Optional[str]
    research_objective: str
    
    # Step outputs
    research_plan: str
    raw_research_data: Dict
    analyzed_overview: str
    quality_score: int
    final_report: Dict
    
    # Metadata
    start_time: Optional[str]
    end_time: Optional[str]
    processing_status: str
    error_message: Optional[str]
    retry_count: int
```

### Conditional Routing Logic

```
After Quality Check Node:
    IF quality_score < threshold AND retry_count < max_retries:
        ROUTE TO: Researcher Node (Retry)
    ELSE:
        ROUTE TO: Reporter Node
```

## Error Handling & Recovery

### Error Handling Strategy
- **Graceful Degradation**: Partial results returned if available
- **Retry Logic**: Up to 3 automatic retries for transient errors
- **User-Initiated Retry**: Failed workflows can be retried manually
- **Error Logging**: All errors logged with context

### Recovery Mechanisms
1. **Workflow State Persistence**: State saved after each node
2. **Resumable Workflows**: Can resume from last successful step
3. **Data Backup**: Failed outputs preserved for analysis
4. **Audit Trail**: Complete record of all operations

## Scalability Considerations

### Current Design (Single Instance)
- SQLite for local development
- In-memory workflow state
- Synchronous node execution

### Production Scaling
- PostgreSQL for concurrent access
- Redis for distributed state
- Async execution with task queue (Celery/RQ)
- Load balancing for API servers
- Database connection pooling
- Caching layer (Redis) for frequently accessed data

## Security Measures

### Implemented
- CORS configuration
- Environment-based secrets
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)
- HTTPS ready

### Recommended for Production
- JWT authentication
- Rate limiting
- API key management
- Encryption for sensitive data
- SSL/TLS certificates
- VPC isolation

## Performance Optimization

### Frontend
- Code splitting with React Router
- Lazy loading of components
- CSS-in-JS optimization
- Image optimization
- Caching strategies

### Backend
- Database indexing on frequently queried fields
- Connection pooling
- Response pagination
- Caching of research results
- Async/await for I/O operations

## Monitoring & Logging

### Current Implementation
- Structured logging to stdout/files
- Request/response logging
- Error tracking with stack traces
- Audit log persistence

### Recommended for Production
- Application Performance Monitoring (APM)
- Log aggregation (ELK, CloudWatch)
- Alerting on critical errors
- Health check endpoints
- Metrics collection (Prometheus)
