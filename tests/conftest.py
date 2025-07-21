"""Pytest configuration and fixtures for MCP tests."""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import create_app
from mcp.config import get_settings
from mcp.models import Agent, Task, Context, Trace
from mcp.models.agent import AgentType, AgentStatus, AgentCapability
from mcp.models.task import TaskType, TaskStatus, TaskPriority, TaskResult
from mcp.models.context import ContextType
from mcp.models.trace import TraceLevel, TraceType


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def settings():
    """Get test settings."""
    return get_settings()


@pytest.fixture
def app():
    """Create FastAPI application for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Model Fixtures

@pytest.fixture
def sample_agent_capability() -> AgentCapability:
    """Create a sample agent capability."""
    return AgentCapability(
        name="python_code_generation",
        description="Generate Python code from natural language",
        version="1.0.0",
        parameters={
            "max_lines": 1000,
            "style": "pep8",
            "include_docstring": True
        }
    )


@pytest.fixture
def sample_agent(sample_agent_capability) -> Agent:
    """Create a sample agent."""
    return Agent(
        name="Python Code Generator",
        type=AgentType.CODE_GENERATION,
        description="An agent specialized in generating Python code",
        capabilities=[sample_agent_capability],
        config={
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 2048
        },
        status=AgentStatus.IDLE,
        total_tasks_completed=5,
        success_rate=0.9,
        average_execution_time=15.5
    )


@pytest.fixture
def sample_task_result() -> TaskResult:
    """Create a sample task result."""
    return TaskResult(
        success=True,
        output="def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
        artifacts={
            "generated_files": ["fibonacci.py"],
            "test_coverage": 0.95,
            "lines_of_code": 4
        },
        metrics={
            "execution_time": 2.5,
            "memory_usage": 45.2,
            "cpu_usage": 12.8
        }
    )


@pytest.fixture
def sample_task(sample_task_result) -> Task:
    """Create a sample task."""
    return Task(
        name="Generate Fibonacci Function",
        type=TaskType.CODE_GENERATION,
        description="Generate a Python function to calculate fibonacci numbers",
        input_data={
            "prompt": "Create a recursive function to calculate fibonacci numbers",
            "language": "python",
            "style": "functional"
        },
        parameters={
            "max_lines": 50,
            "include_docstring": True,
            "include_tests": False
        },
        requirements=["python>=3.8"],
        priority=TaskPriority.NORMAL,
        status=TaskStatus.COMPLETED,
        result=sample_task_result,
        estimated_duration=30.0,
        session_id="test-session-123",
        user_id="test-user"
    )


@pytest.fixture
def sample_context() -> Context:
    """Create a sample context."""
    return Context(
        name="Python Development Session",
        type=ContextType.SESSION,
        description="Context for Python code generation tasks",
        data={
            "programming_language": "python",
            "project_type": "web_application",
            "dependencies": ["fastapi", "sqlalchemy", "pydantic"]
        },
        variables={
            "current_file": "main.py",
            "last_function": "fibonacci",
            "code_style": "pep8"
        },
        metadata={
            "conversation_turns": 3,
            "code_quality_score": 0.88,
            "user_experience_level": "intermediate"
        },
        session_id="test-session-123",
        user_id="test-user"
    )


@pytest.fixture
def sample_trace() -> Trace:
    """Create a sample trace."""
    return Trace(
        trace_id="1a2b3c4d5e6f",
        span_id="7g8h9i0j",
        level=TraceLevel.INFO,
        type=TraceType.AGENT_EXECUTION,
        operation="generate_code",
        component="code_generation_agent",
        message="Successfully generated Python function",
        data={
            "generated_lines": 4,
            "language": "python",
            "complexity_score": 0.3
        },
        tags={
            "agent.type": "code_generation",
            "task.priority": "normal",
            "user.id": "test-user"
        },
        duration_ms=1250.5,
        cpu_usage_percent=15.2,
        memory_usage_mb=128.5
    )


# Factory Fixtures

@pytest.fixture
def agent_factory():
    """Factory for creating test agents."""
    def _create_agent(
        name: str = None,
        agent_type: AgentType = None,
        status: AgentStatus = None,
        **kwargs
    ) -> Agent:
        return Agent(
            name=name or f"Test Agent {uuid4().hex[:8]}",
            type=agent_type or AgentType.CODE_GENERATION,
            description="A test agent",
            status=status or AgentStatus.IDLE,
            **kwargs
        )
    return _create_agent


@pytest.fixture
def task_factory():
    """Factory for creating test tasks."""
    def _create_task(
        name: str = None,
        task_type: TaskType = None,
        status: TaskStatus = None,
        **kwargs
    ) -> Task:
        return Task(
            name=name or f"Test Task {uuid4().hex[:8]}",
            type=task_type or TaskType.CODE_GENERATION,
            description="A test task",
            status=status or TaskStatus.PENDING,
            **kwargs
        )
    return _create_task


@pytest.fixture
def context_factory():
    """Factory for creating test contexts."""
    def _create_context(
        name: str = None,
        context_type: ContextType = None,
        **kwargs
    ) -> Context:
        return Context(
            name=name or f"Test Context {uuid4().hex[:8]}",
            type=context_type or ContextType.SESSION,
            **kwargs
        )
    return _create_context


@pytest.fixture
def trace_factory():
    """Factory for creating test traces."""
    def _create_trace(
        operation: str = None,
        level: TraceLevel = None,
        trace_type: TraceType = None,
        **kwargs
    ) -> Trace:
        return Trace(
            trace_id=uuid4().hex[:16],
            span_id=uuid4().hex[:8],
            operation=operation or "test_operation",
            component="test_component",
            level=level or TraceLevel.INFO,
            type=trace_type or TraceType.SYSTEM_EVENT,
            message="Test trace message",
            **kwargs
        )
    return _create_trace


# Test Data Fixtures

@pytest.fixture
def sample_code_generation_request():
    """Sample code generation request data."""
    return {
        "name": "Generate User Model",
        "type": "code_generation",
        "description": "Generate a Pydantic model for user data",
        "input_data": {
            "prompt": "Create a User model with fields: id, name, email, created_at",
            "language": "python",
            "framework": "pydantic"
        },
        "parameters": {
            "include_docstring": True,
            "include_validation": True,
            "max_lines": 50
        },
        "priority": "normal"
    }


@pytest.fixture
def sample_agent_registration():
    """Sample agent registration data."""
    return {
        "name": "Advanced Python Generator",
        "type": "code_generation",
        "description": "An advanced Python code generation agent with AI capabilities",
        "capabilities": [
            {
                "name": "python_generation",
                "description": "Generate Python code",
                "version": "2.0.0",
                "parameters": {
                    "max_lines": 2000,
                    "supports_async": True,
                    "supports_typing": True
                }
            }
        ],
        "config": {
            "model": "gpt-4",
            "temperature": 0.8,
            "max_tokens": 4096
        }
    }


# Mock Fixtures

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "def hello_world():\n    \"\"\"Return a greeting.\"\"\"\n    return 'Hello, World!'"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 20,
            "completion_tokens": 15,
            "total_tokens": 35
        }
    }


# Database Fixtures (for when we add database support)

@pytest.fixture
async def db_session():
    """Create a test database session."""
    # TODO: Implement when we add database support
    # This would create a test database session with rollback
    pass


@pytest.fixture
async def clean_database():
    """Clean database before each test."""
    # TODO: Implement when we add database support
    # This would clean all tables before each test
    pass


# Configuration for pytest-asyncio
pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 