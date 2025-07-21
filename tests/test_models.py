"""Tests for MCP data models."""

import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from mcp.models import Agent, Task, Context, Trace
from mcp.models.agent import AgentType, AgentStatus, AgentCapability
from mcp.models.task import TaskType, TaskStatus, TaskPriority, TaskResult
from mcp.models.context import ContextType
from mcp.models.trace import TraceLevel, TraceType


class TestAgentCapability:
    """Tests for AgentCapability model."""
    
    def test_create_capability(self):
        """Test creating a capability."""
        capability = AgentCapability(
            name="test_capability",
            description="A test capability",
            version="1.0.0",
            parameters={"key": "value"}
        )
        
        assert capability.name == "test_capability"
        assert capability.description == "A test capability"
        assert capability.version == "1.0.0"
        assert capability.parameters == {"key": "value"}
    
    def test_capability_defaults(self):
        """Test capability default values."""
        capability = AgentCapability(
            name="test_capability",
            description="A test capability"
        )
        
        assert capability.version == "1.0.0"
        assert capability.parameters == {}


class TestAgent:
    """Tests for Agent model."""
    
    def test_create_agent(self, sample_agent_capability):
        """Test creating an agent."""
        agent = Agent(
            name="Test Agent",
            type=AgentType.CODE_GENERATION,
            description="A test agent",
            capabilities=[sample_agent_capability]
        )
        
        assert agent.name == "Test Agent"
        assert agent.type == AgentType.CODE_GENERATION
        assert agent.status == AgentStatus.INITIALIZING
        assert len(agent.capabilities) == 1
        assert isinstance(agent.id, UUID)
        assert isinstance(agent.created_at, datetime)
    
    def test_agent_name_validation(self):
        """Test agent name validation."""
        # Empty name should fail
        with pytest.raises(ValueError, match="Agent name cannot be empty"):
            Agent(
                name="",
                type=AgentType.CODE_GENERATION,
                description="Test"
            )
        
        # Too long name should fail
        with pytest.raises(ValueError, match="Agent name cannot exceed 100 characters"):
            Agent(
                name="x" * 101,
                type=AgentType.CODE_GENERATION,
                description="Test"
            )
    
    def test_success_rate_validation(self):
        """Test success rate validation."""
        # Valid success rate
        agent = Agent(
            name="Test Agent",
            type=AgentType.CODE_GENERATION,
            description="Test",
            success_rate=0.5
        )
        assert agent.success_rate == 0.5
        
        # Invalid success rate should fail
        with pytest.raises(ValueError, match="Success rate must be between 0.0 and 1.0"):
            Agent(
                name="Test Agent",
                type=AgentType.CODE_GENERATION,
                description="Test",
                success_rate=1.5
            )
    
    def test_update_status(self, sample_agent):
        """Test updating agent status."""
        original_time = sample_agent.updated_at
        sample_agent.update_status(AgentStatus.BUSY)
        
        assert sample_agent.status == AgentStatus.BUSY
        assert sample_agent.updated_at > original_time
    
    def test_add_capability(self, sample_agent):
        """Test adding a capability."""
        new_capability = AgentCapability(
            name="new_capability",
            description="A new capability"
        )
        
        original_count = len(sample_agent.capabilities)
        sample_agent.add_capability(new_capability)
        
        assert len(sample_agent.capabilities) == original_count + 1
        assert sample_agent.has_capability("new_capability")
    
    def test_add_duplicate_capability(self, sample_agent):
        """Test adding a duplicate capability."""
        duplicate_capability = AgentCapability(
            name="python_code_generation",  # Same as existing
            description="Duplicate capability"
        )
        
        with pytest.raises(ValueError, match="Capability 'python_code_generation' already exists"):
            sample_agent.add_capability(duplicate_capability)
    
    def test_remove_capability(self, sample_agent):
        """Test removing a capability."""
        assert sample_agent.has_capability("python_code_generation")
        
        removed = sample_agent.remove_capability("python_code_generation")
        assert removed is True
        assert not sample_agent.has_capability("python_code_generation")
        
        # Try to remove non-existent capability
        removed = sample_agent.remove_capability("non_existent")
        assert removed is False
    
    def test_update_heartbeat(self, sample_agent):
        """Test updating heartbeat."""
        original_heartbeat = sample_agent.last_heartbeat
        sample_agent.update_heartbeat()
        
        assert sample_agent.last_heartbeat > original_heartbeat
    
    def test_is_healthy(self, sample_agent):
        """Test health check."""
        # Agent without heartbeat is not healthy
        sample_agent.last_heartbeat = None
        assert not sample_agent.is_healthy()
        
        # Agent with recent heartbeat is healthy
        sample_agent.update_heartbeat()
        assert sample_agent.is_healthy()
        
        # Agent with old heartbeat is not healthy
        sample_agent.last_heartbeat = datetime.utcnow() - timedelta(minutes=2)
        assert not sample_agent.is_healthy(timeout_seconds=60)
    
    def test_update_performance_metrics(self, sample_agent):
        """Test updating performance metrics."""
        original_tasks = sample_agent.total_tasks_completed
        original_success_rate = sample_agent.success_rate
        
        # Successful task
        sample_agent.update_performance_metrics(True, 25.0)
        
        assert sample_agent.total_tasks_completed == original_tasks + 1
        assert sample_agent.success_rate > original_success_rate
        assert sample_agent.average_execution_time > 0
        
        # Failed task
        sample_agent.update_performance_metrics(False, 10.0)
        
        assert sample_agent.total_tasks_completed == original_tasks + 2


