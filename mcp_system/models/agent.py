"""Agent-related data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class AgentType(str, Enum):
    """Agent type enumeration."""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    TESTING = "testing"
    SECURITY = "security"
    REFACTORING = "refactoring"
    ORCHESTRATOR = "orchestrator"


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"


class AgentCapability(BaseModel):
    """Agent capability definition."""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    version: str = Field(default="1.0.0", description="Capability version")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Capability parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "python_code_generation",
                "description": "Generate Python code from natural language descriptions",
                "version": "1.0.0",
                "parameters": {
                    "max_lines": 1000,
                    "style": "pep8"
                }
            }
        }


class Agent(BaseModel):
    """Agent model representing an individual agent in the system."""
    
    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique agent identifier")
    name: str = Field(..., description="Agent name")
    type: AgentType = Field(..., description="Agent type")
    version: str = Field(default="1.0.0", description="Agent version")
    
    # Configuration
    description: str = Field(..., description="Agent description")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Agent capabilities")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent configuration")
    
    # Runtime State
    status: AgentStatus = Field(default=AgentStatus.INITIALIZING, description="Current agent status")
    current_task_id: Optional[UUID] = Field(default=None, description="Currently executing task ID")
    
    # Performance Metrics
    total_tasks_completed: int = Field(default=0, description="Total number of completed tasks")
    success_rate: float = Field(default=0.0, description="Success rate (0.0 to 1.0)")
    average_execution_time: float = Field(default=0.0, description="Average execution time in seconds")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Agent creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_heartbeat: Optional[datetime] = Field(default=None, description="Last heartbeat timestamp")
    
    # Optional fields for runtime
    host: Optional[str] = Field(default=None, description="Host where agent is running")
    port: Optional[int] = Field(default=None, description="Port where agent is listening")
    process_id: Optional[int] = Field(default=None, description="Process ID of the agent")
    
    @validator("success_rate")
    def validate_success_rate(cls, v: float) -> float:
        """Validate success rate is between 0.0 and 1.0."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Success rate must be between 0.0 and 1.0")
        return v
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate agent name format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Agent name cannot be empty")
        if len(v) > 100:
            raise ValueError("Agent name cannot exceed 100 characters")
        return v.strip()
    
    def update_status(self, status: AgentStatus) -> None:
        """Update agent status and timestamp."""
        self.status = status
        self.updated_at = datetime.utcnow()
    
    def add_capability(self, capability: AgentCapability) -> None:
        """Add a new capability to the agent."""
        # Check if capability already exists
        existing_names = {cap.name for cap in self.capabilities}
        if capability.name in existing_names:
            raise ValueError(f"Capability '{capability.name}' already exists")
        
        self.capabilities.append(capability)
        self.updated_at = datetime.utcnow()
    
    def remove_capability(self, capability_name: str) -> bool:
        """Remove a capability from the agent."""
        original_count = len(self.capabilities)
        self.capabilities = [cap for cap in self.capabilities if cap.name != capability_name]
        
        if len(self.capabilities) < original_count:
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability."""
        return any(cap.name == capability_name for cap in self.capabilities)
    
    def update_heartbeat(self) -> None:
        """Update the last heartbeat timestamp."""
        self.last_heartbeat = datetime.utcnow()
    
    def is_healthy(self, timeout_seconds: int = 60) -> bool:
        """Check if agent is healthy based on heartbeat."""
        if not self.last_heartbeat:
            return False
        
        time_since_heartbeat = (datetime.utcnow() - self.last_heartbeat).total_seconds()
        return time_since_heartbeat <= timeout_seconds
    
    def update_performance_metrics(
        self,
        task_completed: bool,
        execution_time: float
    ) -> None:
        """Update performance metrics after task completion."""
        self.total_tasks_completed += 1
        
        # Update success rate
        if task_completed:
            successful_tasks = int(self.success_rate * (self.total_tasks_completed - 1)) + 1
        else:
            successful_tasks = int(self.success_rate * (self.total_tasks_completed - 1))
        
        self.success_rate = successful_tasks / self.total_tasks_completed
        
        # Update average execution time (exponential moving average)
        if self.average_execution_time == 0.0:
            self.average_execution_time = execution_time
        else:
            alpha = 0.1  # Smoothing factor
            self.average_execution_time = (
                alpha * execution_time + (1 - alpha) * self.average_execution_time
            )
        
        self.updated_at = datetime.utcnow()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Python Code Generator",
                "type": "code_generation",
                "version": "1.0.0",
                "description": "Generates Python code from natural language descriptions",
                "capabilities": [
                    {
                        "name": "python_generation",
                        "description": "Generate Python code",
                        "version": "1.0.0",
                        "parameters": {"max_lines": 1000}
                    }
                ],
                "status": "idle",
                "total_tasks_completed": 42,
                "success_rate": 0.95,
                "average_execution_time": 15.5
            }
        } 