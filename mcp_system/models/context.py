"""Context-related data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class ContextType(str, Enum):
    """Context type enumeration."""
    SESSION = "session"
    CONVERSATION = "conversation"
    TASK_EXECUTION = "task_execution"
    AGENT_STATE = "agent_state"
    CODE_WORKSPACE = "code_workspace"
    MEMORY_SNAPSHOT = "memory_snapshot"


class Context(BaseModel):
    """Context model for managing state and conversation context."""
    
    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique context identifier")
    name: str = Field(..., description="Context name")
    type: ContextType = Field(..., description="Context type")
    description: Optional[str] = Field(default=None, description="Context description")
    
    # Hierarchy and Relationships
    parent_context_id: Optional[UUID] = Field(default=None, description="Parent context ID")
    child_context_ids: List[UUID] = Field(default_factory=list, description="Child context IDs")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    
    # Context Data
    data: Dict[str, Any] = Field(default_factory=dict, description="Context data")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Context variables")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Context metadata")
    
    # State Management
    version: int = Field(default=1, description="Context version for optimistic locking")
    is_active: bool = Field(default=True, description="Whether context is active")
    is_persistent: bool = Field(default=True, description="Whether context should be persisted")
    
    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Context creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    accessed_at: datetime = Field(default_factory=datetime.utcnow, description="Last access timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Context expiration timestamp")
    
    # Associated Entities
    user_id: Optional[str] = Field(default=None, description="User who owns the context")
    agent_ids: List[UUID] = Field(default_factory=list, description="Associated agent IDs")
    task_ids: List[UUID] = Field(default_factory=list, description="Associated task IDs")
    
    # Memory and Storage
    memory_usage_bytes: int = Field(default=0, description="Memory usage in bytes")
    storage_location: Optional[str] = Field(default=None, description="Storage location for large contexts")
    compression_enabled: bool = Field(default=False, description="Whether context data is compressed")
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate context name format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Context name cannot be empty")
        if len(v) > 200:
            raise ValueError("Context name cannot exceed 200 characters")
        return v.strip()
    
    @validator("version")
    def validate_version(cls, v: int) -> int:
        """Validate version is positive."""
        if v <= 0:
            raise ValueError("Version must be positive")
        return v
    
    def update_timestamp(self) -> None:
        """Update the updated_at and accessed_at timestamps."""
        now = datetime.utcnow()
        self.updated_at = now
        self.accessed_at = now
    
    def access(self) -> None:
        """Update the accessed_at timestamp."""
        self.accessed_at = datetime.utcnow()
    
    def increment_version(self) -> None:
        """Increment version and update timestamp."""
        self.version += 1
        self.update_timestamp()
    
    def set_variable(self, key: str, value: Any) -> None:
        """Set a context variable."""
        self.variables[key] = value
        self.increment_version()
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a context variable."""
        self.access()
        return self.variables.get(key, default)
    
    def remove_variable(self, key: str) -> bool:
        """Remove a context variable."""
        if key in self.variables:
            del self.variables[key]
            self.increment_version()
            return True
        return False
    
    def set_data(self, key: str, value: Any) -> None:
        """Set context data."""
        self.data[key] = value
        self.increment_version()
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get context data."""
        self.access()
        return self.data.get(key, default)
    
    def remove_data(self, key: str) -> bool:
        """Remove context data."""
        if key in self.data:
            del self.data[key]
            self.increment_version()
            return True
        return False
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set context metadata."""
        self.metadata[key] = value
        self.increment_version()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get context metadata."""
        return self.metadata.get(key, default)
    
    def add_agent(self, agent_id: UUID) -> None:
        """Add an agent to the context."""
        if agent_id not in self.agent_ids:
            self.agent_ids.append(agent_id)
            self.increment_version()
    
    def remove_agent(self, agent_id: UUID) -> bool:
        """Remove an agent from the context."""
        if agent_id in self.agent_ids:
            self.agent_ids.remove(agent_id)
            self.increment_version()
            return True
        return False
    
    def add_task(self, task_id: UUID) -> None:
        """Add a task to the context."""
        if task_id not in self.task_ids:
            self.task_ids.append(task_id)
            self.increment_version()
    
    def remove_task(self, task_id: UUID) -> bool:
        """Remove a task from the context."""
        if task_id in self.task_ids:
            self.task_ids.remove(task_id)
            self.increment_version()
            return True
        return False
    
    def add_child_context(self, child_id: UUID) -> None:
        """Add a child context."""
        if child_id not in self.child_context_ids:
            self.child_context_ids.append(child_id)
            self.increment_version()
    
    def remove_child_context(self, child_id: UUID) -> bool:
        """Remove a child context."""
        if child_id in self.child_context_ids:
            self.child_context_ids.remove(child_id)
            self.increment_version()
            return True
        return False
    
    def is_expired(self) -> bool:
        """Check if context has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def deactivate(self) -> None:
        """Deactivate the context."""
        self.is_active = False
        self.update_timestamp()
    
    def activate(self) -> None:
        """Activate the context."""
        self.is_active = True
        self.update_timestamp()
    
    def clone(self, new_name: Optional[str] = None) -> "Context":
        """Create a clone of this context."""
        clone_data = self.dict(exclude={"id", "created_at", "updated_at", "accessed_at"})
        
        if new_name:
            clone_data["name"] = new_name
        else:
            clone_data["name"] = f"{self.name}_clone"
        
        # Reset version and set parent
        clone_data["version"] = 1
        clone_data["parent_context_id"] = self.id
        clone_data["child_context_ids"] = []
        
        return Context(**clone_data)
    
    def merge_data(self, other_context: "Context") -> None:
        """Merge data from another context."""
        # Merge variables (other context takes precedence)
        self.variables.update(other_context.variables)
        
        # Merge data (other context takes precedence)
        self.data.update(other_context.data)
        
        # Merge metadata (other context takes precedence)
        self.metadata.update(other_context.metadata)
        
        # Merge associated entities
        for agent_id in other_context.agent_ids:
            self.add_agent(agent_id)
        
        for task_id in other_context.task_ids:
            self.add_task(task_id)
        
        self.increment_version()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the context."""
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type,
            "version": self.version,
            "is_active": self.is_active,
            "variables_count": len(self.variables),
            "data_size": len(str(self.data)),
            "agent_count": len(self.agent_ids),
            "task_count": len(self.task_ids),
            "child_context_count": len(self.child_context_ids),
            "memory_usage_bytes": self.memory_usage_bytes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
        }
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Code Generation Session",
                "type": "session",
                "description": "Context for a code generation conversation",
                "data": {
                    "programming_language": "python",
                    "project_type": "web_app",
                    "requirements": ["FastAPI", "SQLAlchemy"]
                },
                "variables": {
                    "current_file": "main.py",
                    "last_generated_code": "def hello():\n    return 'Hello'"
                },
                "metadata": {
                    "conversation_turns": 5,
                    "code_quality_score": 0.85
                },
                "is_active": True,
                "version": 3
            }
        } 