class TestTaskResult:
    """Tests for TaskResult model."""
    
    def test_create_task_result(self):
        """Test creating a task result."""
        result = TaskResult(
            success=True,
            output="Generated code here",
            artifacts={"files": ["test.py"]},
            metrics={"time": 1.5}
        )
        
        assert result.success is True
        assert result.output == "Generated code here"
        assert result.artifacts == {"files": ["test.py"]}
        assert result.metrics == {"time": 1.5}
    
    def test_task_result_defaults(self):
        """Test task result default values."""
        result = TaskResult(success=False)
        
        assert result.output is None
        assert result.error_message is None
        assert result.artifacts == {}
        assert result.metrics == {}


class TestTask:
    """Tests for Task model."""
    
    def test_create_task(self):
        """Test creating a task."""
        task = Task(
            name="Test Task",
            type=TaskType.CODE_GENERATION,
            description="A test task"
        )
        
        assert task.name == "Test Task"
        assert task.type == TaskType.CODE_GENERATION
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.NORMAL
        assert isinstance(task.id, UUID)
        assert isinstance(task.created_at, datetime)
    
    def test_task_name_validation(self):
        """Test task name validation."""
        # Empty name should fail
        with pytest.raises(ValueError, match="Task name cannot be empty"):
            Task(
                name="",
                type=TaskType.CODE_GENERATION,
                description="Test"
            )
        
        # Too long name should fail
        with pytest.raises(ValueError, match="Task name cannot exceed 200 characters"):
            Task(
                name="x" * 201,
                type=TaskType.CODE_GENERATION,
                description="Test"
            )
    
    def test_estimated_duration_validation(self):
        """Test estimated duration validation."""
        # Valid duration
        task = Task(
            name="Test Task",
            type=TaskType.CODE_GENERATION,
            description="Test",
            estimated_duration=30.0
        )
        assert task.estimated_duration == 30.0
        
        # Invalid duration should fail
        with pytest.raises(ValueError, match="Estimated duration must be positive"):
            Task(
                name="Test Task",
                type=TaskType.CODE_GENERATION,
                description="Test",
                estimated_duration=-10.0
            )
    
    def test_update_status(self, sample_task):
        """Test updating task status."""
        original_time = sample_task.updated_at
        sample_task.update_status(TaskStatus.IN_PROGRESS)
        
        assert sample_task.status == TaskStatus.IN_PROGRESS
        assert sample_task.updated_at > original_time
        assert sample_task.started_at is not None
    
    def test_assign_agent(self, sample_task):
        """Test assigning an agent to a task."""
        agent_id = uuid4()
        sample_task.assign_agent(agent_id)
        
        assert sample_task.assigned_agent_id == agent_id
        assert sample_task.status == TaskStatus.ASSIGNED
    
    def test_complete_successfully(self, sample_task):
        """Test completing a task successfully."""
        result = TaskResult(success=True, output="Success!")
        sample_task.complete_successfully(result)
        
        assert sample_task.status == TaskStatus.COMPLETED
        assert sample_task.result == result
        assert sample_task.completed_at is not None
    
    def test_fail_task(self, sample_task):
        """Test failing a task."""
        sample_task.fail("Something went wrong")
        
        assert sample_task.status == TaskStatus.FAILED
        assert sample_task.result.success is False
        assert sample_task.result.error_message == "Something went wrong"
        assert sample_task.completed_at is not None
    
    def test_can_retry(self, sample_task):
        """Test retry logic."""
        # Pending task cannot retry
        assert not sample_task.can_retry()
        
        # Failed task can retry
        sample_task.fail("Error")
        assert sample_task.can_retry()
        
        # Task that exceeded max retries cannot retry
        sample_task.retry_count = sample_task.max_retries
        assert not sample_task.can_retry()
    
    def test_increment_retry(self, sample_task):
        """Test incrementing retry count."""
        sample_task.fail("Error")
        original_retry_count = sample_task.retry_count
        
        sample_task.increment_retry()
        
        assert sample_task.retry_count == original_retry_count + 1
        assert sample_task.status == TaskStatus.PENDING
        assert sample_task.started_at is None
        assert sample_task.completed_at is None
    
    def test_is_overdue(self, sample_task):
        """Test overdue check."""
        # Task without deadline is never overdue
        assert not sample_task.is_overdue()
        
        # Task with future deadline is not overdue
        sample_task.deadline = datetime.utcnow() + timedelta(hours=1)
        assert not sample_task.is_overdue()
        
        # Task with past deadline is overdue
        sample_task.deadline = datetime.utcnow() - timedelta(hours=1)
        assert sample_task.is_overdue()
        
        # Completed task is never overdue
        sample_task.update_status(TaskStatus.COMPLETED)
        assert not sample_task.is_overdue()
    
    def test_execution_time(self, sample_task):
        """Test execution time calculation."""
        # Task not started has no execution time
        sample_task.started_at = None
        assert sample_task.execution_time is None
        
        # Running task has execution time
        sample_task.start_execution()
        assert sample_task.execution_time is not None
        assert sample_task.execution_time > 0
    
    def test_priority_score(self, sample_task):
        """Test priority score calculation."""
        sample_task.priority = TaskPriority.LOW
        assert sample_task.priority_score == 1
        
        sample_task.priority = TaskPriority.NORMAL
        assert sample_task.priority_score == 2
        
        sample_task.priority = TaskPriority.HIGH
        assert sample_task.priority_score == 3
        
        sample_task.priority = TaskPriority.CRITICAL
        assert sample_task.priority_score == 4
    
    def test_add_dependency(self, sample_task):
        """Test adding task dependencies."""
        dep_id = uuid4()
        sample_task.add_dependency(dep_id)
        
        assert dep_id in sample_task.dependencies
        
        # Adding same dependency again should not duplicate
        sample_task.add_dependency(dep_id)
        assert sample_task.dependencies.count(dep_id) == 1
    
    def test_remove_dependency(self, sample_task):
        """Test removing task dependencies."""
        dep_id = uuid4()
        sample_task.add_dependency(dep_id)
        
        removed = sample_task.remove_dependency(dep_id)
        assert removed is True
        assert dep_id not in sample_task.dependencies
        
        # Removing non-existent dependency
        removed = sample_task.remove_dependency(uuid4())
        assert removed is False


