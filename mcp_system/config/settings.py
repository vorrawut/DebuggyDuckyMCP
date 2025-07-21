"""Application settings and configuration management."""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="MCP_"
    )
    
    # Application Settings
    app_name: str = Field(default="MCP", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    docs_url: Optional[str] = Field(default="/docs", description="API documentation URL")
    redoc_url: Optional[str] = Field(default="/redoc", description="ReDoc documentation URL")
    
    # Security Settings
    secret_key: str = Field(..., description="Secret key for JWT and other cryptographic operations")
    access_token_expire_minutes: int = Field(default=60, description="Access token expiration in minutes")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    
    # Database Settings
    database_url: str = Field(..., description="Database connection URL")
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow connections")
    
    # Redis Settings
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # AI/ML Settings
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="Default OpenAI model")
    openai_max_tokens: int = Field(default=2048, description="Max tokens for OpenAI requests")
    
    # Agent Settings
    max_agents: int = Field(default=10, description="Maximum number of concurrent agents")
    agent_timeout: int = Field(default=300, description="Agent execution timeout in seconds")
    
    # Execution Settings
    docker_host: str = Field(default="unix:///var/run/docker.sock", description="Docker host")
    execution_timeout: int = Field(default=60, description="Code execution timeout in seconds")
    max_memory_mb: int = Field(default=512, description="Max memory for code execution in MB")
    max_cpu_quota: int = Field(default=50000, description="Max CPU quota for execution (1 CPU = 100000)")
    
    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json, text)")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # Monitoring Settings
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    tracing_enabled: bool = Field(default=True, description="Enable distributed tracing")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    
    # CORS Settings
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    cors_methods: List[str] = Field(default=["*"], description="CORS allowed methods")
    cors_headers: List[str] = Field(default=["*"], description="CORS allowed headers")
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level setting."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()
    
    @validator("log_format")
    def validate_log_format(cls, v: str) -> str:
        """Validate log format setting."""
        allowed = ["json", "text"]
        if v not in allowed:
            raise ValueError(f"Log format must be one of: {allowed}")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            "url": self.database_url,
            "echo": self.database_echo,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
        }
    
    @property
    def redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration dictionary."""
        return {
            "url": self.redis_url,
            "db": self.redis_db,
            "password": self.redis_password,
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings() 