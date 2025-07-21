# MCP (Master Control Program)

> **Advanced Agentic Server for Code Planning, Execution & Evaluation**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

MCP is an intelligent orchestrator that coordinates specialized agents to solve complex coding tasks through autonomous planning, secure execution, contextual learning, and complete auditability.

## ✨ Features

- 🤖 **Multi-Agent Orchestration**: Coordinate specialized agents for different coding tasks
- 🔒 **Secure Code Execution**: Docker-based sandboxing with comprehensive safety controls
- 🧠 **Contextual Memory**: Long-term memory and iterative improvement through feedback loops
- 📊 **Complete Auditability**: Full trace logging for explainable AI and debugging
- ⚡ **Modern Architecture**: Built with FastAPI, Pydantic, and structured logging
- 🚀 **Production Ready**: Comprehensive monitoring, health checks, and scalability features

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent Layer   │    │ Execution Layer │    │ Context Layer   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • CodeGenAgent  │    │ • DockerSandbox │    │ • ContextMgr    │
│ • AnalysisAgent │    │ • SecurityVal   │    │ • MemoryStore   │
│ • TestingAgent  │    │ • ResourceMgr   │    │ • StateSerial   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ FastAPI Server  │
                    ├─────────────────┤
                    │ • REST API      │
                    │ • WebSocket     │
                    │ • Monitoring    │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mcp
```

### 2. Run the Setup Script

The setup script will handle everything for you:

```bash
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh
```

This script will:
- ✅ Check Python and Docker installation
- 📦 Create virtual environment and install dependencies
- 🐳 Start PostgreSQL and Redis containers
- ⚙️ Create configuration files
- 🧪 Run tests to verify the setup

### 3. Start the Development Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python main.py
```

Or use Docker Compose:

```bash
docker compose --profile dev up
```

### 4. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## 🛠️ Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
MCP_SECRET_KEY=your-secret-key-here
MCP_DATABASE_URL=postgresql://mcp_user:mcp_password@localhost:5432/mcp
MCP_REDIS_URL=redis://:mcp_redis_password@localhost:6379/0
```

### 4. Start Infrastructure

```bash
docker compose up -d postgres redis
```

### 5. Run the Application

```bash
python main.py
```

## 🔧 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .

# Security scan
bandit -r mcp/

# Run all quality checks
make quality  # If using Makefile
```

### Development with Docker

```bash
# Start full development environment
docker compose --profile dev up

# Start with monitoring stack
docker compose --profile monitoring up

# Build and run specific service
docker compose build mcp
docker compose run mcp pytest
```

## 📊 Monitoring and Observability

### Available Endpoints

- `/health` - Basic health check
- `/health/ready` - Readiness probe (Kubernetes)
- `/health/live` - Liveness probe (Kubernetes)
- `/metrics` - Prometheus metrics

### Monitoring Stack (Optional)

Start the full monitoring stack:

```bash
docker compose --profile monitoring up
```

Access monitoring tools:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 🧪 Testing

### Test Structure

```
tests/
├── conftest.py          # Test configuration and fixtures
├── test_models.py       # Model validation tests
├── test_api.py          # API endpoint tests
├── integration/         # Integration tests
└── fixtures/            # Test data fixtures
```

### Test Categories

- **Unit Tests**: Fast tests for individual components
- **Integration Tests**: Tests with external dependencies
- **End-to-End Tests**: Full workflow tests

### Writing Tests

```python
def test_agent_creation(agent_factory):
    """Test creating an agent."""
    agent = agent_factory(name="Test Agent")
    assert agent.name == "Test Agent"
    assert agent.status == AgentStatus.IDLE

async def test_api_health_check(async_client):
    """Test health check endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

## 📚 API Documentation

### Core Models

- **Agent**: Represents an individual agent with capabilities
- **Task**: Unit of work to be executed
- **Context**: Session and conversation context
- **Trace**: Audit trail and logging information

### Key Endpoints

```
GET    /                 # Application info
GET    /health           # Health check
GET    /docs             # Interactive API docs
GET    /metrics          # Prometheus metrics