class TestContext:
    """Tests for Context model."""
    
    def test_create_context(self):
        """Test creating a context."""
        context = Context(
            name="Test Context",
            type=ContextType.SESSION
        )
        
        assert context.name == "Test Context"
        assert context.type == ContextType.SESSION
        assert context.version == 1
        assert context.is_active is True
        assert isinstance(context.id, UUID)
        assert isinstance(context.created_at, datetime)
    
    def test_context_name_validation(self):
        """Test context name validation."""
        # Empty name should fail
        with pytest.raises(ValueError, match="Context name cannot be empty"):
            Context(name="", type=ContextType.SESSION)
        
        # Too long name should fail
        with pytest.raises(ValueError, match="Context name cannot exceed 200 characters"):
            Context(name="x" * 201, type=ContextType.SESSION)
    
    def test_set_get_variable(self, sample_context):
        """Test setting and getting variables."""
        sample_context.set_variable("test_var", "test_value")
        
        assert sample_context.get_variable("test_var") == "test_value"
        assert sample_context.get_variable("non_existent", "default") == "default"
        assert sample_context.version == 2  # Version incremented
    
    def test_remove_variable(self, sample_context):
        """Test removing variables."""
        sample_context.set_variable("test_var", "test_value")
        
        removed = sample_context.remove_variable("test_var")
        assert removed is True
        assert sample_context.get_variable("test_var") is None
        
        # Removing non-existent variable
        removed = sample_context.remove_variable("non_existent")
        assert removed is False
    
    def test_set_get_data(self, sample_context):
        """Test setting and getting data."""
        sample_context.set_data("test_data", {"key": "value"})
        
        assert sample_context.get_data("test_data") == {"key": "value"}
        assert sample_context.get_data("non_existent", {}) == {}
    
    def test_add_remove_agents(self, sample_context):
        """Test adding and removing agents."""
        agent_id = uuid4()
        sample_context.add_agent(agent_id)
        
        assert agent_id in sample_context.agent_ids
        
        removed = sample_context.remove_agent(agent_id)
        assert removed is True
        assert agent_id not in sample_context.agent_ids
    
    def test_add_remove_tasks(self, sample_context):
        """Test adding and removing tasks."""
        task_id = uuid4()
        sample_context.add_task(task_id)
        
        assert task_id in sample_context.task_ids
        
        removed = sample_context.remove_task(task_id)
        assert removed is True
        assert task_id not in sample_context.task_ids
    
    def test_is_expired(self, sample_context):
        """Test expiration check."""
        # Context without expiration never expires
        assert not sample_context.is_expired()
        
        # Context with future expiration is not expired
        sample_context.expires_at = datetime.utcnow() + timedelta(hours=1)
        assert not sample_context.is_expired()
        
        # Context with past expiration is expired
        sample_context.expires_at = datetime.utcnow() - timedelta(hours=1)
        assert sample_context.is_expired()
    
    def test_clone(self, sample_context):
        """Test cloning a context."""
        clone = sample_context.clone("Cloned Context")
        
        assert clone.name == "Cloned Context"
        assert clone.id != sample_context.id
        assert clone.parent_context_id == sample_context.id
        assert clone.version == 1
        assert clone.data == sample_context.data
        assert clone.variables == sample_context.variables
    
    def test_merge_data(self, sample_context):
        """Test merging data from another context."""
        other_context = Context(
            name="Other Context",
            type=ContextType.SESSION,
            data={"new_key": "new_value"},
            variables={"new_var": "new_var_value"}
        )
        
        original_data_count = len(sample_context.data)
        sample_context.merge_data(other_context)
        
        assert len(sample_context.data) > original_data_count
        assert sample_context.data["new_key"] == "new_value"
        assert sample_context.variables["new_var"] == "new_var_value"
    
    def test_get_summary(self, sample_context):
        """Test getting context summary."""
        summary = sample_context.get_summary()
        
        assert "id" in summary
        assert "name" in summary
        assert "type" in summary
        assert "version" in summary
        assert "variables_count" in summary
        assert "data_size" in summary


