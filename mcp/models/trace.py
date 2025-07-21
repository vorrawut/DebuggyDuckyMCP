"""Trace-related data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class TraceLevel(str, Enum):
    """Trace level enumeration."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TraceType(str, Enum):
    """Trace type enumeration."""
    REQUEST = "request"
    RESPONSE = "response"
    AGENT_EXECUTION = "agent_execution"
    TASK_LIFECYCLE = "task_lifecycle"
    CONTEXT_OPERATION = "context_operation"
    SECURITY_EVENT = "security_event"
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_EVENT = "error_event"
    DECISION_POINT = "decision_point"
    SYSTEM_EVENT = "system_event"


class Trace(BaseModel):
    """Trace model for logging and auditability."""
    
    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique trace identifier")
    trace_id: str = Field(..., description="Trace ID for correlation across services")
    span_id: str = Field(..., description="Span ID for this specific operation")
    parent_span_id: Optional[str] = Field(default=None, description="Parent span ID for nested operations")
    
    # Classification
    level: TraceLevel = Field(..., description="Trace level")
    type: TraceType = Field(..., description="Trace type")
    operation: str = Field(..., description="Operation being traced")
    component: str = Field(..., description="Component that generated the trace")
    
    # Message and Data
    message: str = Field(..., description="Trace message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured trace data")
    tags: Dict[str, str] = Field(default_factory=dict, description="Trace tags for filtering")
    
    # Context
    user_id: Optional[str] = Field(default=None, description="User associated with the trace")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    request_id: Optional[str] = Field(default=None, description="Request identifier")
    agent_id: Optional[UUID] = Field(default=None, description="Agent identifier")
    task_id: Optional[UUID] = Field(default=None, description="Task identifier")
    context_id: Optional[UUID] = Field(default=None, description="Context identifier")
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Trace timestamp")
    duration_ms: Optional[float] = Field(default=None, description="Operation duration in milliseconds")
    
    # Error Information
    error_code: Optional[str] = Field(default=None, description="Error code if applicable")
    error_message: Optional[str] = Field(default=None, description="Error message if applicable")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace if applicable")
    
    # Performance Metrics
    cpu_usage_percent: Optional[float] = Field(default=None, description="CPU usage percentage")
    memory_usage_mb: Optional[float] = Field(default=None, description="Memory usage in MB")
    disk_io_kb: Optional[float] = Field(default=None, description="Disk I/O in KB")
    network_io_kb: Optional[float] = Field(default=None, description="Network I/O in KB")
    
    # System Information
    hostname: Optional[str] = Field(default=None, description="Hostname where trace was generated")
    process_id: Optional[int] = Field(default=None, description="Process ID")
    thread_id: Optional[str] = Field(default=None, description="Thread ID")
    
    @validator("message")
    def validate_message(cls, v: str) -> str:
        """Validate trace message format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Trace message cannot be empty")
        if len(v) > 1000:
            raise ValueError("Trace message cannot exceed 1000 characters")
        return v.strip()
    
    @validator("operation")
    def validate_operation(cls, v: str) -> str:
        """Validate operation format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Operation cannot be empty")
        if len(v) > 100:
            raise ValueError("Operation cannot exceed 100 characters")
        return v.strip()
    
    @validator("component")
    def validate_component(cls, v: str) -> str:
        """Validate component format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Component cannot be empty")
        if len(v) > 100:
            raise ValueError("Component cannot exceed 100 characters")
        return v.strip()
    
    @validator("duration_ms")
    def validate_duration(cls, v: Optional[float]) -> Optional[float]:
        """Validate duration is non-negative."""
        if v is not None and v < 0:
            raise ValueError("Duration cannot be negative")
        return v
    
    @validator("cpu_usage_percent")
    def validate_cpu_usage(cls, v: Optional[float]) -> Optional[float]:
        """Validate CPU usage percentage."""
        if v is not None and not 0 <= v <= 100:
            raise ValueError("CPU usage must be between 0 and 100")
        return v
    
    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the trace."""
        self.tags[key] = value
    
    def add_data(self, key: str, value: Any) -> None:
        """Add data to the trace."""
        self.data[key] = value
    
    def set_error(self, error_code: str, error_message: str, stack_trace: Optional[str] = None) -> None:
        """Set error information for the trace."""
        self.level = TraceLevel.ERROR
        self.error_code = error_code
        self.error_message = error_message
        self.stack_trace = stack_trace
    
    def set_performance_metrics(
        self,
        cpu_usage: Optional[float] = None,
        memory_usage: Optional[float] = None,
        disk_io: Optional[float] = None,
        network_io: Optional[float] = None,
    ) -> None:
        """Set performance metrics for the trace."""
        if cpu_usage is not None:
            self.cpu_usage_percent = cpu_usage
        if memory_usage is not None:
            self.memory_usage_mb = memory_usage
        if disk_io is not None:
            self.disk_io_kb = disk_io
        if network_io is not None:
            self.network_io_kb = network_io
    
    def set_timing(self, duration_ms: float) -> None:
        """Set timing information for the trace."""
        self.duration_ms = duration_ms
    
    def is_error(self) -> bool:
        """Check if trace represents an error."""
        return self.level in (TraceLevel.ERROR, TraceLevel.CRITICAL) or self.error_code is not None
    
    def is_performance_trace(self) -> bool:
        """Check if trace contains performance metrics."""
        return any([
            self.duration_ms is not None,
            self.cpu_usage_percent is not None,
            self.memory_usage_mb is not None,
            self.disk_io_kb is not None,
            self.network_io_kb is not None,
        ])
    
    def get_correlation_id(self) -> str:
        """Get correlation ID for grouping related traces."""
        # Use request_id if available, otherwise trace_id
        return self.request_id or self.trace_id
    
    def to_log_format(self) -> Dict[str, Any]:
        """Convert trace to structured log format."""
        log_entry = {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "operation": self.operation,
            "component": self.component,
            "type": self.type,
        }
        
        # Add optional fields if present
        if self.parent_span_id:
            log_entry["parent_span_id"] = self.parent_span_id
        if self.user_id:
            log_entry["user_id"] = self.user_id
        if self.session_id:
            log_entry["session_id"] = self.session_id
        if self.request_id:
            log_entry["request_id"] = self.request_id
        if self.agent_id:
            log_entry["agent_id"] = str(self.agent_id)
        if self.task_id:
            log_entry["task_id"] = str(self.task_id)
        if self.context_id:
            log_entry["context_id"] = str(self.context_id)
        if self.duration_ms is not None:
            log_entry["duration_ms"] = self.duration_ms
        
        # Add error information if present
        if self.error_code:
            log_entry["error_code"] = self.error_code
        if self.error_message:
            log_entry["error_message"] = self.error_message
        
        # Add performance metrics if present
        if self.cpu_usage_percent is not None:
            log_entry["cpu_usage_percent"] = self.cpu_usage_percent
        if self.memory_usage_mb is not None:
            log_entry["memory_usage_mb"] = self.memory_usage_mb
        
        # Add tags and data
        if self.tags:
            log_entry["tags"] = self.tags
        if self.data:
            log_entry["data"] = self.data
        
        return log_entry
    
    def to_opentelemetry_format(self) -> Dict[str, Any]:
        """Convert trace to OpenTelemetry format."""
        return {
            "traceId": self.trace_id,
            "spanId": self.span_id,
            "parentSpanId": self.parent_span_id,
            "operationName": self.operation,
            "startTime": int(self.timestamp.timestamp() * 1000000),  # microseconds
            "duration": int((self.duration_ms or 0) * 1000),  # microseconds
            "tags": {
                **self.tags,
                "component": self.component,
                "level": self.level,
                "type": self.type,
            },
            "logs": [
                {
                    "timestamp": int(self.timestamp.timestamp() * 1000000),
                    "fields": {
                        "level": self.level,
                        "message": self.message,
                        **self.data,
                    }
                }
            ] if self.message else [],
        }
    
    @classmethod
    def create_request_trace(
        cls,
        trace_id: str,
        span_id: str,
        method: str,
        path: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> "Trace":
        """Create a trace for an HTTP request."""
        return cls(
            trace_id=trace_id,
            span_id=span_id,
            level=TraceLevel.INFO,
            type=TraceType.REQUEST,
            operation=f"{method} {path}",
            component="api",
            message=f"Processing {method} request to {path}",
            user_id=user_id,
            request_id=request_id,
            tags={"http.method": method, "http.path": path},
        )
    
    @classmethod
    def create_agent_trace(
        cls,
        trace_id: str,
        span_id: str,
        agent_id: UUID,
        operation: str,
        message: str,
        level: TraceLevel = TraceLevel.INFO,
        task_id: Optional[UUID] = None,
    ) -> "Trace":
        """Create a trace for an agent operation."""
        return cls(
            trace_id=trace_id,
            span_id=span_id,
            level=level,
            type=TraceType.AGENT_EXECUTION,
            operation=operation,
            component="agent",
            message=message,
            agent_id=agent_id,
            task_id=task_id,
            tags={"agent.id": str(agent_id)},
        )
    
    @classmethod
    def create_error_trace(
        cls,
        trace_id: str,
        span_id: str,
        operation: str,
        component: str,
        error_code: str,
        error_message: str,
        stack_trace: Optional[str] = None,
    ) -> "Trace":
        """Create a trace for an error event."""
        trace = cls(
            trace_id=trace_id,
            span_id=span_id,
            level=TraceLevel.ERROR,
            type=TraceType.ERROR_EVENT,
            operation=operation,
            component=component,
            message=f"Error in {operation}: {error_message}",
            error_code=error_code,
            error_message=error_message,
            stack_trace=stack_trace,
            tags={"error": "true", "error.code": error_code},
        )
        return trace
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "trace_id": "1a2b3c4d5e6f7g8h",
                "span_id": "9i0j1k2l3m4n",
                "operation": "generate_code",
                "component": "code_generation_agent",
                "level": "info",
                "type": "agent_execution",
                "message": "Successfully generated Python function",
                "duration_ms": 1250.5,
                "data": {
                    "generated_lines": 25,
                    "language": "python",
                    "complexity_score": 0.7
                },
                "tags": {
                    "agent.type": "code_generation",
                    "task.priority": "normal"
                }
            }
        } 