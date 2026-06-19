# Engineering Decisions

## Decision 1: LangGraph vs Traditional State Machines

### Decision
**Use LangGraph for workflow orchestration** instead of custom state machine implementation.

### Alternatives Considered

1. **Custom Python State Machine**
   - Pros: Full control, lightweight, no dependencies
   - Cons: Reinventing the wheel, harder to debug, no built-in monitoring

2. **Apache Airflow**
   - Pros: Production-grade, rich ecosystem, scheduling
   - Cons: Heavy, complex setup, overkill for single workflow

3. **AWS Step Functions**
   - Pros: Fully managed, scalable, good monitoring
   - Cons: Vendor lock-in, costs add up, less flexible

### Rationale
- **Conditional Routing**: LangGraph's built-in support for conditional edges makes quality-gated retries trivial
- **State Management**: First-class state passing between nodes eliminates middleware complexity
- **Developer Experience**: Clear node-based mental model, excellent for the research workflow pattern
- **Future-Proof**: As the product scales, LangGraph's streaming and branching capabilities become valuable
- **LLM-Native**: Designed by Anthropic with LLM use cases in mind

### Tradeoffs
- **Less Mature**: Newer than Airflow but actively developed
- **Smaller Ecosystem**: Fewer integrations, but those that exist are well-maintained
- **Learning Curve**: Team needs to learn the LangGraph abstraction

### Outcome
LangGraph provides exactly the right abstraction level. The five-node workflow is clean and readable. Conditional routing for quality checks is implementation in 5 lines.

---

## Decision 2: React + FastAPI vs Django

### Decision
**Use React + FastAPI** for frontend and backend respectively.

### Alternatives Considered

1. **Django + Django Templates**
   - Pros: All-in-one framework, built-in admin, ORM
   - Cons: Heavier, slower iteration, monolithic

2. **Flask + Jinja2**
   - Pros: Lightweight, flexible, simple
   - Cons: Fewer batteries included, more boilerplate

3. **Next.js + API Routes**
   - Pros: Full-stack JavaScript, great DX, built-in optimization
   - Cons: JavaScript everywhere might not be ideal for complex data processing

### Rationale
- **Separation of Concerns**: Clear frontend/backend boundary enables independent scaling
- **FastAPI Excellence**: 
  - Async-first → perfect for I/O-heavy research workflows
  - Automatic OpenAPI docs
  - Pydantic validation (type safety)
  - Performance matches Node.js/Go
- **React Familiarity**: Modern, large ecosystem, excellent tooling
- **Real-Time Capable**: Easy to add WebSockets for progress streaming later
- **Developer Experience**: Hot reload, instant feedback loop

### Tradeoffs
- **Two Code Bases**: More to maintain, but separation benefit outweighs this
- **API Surface Design**: Must design API carefully; no templates to fall back on
- **DevOps Complexity**: Two services to deploy, but worth it for scalability

### Outcome
The separation enabled us to:
- Iterate on frontend UI without backend restarts
- Scale backend and frontend independently
- Add WebSocket progress streaming easily
- Use modern development tooling (Vite, TypeScript later if needed)

---

## Decision 3: SQLite vs PostgreSQL

### Decision
**Use SQLite for development, design for PostgreSQL migration** with SQLAlchemy ORM for database abstraction.

### Alternatives Considered

1. **PostgreSQL Immediately**
   - Pros: Production-ready, better concurrency, advanced features
   - Cons: Local development complexity, dependency management

2. **MongoDB**
   - Pros: Flexible schema, good for nested data (reports)
   - Cons: Less ACID guarantees, worse for structured queries

3. **DynamoDB/NoSQL Cloud Database**
   - Pros: Fully managed, scales automatically
   - Cons: Vendor lock-in, expensive at low volumes

### Rationale
- **Development Speed**: SQLite starts immediately, no Docker required
- **Correctness**: ACID transactions for critical operations
- **Flexibility**: Can migrate to PostgreSQL by changing connection string
- **Data Integrity**: Foreign key constraints ensure data consistency
- **Audit Trail**: Time-series data (workflow steps) natural in relational model

### Tradeoffs
- **Limited Concurrency**: SQLite struggles with concurrent writes, but fine for our workflow
- **Migration Required**: Must migrate for production, adds one-time work
- **Not Clusterable**: SQLite can't run on multiple machines

### Outcome
Using SQLAlchemy means we can:
```python
# Development
DATABASE_URL = "sqlite:///./copilot.db"

# Production
DATABASE_URL = "postgresql://user:pass@host/copilot"
```
Zero code changes. The ORM abstraction was worth the ~5% performance loss.

---

## Decision 4: Synchronous vs Asynchronous Workflow Execution

### Decision
**Async/await workflow execution with background tasks** but sync node implementation.

### Rationale
- **Resource Efficient**: Hundreds of concurrent workflows on single server
- **Better API Response**: Client gets immediate confirmation, workflow runs in background
- **Easy Monitoring**: Can track progress via separate endpoint
- **Error Resilience**: Failed background task doesn't crash the API