class TestTrace:
    """Tests for Trace model."""
    
    def test_create_trace(self):
        """Test creating a trace."""
        trace = Trace(
            trace_id="test_trace",
            span_id="test_span",
            level=TraceLevel.INFO,
            type=TraceType.SYSTEM_EVENT,
            operation="test_operation",
            component="test_component",
            message="Test message"
        )
        
        assert trace.trace_id == "test_trace"
        assert trace.span_id == "test_span"
        assert trace.level == TraceLevel.INFO
        assert trace.type == TraceType.SYSTEM_EVENT
        assert trace.operation == "test_operation"
        assert trace.component == "test_component"
        assert trace.message == "Test message"
        assert isinstance(trace.id, UUID)
        assert isinstance(trace.timestamp, datetime)
    
    def test_trace_validation(self):
        """Test trace field validation."""
        # Empty message should fail
        with pytest.raises(ValueError, match="Trace message cannot be empty"):
            Trace(
                trace_id="test",
                span_id="test",
                level=TraceLevel.INFO,
                type=TraceType.SYSTEM_EVENT,
                operation="test",
                component="test",
                message=""
            )
        
        # Too long message should fail
        with pytest.raises(ValueError, match="Trace message cannot exceed 1000 characters"):
            Trace(
                trace_id="test",
                span_id="test",
                level=TraceLevel.INFO,
                type=TraceType.SYSTEM_EVENT,
                operation="test",
                component="test",
                message="x" * 1001
            )
    
    def test_add_tag_data(self, sample_trace):
        """Test adding tags and data."""
        sample_trace.add_tag("key", "value")
        sample_trace.add_data("data_key", {"nested": "data"})
        
        assert sample_trace.tags["key"] == "value"
        assert sample_trace.data["data_key"] == {"nested": "data"}
    
    def test_set_error(self, sample_trace):
        """Test setting error information."""
        sample_trace.set_error("E001", "Test error", "Stack trace here")
        
        assert sample_trace.level == TraceLevel.ERROR
        assert sample_trace.error_code == "E001"
        assert sample_trace.error_message == "Test error"
        assert sample_trace.stack_trace == "Stack trace here"
    
    def test_set_performance_metrics(self, sample_trace):
        """Test setting performance metrics."""
        sample_trace.set_performance_metrics(
            cpu_usage=25.5,
            memory_usage=128.0,
            disk_io=1024.0,
            network_io=512.0
        )
        
        assert sample_trace.cpu_usage_percent == 25.5
        assert sample_trace.memory_usage_mb == 128.0
        assert sample_trace.disk_io_kb == 1024.0
        assert sample_trace.network_io_kb == 512.0
    
    def test_is_error(self, sample_trace):
        """Test error detection."""
        assert not sample_trace.is_error()
        
        sample_trace.level = TraceLevel.ERROR
        assert sample_trace.is_error()
        
        sample_trace.level = TraceLevel.INFO
        sample_trace.error_code = "E001"
        assert sample_trace.is_error()
    
    def test_is_performance_trace(self, sample_trace):
        """Test performance trace detection."""
        assert sample_trace.is_performance_trace()  # Has duration_ms
        
        new_trace = Trace(
            trace_id="test",
            span_id="test",
            level=TraceLevel.INFO,
            type=TraceType.SYSTEM_EVENT,
            operation="test",
            component="test",
            message="Test"
        )
        assert not new_trace.is_performance_trace()
    
    def test_get_correlation_id(self, sample_trace):
        """Test correlation ID extraction."""
        assert sample_trace.get_correlation_id() == sample_trace.trace_id
        
        sample_trace.request_id = "request_123"
        assert sample_trace.get_correlation_id() == "request_123"
    
    def test_to_log_format(self, sample_trace):
        """Test converting to log format."""
        log_entry = sample_trace.to_log_format()
        
        assert "timestamp" in log_entry
        assert "level" in log_entry
        assert "message" in log_entry
        assert "trace_id" in log_entry
        assert "span_id" in log_entry
        assert "operation" in log_entry
        assert "component" in log_entry
        assert "type" in log_entry
        assert "duration_ms" in log_entry
    
    def test_create_request_trace(self):
        """Test creating a request trace."""
        trace = Trace.create_request_trace(
            trace_id="trace_123",
            span_id="span_123",
            method="GET",
            path="/api/test",
            user_id="user_123",
            request_id="req_123"
        )
        
        assert trace.trace_id == "trace_123"
        assert trace.span_id == "span_123"
        assert trace.type == TraceType.REQUEST
        assert trace.operation == "GET /api/test"
        assert trace.component == "api"
        assert trace.user_id == "user_123"
        assert trace.request_id == "req_123"
        assert trace.tags["http.method"] == "GET"
        assert trace.tags["http.path"] == "/api/test"
    
    def test_create_agent_trace(self):
        """Test creating an agent trace."""
        agent_id = uuid4()
        task_id = uuid4()
        
        trace = Trace.create_agent_trace(
            trace_id="trace_123",
            span_id="span_123",
            agent_id=agent_id,
            operation="generate_code",
            message="Generated code successfully",
            level=TraceLevel.INFO,
            task_id=task_id
        )
        
        assert trace.trace_id == "trace_123"
        assert trace.span_id == "span_123"
        assert trace.type == TraceType.AGENT_EXECUTION
        assert trace.operation == "generate_code"
        assert trace.component == "agent"
        assert trace.agent_id == agent_id
        assert trace.task_id == task_id
        assert trace.tags["agent.id"] == str(agent_id)
    
    def test_create_error_trace(self):
        """Test creating an error trace."""
        trace = Trace.create_error_trace(
            trace_id="trace_123",
            span_id="span_123",
            operation="test_operation",
            component="test_component",
            error_code="E001",
            error_message="Test error occurred",
            stack_trace="Stack trace here"
        )
        
        assert trace.trace_id == "trace_123"
        assert trace.span_id == "span_123"
        assert trace.level == TraceLevel.ERROR
        assert trace.type == TraceType.ERROR_EVENT
        assert trace.error_code == "E001"
        assert trace.error_message == "Test error occurred"
        assert trace.stack_trace == "Stack trace here"
        assert trace.tags["error"] == "true"
        assert trace.tags["error.code"] == "E001" 