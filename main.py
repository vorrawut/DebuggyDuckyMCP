"""
MCP (Master Control Program) - Main Application

Advanced Agentic Server for Code Planning, Execution & Evaluation
"""

import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from mcp_system import __version__, __description__
from mcp_system.config import get_settings
from mcp_system.config.logging import setup_logging, get_logger, request_logging_context


# Setup logging before anything else
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    settings = get_settings()
    
    # Startup
    logger.info("Starting MCP application", version=__version__, environment=settings.environment)
    
    # TODO: Initialize database connections
    # TODO: Initialize Redis connections
    # TODO: Initialize agent registry
    # TODO: Start background tasks
    
    logger.info("MCP application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MCP application")
    
    # TODO: Cleanup database connections
    # TODO: Cleanup Redis connections
    # TODO: Stop background tasks
    # TODO: Graceful agent shutdown
    
    logger.info("MCP application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title="MCP (Master Control Program)",
        description=__description__,
        version=__version__,
        docs_url=settings.docs_url if not settings.is_production else None,
        redoc_url=settings.redoc_url if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )
    
    # Add middleware
    setup_middleware(app, settings)
    
    # Add routes
    setup_routes(app, settings)
    
    return app


def setup_middleware(app: FastAPI, settings) -> None:
    """Setup application middleware."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Trusted host middleware (only in production)
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # TODO: Configure allowed hosts
        )
    
    # Request ID and logging middleware
    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        """Add request ID and structured logging."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        # Create logging context
        with request_logging_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        ):
            logger.info(
                "Request started",
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params),
                user_agent=request.headers.get("user-agent"),
            )
            
            try:
                response = await call_next(request)
                
                # Calculate request duration
                duration = time.time() - start_time
                
                logger.info(
                    "Request completed",
                    status_code=response.status_code,
                    duration_ms=round(duration * 1000, 2),
                )
                
                # Add request ID to response headers
                response.headers["X-Request-ID"] = request_id
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    "Request failed",
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_ms=round(duration * 1000, 2),
                    exc_info=True,
                )
                
                # Return error response
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal Server Error",
                        "request_id": request_id,
                        "message": "An unexpected error occurred"
                    },
                    headers={"X-Request-ID": request_id}
                )


def setup_routes(app: FastAPI, settings) -> None:
    """Setup application routes."""
    
    @app.get("/", tags=["Root"])
    async def root() -> Dict[str, Any]:
        """Root endpoint with basic application info."""
        return {
            "name": "MCP (Master Control Program)",
            "description": __description__,
            "version": __version__,
            "environment": settings.environment,
            "docs_url": settings.docs_url,
            "status": "operational"
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint for load balancers and monitoring."""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": __version__,
            "checks": {
                "api": "healthy",
                # TODO: Add database health check
                # TODO: Add Redis health check
                # TODO: Add agent health checks
            }
        }
    
    @app.get("/health/ready", tags=["Health"])
    async def readiness_check() -> Dict[str, Any]:
        """Readiness check endpoint for Kubernetes."""
        # TODO: Check if all required services are ready
        # TODO: Check if agents are initialized
        # TODO: Check if database migrations are complete
        
        return {
            "status": "ready",
            "timestamp": time.time(),
            "version": __version__,
            "checks": {
                "database": "ready",
                "redis": "ready",
                "agents": "ready",
            }
        }
    
    @app.get("/health/live", tags=["Health"])
    async def liveness_check() -> Dict[str, Any]:
        """Liveness check endpoint for Kubernetes."""
        return {
            "status": "alive",
            "timestamp": time.time(),
            "version": __version__,
        }
    
    @app.get("/metrics", tags=["Monitoring"])
    async def metrics() -> Response:
        """Prometheus metrics endpoint."""
        # TODO: Implement Prometheus metrics collection
        # TODO: Add custom business metrics
        
        metrics_content = """
        # HELP mcp_requests_total Total number of HTTP requests
        # TYPE mcp_requests_total counter
        mcp_requests_total{method="GET",endpoint="/health"} 1
        
        # HELP mcp_agents_active Number of active agents
        # TYPE mcp_agents_active gauge
        mcp_agents_active 0
        
        # HELP mcp_tasks_pending Number of pending tasks
        # TYPE mcp_tasks_pending gauge
        mcp_tasks_pending 0
        """
        
        return Response(content=metrics_content, media_type="text/plain")
    
    # TODO: Add API routes
    # app.include_router(agent_router, prefix=settings.api_prefix + "/agents", tags=["Agents"])
    # app.include_router(task_router, prefix=settings.api_prefix + "/tasks", tags=["Tasks"])
    # app.include_router(context_router, prefix=settings.api_prefix + "/contexts", tags=["Contexts"])
    # app.include_router(trace_router, prefix=settings.api_prefix + "/traces", tags=["Traces"])


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    logger.info(
        "Starting MCP server",
        host=settings.api_host,
        port=settings.api_port,
        environment=settings.environment,
        debug=settings.debug,
    )
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_config=None,  # Use our custom logging configuration
    ) 