### Implementation Details
```python
@router.post("/workflows/start")
async def start_workflow(request, background_tasks):
    background_tasks.add_task(execute_workflow_task, session_id, state, workflow)
    return {"status": "started"}  # Returns immediately

# Workflow runs in background
async def execute_workflow_task(session_id, state, workflow):
    final_state = await workflow.execute(state)
    save_to_database(final_state)
```

### Tradeoffs
- **Complexity**: Need to handle workflow lifecycle separately
- **Debugging**: Harder to trace failures in background tasks
- **Timeouts**: Long workflows might timeout if not careful

### Outcome
Allows frontend to show real-time progress without blocking API. Can add WebSocket streaming later for even better UX.

---

## Decision 5: Monolithic Backend vs Microservices

### Decision
**Monolithic FastAPI application** with clean service layer for future decomposition.

### Alternatives Considered

1. **Microservices From Day 1**
   - Pros: Technology flexibility, independent scaling
   - Cons: Operational complexity, distributed system challenges, overkill

2. **Serverless (AWS Lambda)**
   - Pros: Auto-scaling, pay-per-use
   - Cons: Cold starts, state management, harder to debug

### Rationale
- **MVP Simplicity**: Single service easier to develop and deploy initially
- **Performance**: No network latency between components
- **Debugging**: Stack traces and logs easier to trace
- **Cost**: Single server cheaper than distributed infrastructure
- **Future Flexibility**: Service layer designed for easy extraction to microservices

### Service Layer Structure
```python
# Clean separation for future splitting
app/
├── api/              # HTTP endpoints (easily extracts to separate service)
├── workflows/        # Workflow logic (could become async queue service)
├── services/         # Business logic (composable across services)
└── models/           # Data layer (shared via API/DB)
```

### Tradeoffs
- **Scaling Limitations**: Single server can only scale vertically
- **Flexibility**: Can't use different languages per component
- **Failure Domains**: One outage takes down entire system

### Outcome
Designed for monolith but structured for future microservice migration. Can split at service layer when needed.

---

## Top Technical Debt Items

### 1. **No Persistent Job Queue** (High Priority)
- **Current**: Background tasks lost on server restart
- **Impact**: In-flight workflows interrupted on deployment
- **Solution**: Add Redis queue (Celery/RQ) with persistence
- **Effort**: 2-3 days

### 2. **Limited Error Context** (Medium Priority)
- **Current**: Errors logged but not easily retrievable in UI
- **Impact**: Users can't debug why research failed
- **Solution**: Add error detail endpoint, richer error responses
- **Effort**: 1-2 days

### 3. **No Authentication** (Critical for Production)
- **Current**: Any request works
- **Impact**: Can't control access, audit trail unclear
- **Solution**: Add JWT auth, API key management
- **Effort**: 3-4 days

### 4. **Hard-Coded LLM Calls** (Medium Priority)
- **Current**: Mock LLM responses, not actually calling OpenAI
- **Impact**: Reports not actually researched
- **Solution**: Integrate real LLM calls with proper error handling
- **Effort**: 2-3 days

### 5. **No Rate Limiting** (Medium Priority)
- **Current**: No protection against abuse
- **Impact**: Could be DOS'd, or expensive LLM calls
- **Solution**: Add rate limiting per user/API key
- **Effort**: 1 day

---

## Biggest Technical Risk

### **Workflow State Consistency**
**Risk**: Lost or corrupted workflow state during execution.

**Why It Matters**:
- User loses all progress on 10-minute research
- Database inconsistent with workflow reality
- Retry mechanism fails

**Current Mitigation**:
- State saved after each node completion
- Transaction safety with ACID database
- Error handling in each node

**Additional Safeguards Needed**:
- State versioning and audit trail
- Periodic state snapshots
- Recovery mechanism from broken states
- Monitoring for state corruption

---

## With 2 Additional Weeks, What Would You Improve?

### Week 1: Production Readiness
1. **Authentication & Authorization** (3 days)
   - JWT token auth
   - User isolation
   - Admin dashboard

2. **Real LLM Integration** (2 days)
   - Integrate OpenAI API
   - Proper error handling
   - Cost tracking

3. **Async Job Queue** (2 days)
   - Redis + Celery setup
   - Persistent workflow state
   - Better scaling

### Week 2: Quality & Scale
1. **Comprehensive Testing** (3 days)
   - Unit tests for each node
   - Integration tests for workflows
   - Load testing

2. **Monitoring & Observability** (2 days)
   - Error tracking (Sentry)
   - Performance monitoring
   - Health checks

3. **Production Deployment** (2 days)
   - Docker configuration
   - PostgreSQL setup
   - CI/CD pipeline

**Prioritization**: Authentication > Real LLM > Monitoring > Testing

Focus on making it actually work with real data and real users before optimizing operations.
