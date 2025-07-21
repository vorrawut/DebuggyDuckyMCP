"""Task-related data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class TaskType(str, Enum):
    """Task type enumeration."""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CODE_EXECUTION = "code_execution"
    TEST_GENERATION = "test_generation"
    TEST_EXECUTION = "test_execution"
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    OPTIMIZATION = "optimization"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskResult(BaseModel):
    """Task execution result."""
    success: bool = Field(..., description="Whether the task was successful")
    output: Optional[str] = Field(default=None, description="Task output or result")
    error_message: Optional[str] = Field(default=None, description="Error message if task failed")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Generated artifacts")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "output": "def hello_world():\n    return 'Hello, World!'",
                "error_message": None,
                "artifacts": {
                    "generated_files": ["hello.py"],
                    "test_coverage": 0.95
                },
                "metrics": {
                    "execution_time": 2.5,
                    "memory_usage": 45.2
                }
            }
        }


class Task(BaseModel):
    """Task model representing a unit of work to be executed by agents."""
    
    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique task identifier")
    name: str = Field(..., description="Task name")
    type: TaskType = Field(..., description="Task type")
    description: str = Field(..., description="Task description")
    
    # Task Configuration
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for the task")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    requirements: List[str] = Field(default_factory=list, description="Task requirements")
    
    # Priority and Scheduling
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Task priority")
    deadline: Optional[datetime] = Field(default=None, description="Task deadline")
    estimated_duration: Optional[float] = Field(default=None, description="Estimated duration in seconds")
    
    # Assignment and Execution
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    assigned_agent_id: Optional[UUID] = Field(default=None, description="ID of assigned agent")
    parent_task_id: Optional[UUID] = Field(default=None, description="Parent task ID for subtasks")
    dependencies: List[UUID] = Field(default_factory=list, description="Task dependencies")
    
    # Results
    result: Optional[TaskResult] = Field(default=None, description="Task execution result")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Task completion timestamp")
    
    # Context
    context_id: Optional[UUID] = Field(default=None, description="Associated context ID")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    user_id: Optional[str] = Field(default=None, description="User who created the task")
    
    # Retry and Error Handling
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=5.0, description="Delay between retries in seconds")
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate task name format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Task name cannot be empty")
        if len(v) > 200:
            raise ValueError("Task name cannot exceed 200 characters")
        return v.strip()
    
    @validator("estimated_duration")
    def validate_estimated_duration(cls, v: Optional[float]) -> Optional[float]:
        """Validate estimated duration is positive."""
        if v is not None and v <= 0:
            raise ValueError("Estimated duration must be positive")
        return v
    
    @validator("retry_delay")
    def validate_retry_delay(cls, v: float) -> float:
        """Validate retry delay is non-negative."""
        if v < 0:
            raise ValueError("Retry delay cannot be negative")
        return v
    
    @validator("max_retries")
    def validate_max_retries(cls, v: int) -> int:
        """Validate max retries is non-negative."""
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        return v
    
    def update_status(self, status: TaskStatus) -> None:
        """Update task status and timestamp."""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if status == TaskStatus.IN_PROGRESS and not self.started_at:
            self.started_at = datetime.utcnow()
        elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT):
            if not self.completed_at:
                self.completed_at = datetime.utcnow()
    
    def assign_agent(self, agent_id: UUID) -> None:
        """Assign the task to an agent."""
        self.assigned_agent_id = agent_id
        self.update_status(TaskStatus.ASSIGNED)
    
    def start_execution(self) -> None:
        """Mark task as started."""
        self.update_status(TaskStatus.IN_PROGRESS)
    
    def complete_successfully(self, result: TaskResult) -> None:
        """Mark task as completed successfully."""
        self.result = result
        self.update_status(TaskStatus.COMPLETED)
    
    def fail(self, error_message: str, result: Optional[TaskResult] = None) -> None:
        """Mark task as failed."""
        if result:
            self.result = result
        else:
            self.result = TaskResult(
                success=False,
                error_message=error_message
            )
        self.update_status(TaskStatus.FAILED)
    
    def cancel(self) -> None:
        """Cancel the task."""
        self.update_status(TaskStatus.CANCELLED)
    
    def timeout(self) -> None:
        """Mark task as timed out."""
        self.update_status(TaskStatus.TIMEOUT)
    
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return (
            self.status in (TaskStatus.FAILED, TaskStatus.TIMEOUT) and
            self.retry_count < self.max_retries
        )
    
    def increment_retry(self) -> None:
        """Increment retry count and reset status."""
        if not self.can_retry():
            raise ValueError("Task cannot be retried")
        
        self.retry_count += 1
        self.update_status(TaskStatus.PENDING)
        # Reset timestamps for retry
        self.started_at = None
        self.completed_at = None
    
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.deadline:
            return False
        
        return (
            self.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED) and
            datetime.utcnow() > self.deadline
        )
    
    @property
    def execution_time(self) -> Optional[float]:
        """Calculate task execution time in seconds."""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()
    
    @property
    def is_terminal_status(self) -> bool:
        """Check if task is in a terminal status."""
        return self.status in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
            TaskStatus.TIMEOUT
        )
    
    @property
    def priority_score(self) -> int:
        """Get numeric priority score for sorting."""
        priority_scores = {
            TaskPriority.LOW: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.HIGH: 3,
            TaskPriority.CRITICAL: 4,
        }
        return priority_scores[self.priority]
    
    def add_dependency(self, task_id: UUID) -> None:
        """Add a task dependency."""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
            self.updated_at = datetime.utcnow()
    
    def remove_dependency(self, task_id: UUID) -> bool:
        """Remove a task dependency."""
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Generate Python Function",
                "type": "code_generation",
                "description": "Generate a Python function that calculates fibonacci numbers",
                "input_data": {
                    "prompt": "Create a function to calculate fibonacci numbers",
                    "language": "python"
                },
                "parameters": {
                    "max_lines": 50,
                    "include_docstring": True
                },
                "priority": "normal",
                "status": "pending",
                "estimated_duration": 30.0
            }
        } 