# Future endpoints (Phase 2+)
POST   /api/v1/agents    # Register new agent
GET    /api/v1/agents    # List agents
POST   /api/v1/tasks     # Submit task
GET    /api/v1/tasks     # List tasks
```

## 🏛️ Project Structure

```
mcp/
├── main.py                    # FastAPI application entry point
├── mcp/
│   ├── __init__.py           # Package initialization
│   ├── config/               # Configuration management
│   │   ├── settings.py       # Pydantic settings
│   │   └── logging.py        # Structured logging
│   └── models/               # Data models
│       ├── agent.py          # Agent models
│       ├── task.py           # Task models
│       ├── context.py        # Context models
│       └── trace.py          # Trace models
├── tests/                    # Test suite
├── scripts/                  # Utility scripts
├── docker-compose.yml        # Development environment
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
└── pyproject.toml           # Project configuration
```

## ⚙️ Configuration

### Environment Variables

All configuration is done through environment variables with the `MCP_` prefix:

```bash
# Application
MCP_ENVIRONMENT=development
MCP_DEBUG=true
MCP_SECRET_KEY=your-secret-key

# Database
MCP_DATABASE_URL=postgresql://user:pass@host:port/db
MCP_REDIS_URL=redis://host:port/db

# Logging
MCP_LOG_LEVEL=INFO
MCP_LOG_FORMAT=json

# AI Integration (optional)
MCP_OPENAI_API_KEY=your-api-key
```

### Configuration Validation

MCP uses Pydantic for configuration validation with helpful error messages:

```python
from mcp.config import get_settings

settings = get_settings()
print(f"Running in {settings.environment} mode")
```

## 🔒 Security

### Code Execution Security

- **Docker Sandboxing**: All code execution happens in isolated containers
- **Resource Limits**: CPU, memory, and time constraints
- **Network Isolation**: No external network access during execution
- **Static Analysis**: Code is analyzed before execution

### API Security

- **Input Validation**: Comprehensive Pydantic validation
- **Rate Limiting**: Request throttling (future)
- **Authentication**: JWT-based auth (future)
- **CORS Configuration**: Configurable cross-origin policies

## 🛣️ Roadmap

### Phase 1: Foundation ✅
- [x] Core FastAPI application
- [x] Data models and validation
- [x] Configuration management
- [x] Structured logging
- [x] Testing framework
- [x] Docker development environment

### Phase 2: Agent Framework (Weeks 3-4)
- [ ] Base agent architecture
- [ ] Agent manager and orchestration
- [ ] Initial specialized agents
- [ ] Agent registry and discovery

### Phase 3: Execution & Security (Weeks 5-6)
- [ ] Docker sandbox implementation
- [ ] Security validation pipeline
- [ ] Resource management
- [ ] Container pool management

### Phase 4: Context & Memory (Weeks 7-8)
- [ ] Context management system
- [ ] Vector database integration
- [ ] Memory operations
- [ ] Learning integration

See [implementation.md](implementation.md) for the complete roadmap.

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run the setup script: `./scripts/setup_dev.sh`
4. Make your changes
5. Run tests: `pytest`
6. Run quality checks: `ruff check . && black . && mypy .`
7. Commit your changes: `git commit -m 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

### Code Style

- **Formatting**: Black with 100 character line limit
- **Linting**: Ruff with comprehensive rule set
- **Type Hints**: Full type coverage with mypy
- **Testing**: Pytest with comprehensive coverage
- **Documentation**: Docstrings for all public functions

### Commit Messages

Follow conventional commits:
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `test:` test additions or modifications
- `refactor:` code refactoring

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: For the excellent async web framework
- **Pydantic**: For powerful data validation
- **Structlog**: For structured logging capabilities
- **Docker**: For containerization and security isolation

## 📞 Support

- **Documentation**: [Full docs](implementation.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/mcp/discussions)

---

**Built with ❤️ by the MCP Development Team**
