# AI Research Copilot

A production-grade AI Research Copilot that helps sales and business professionals prepare for meetings by researching companies and generating structured briefings.

## 🎯 Project Overview

The AI Research Copilot automates company research and creates comprehensive briefings for sales meetings. It uses LangGraph workflows to orchestrate AI-powered research, analysis, and report generation.

**Key Features:**
- 🔍 Automated company research using web data
- 📊 Structured research reports with actionable insights
- 💬 Follow-up chat with context-aware responses
- 📝 Session persistence and history management
- ⚙️ Production-ready with comprehensive logging and error handling

## 🏗️ Architecture

```
┌─────────────────┐
│   React SPA     │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────┐
│   FastAPI Server            │
│   - Session Management      │
│   - Chat API                │
│   - Workflow Orchestration  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   LangGraph Workflow        │
│   - Research Planning       │
│   - Data Collection         │
│   - Analysis & Synthesis    │
│   - Quality Checks          │
│   - Report Generation       │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Persistent Storage        │
│   - SQLite/PostgreSQL       │
│   - Sessions & Reports      │
│   - Chat History            │
└─────────────────────────────┘
```

See `docs/architecture.md` for detailed architecture documentation.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Run migrations (if applicable)
python scripts/init_db.py

# Start server
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`
API docs available at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm start
```

Frontend runs on `http://localhost:3000`

## 📁 Project Structure

```
ai-research-copilot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app
│   │   ├── config.py                  # Configuration
│   │   ├── database.py                # Database setup
│   │   ├── models.py                  # Pydantic models
│   │   ├── schemas.py                 # Database schemas
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── sessions.py            # Session endpoints
│   │   │   ├── workflow.py            # Workflow endpoints
│   │   │   └── chat.py                # Chat endpoints
│   │   ├── workflows/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py               # LangGraph definition
│   │   │   ├── nodes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── planner.py         # Planning node
│   │   │   │   ├── researcher.py      # Research node
│   │   │   │   ├── analyzer.py        # Analysis node
│   │   │   │   ├── quality_check.py   # Quality check node
│   │   │   │   └── reporter.py        # Report generation node
│   │   │   ├── states.py              # Graph state definition
│   │   │   └── utils.py               # Workflow utilities
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── research_service.py    # Research logic
│   │   │   ├── llm_service.py         # LLM interactions
│   │   │   └── storage_service.py     # Data persistence
│   │   ├── middleware.py              # Custom middleware
│   │   └── logger.py                  # Logging setup
│   ├── scripts/
│   │   ├── init_db.py                 # Database initialization
│   │   └── seed_data.py               # Sample data
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_workflow.py
│   │   └── test_services.py
│   ├── requirements.txt
│   ├── .env.example
│   └── main.py                        # Entry point
│
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── index.js
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── SessionList.jsx        # Session history view
│   │   │   ├── SessionCreate.jsx      # Create new session
│   │   │   ├── SessionDetail.jsx      # Session detail page
│   │   │   ├── WorkflowProgress.jsx   # Progress visualization
│   │   │   ├── ChatInterface.jsx      # Chat UI
│   │   │   ├── ReportView.jsx         # Report display
│   │   │   └── LoadingStates.jsx      # Loading skeletons
│   │   ├── hooks/
│   │   │   ├── useApi.js              # API requests
│   │   │   ├── useSession.js          # Session state
│   │   │   └── useWebSocket.js        # WebSocket connection
│   │   ├── services/
│   │   │   ├── api.js                 # API client
│   │   │   └── websocket.js           # WebSocket manager
│   │   ├── styles/
│   │   │   ├── index.css
│   │   │   ├── components.css
│   │   │   └── responsive.css
│   │   └── utils/
│   │       ├── formatting.js
│   │       └── validation.js
│   ├── package.json
│   ├── .env.example
│   └── .gitignore
│
├── docs/
│   ├── architecture.md                # Architecture documentation
│   ├── engineering-decisions.md       # Engineering decisions
│   ├── product-improvements.md        # Product roadmap & thinking
│   ├── api-documentation.md           # API reference
│   └── workflow-guide.md              # LangGraph workflow details
│
├── .gitignore
└── docker-compose.yml                 # Local development setup
```

## 🔧 Technical Stack

**Frontend:**
- React 18 with Hooks
- Axios for HTTP requests
- TailwindCSS for styling
- React Router for navigation

**Backend:**
- Python 3.10+
- FastAPI for REST API
- LangGraph for workflow orchestration
- SQLAlchemy for ORM
- Pydantic for validation

**AI/LLM:**
- LangChain integration
- OpenAI API (configurable)
- Prompt engineering for research

**Deployment:**
- Docker & Docker Compose
- PostgreSQL for production
- Optional: AWS deployment

## 📊 Workflow Design

The LangGraph workflow implements a multi-stage research process:

```
START
  │
  ▼
┌─────────────────┐
│ PLANNER NODE    │ → Plan research strategy
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RESEARCH NODE   │ → Collect company data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ANALYZER NODE   │ → Analyze & synthesize
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ QUALITY NODE    │ → Validate quality
└────────┬────────┘
         │
    ┌────┴────┐
    │ PASS?   │
    └────┬────┘
         │
    ┌────┴────┐
    YES      NO → Loop back or retry
    │
    ▼
┌─────────────────┐
│ REPORTER NODE   │ → Generate report
└────────┬────────┘
         │
         ▼
       END
```

**Key Features:**
- ✅ Conditional routing with quality gates
- ✅ State persistence for recovery
- ✅ Intermediate outputs for streaming
- ✅ Error handling and retries
- ✅ Configurable workflow steps

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## 📝 Documentation

- **[architecture.md](docs/architecture.md)** - System design and components
- **[engineering-decisions.md](docs/engineering-decisions.md)** - Technical decisions and tradeoffs
- **[product-improvements.md](docs/product-improvements.md)** - Product strategy and roadmap
- **[api-documentation.md](docs/api-documentation.md)** - REST API reference
- **[workflow-guide.md](docs/workflow-guide.md)** - LangGraph workflow details

## 🚢 Production Deployment

### Using Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Environment Variables

Create `.env` files for both backend and frontend with required configuration:

```bash
# Backend .env
OPENAI_API_KEY=your_key
DATABASE_URL=postgresql://user:pass@localhost/copilot
LOG_LEVEL=INFO

# Frontend .env
REACT_APP_API_URL=https://api.example.com
REACT_APP_WS_URL=wss://api.example.com
```

## 📈 Monitoring

- Logging with structured output
- Health check endpoints
- Performance metrics
- Error tracking

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file

## 📞 Support

For issues, questions, or feedback, please open an issue on GitHub.

---

**Built with ❤️ for AI-powered sales enablement**
