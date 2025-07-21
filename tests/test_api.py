"""Tests for MCP FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from mcp import __version__


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_health_check(self, client: TestClient):
        """Test basic health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["version"] == __version__
        assert "timestamp" in data
        assert "checks" in data
        assert data["checks"]["api"] == "healthy"
    
    def test_readiness_check(self, client: TestClient):
        """Test readiness probe endpoint."""
        response = client.get("/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ready"
        assert data["version"] == __version__
        assert "timestamp" in data
        assert "checks" in data
        assert data["checks"]["database"] == "ready"
        assert data["checks"]["redis"] == "ready"
        assert data["checks"]["agents"] == "ready"
    
    def test_liveness_check(self, client: TestClient):
        """Test liveness probe endpoint."""
        response = client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "alive"
        assert data["version"] == __version__
        assert "timestamp" in data
    
    async def test_health_check_async(self, async_client: AsyncClient):
        """Test health check with async client."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["version"] == __version__


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns application info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "MCP (Master Control Program)"
        assert data["version"] == __version__
        assert data["status"] == "operational"
        assert "environment" in data
        assert "docs_url" in data
    
    async def test_root_endpoint_async(self, async_client: AsyncClient):
        """Test root endpoint with async client."""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "MCP (Master Control Program)"
        assert data["version"] == __version__


class TestMetricsEndpoint:
    """Tests for metrics endpoint."""
    
    def test_metrics_endpoint(self, client: TestClient):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        
        content = response.text
        assert "mcp_requests_total" in content
        assert "mcp_agents_active" in content
        assert "mcp_tasks_pending" in content
        
        # Check basic Prometheus format
        assert "# HELP" in content
        assert "# TYPE" in content


class TestMiddleware:
    """Tests for application middleware."""
    
    def test_request_id_header(self, client: TestClient):
        """Test that request ID is added to response headers."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) == 36  # UUID length with hyphens
        assert request_id.count("-") == 4  # UUID has 4 hyphens
    
    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are present."""
        # Make an OPTIONS request to trigger CORS
        response = client.options("/health")
        
        # FastAPI handles CORS automatically, so we check for the endpoint
        # In a real test, you might check for specific CORS headers
        assert response.status_code in [200, 405]  # 405 if OPTIONS not implemented
    
    async def test_request_logging(self, async_client: AsyncClient, caplog):
        """Test that requests are logged."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        
        # Check that request was logged
        # Note: This might need adjustment based on actual logging setup
        log_messages = [record.message for record in caplog.records]
        assert any("Request started" in msg for msg in log_messages)


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_404_error(self, client: TestClient):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/non-existent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_method_not_allowed(self, client: TestClient):
        """Test 405 error for wrong HTTP method."""
        response = client.post("/health")
        
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
    
    async def test_internal_server_error_handling(self, async_client: AsyncClient):
        """Test that internal server errors are handled gracefully."""
        # This would test error handling, but we don't have an endpoint that fails yet
        # In a real application, you might have a test endpoint that raises an exception
        pass


class TestApplicationLifecycle:
    """Tests for application lifecycle events."""
    
    def test_application_startup(self, app):
        """Test that application starts up correctly."""
        # The app fixture creates the application
        assert app.title == "MCP (Master Control Program)"
        assert app.version == __version__
    
    def test_application_routes(self, app):
        """Test that all expected routes are registered."""
        route_paths = [route.path for route in app.routes]
        
        expected_routes = [
            "/",
            "/health",
            "/health/ready", 
            "/health/live",
            "/metrics",
            "/openapi.json",  # Auto-generated by FastAPI
        ]
        
        for expected_route in expected_routes:
            assert expected_route in route_paths


class TestConfiguration:
    """Tests for application configuration."""
    
    def test_settings_injection(self, settings):
        """Test that settings are properly configured."""
        assert settings.app_name == "MCP"
        assert settings.app_version == "0.1.0"
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
    
    def test_environment_specific_behavior(self, settings):
        """Test environment-specific behavior."""
        if settings.environment == "development":
            assert settings.debug is True
            assert settings.docs_url is not None
        elif settings.environment == "production":
            assert settings.debug is False
            # In production, docs might be disabled
    
    def test_database_configuration(self, settings):
        """Test database configuration."""
        assert settings.database_url is not None
        assert "postgresql://" in settings.database_url or "sqlite://" in settings.database_url
    
    def test_redis_configuration(self, settings):
        """Test Redis configuration."""
        redis_config = settings.redis_config
        assert "url" in redis_config
        assert "db" in redis_config


class TestDocumentation:
    """Tests for API documentation."""
    
    def test_openapi_schema(self, client: TestClient):
        """Test OpenAPI schema generation."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "MCP (Master Control Program)"
        assert schema["info"]["version"] == __version__
        assert "paths" in schema
    
    def test_docs_page(self, client: TestClient, settings):
        """Test Swagger UI documentation page."""
        if settings.docs_url:
            response = client.get(settings.docs_url)
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
    
    def test_redoc_page(self, client: TestClient, settings):
        """Test ReDoc documentation page."""
        if settings.redoc_url:
            response = client.get(settings.redoc_url)
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]


# Integration tests that require external dependencies
@pytest.mark.integration
class TestIntegration:
    """Integration tests with external services."""
    
    async def test_database_connection(self):
        """Test database connection."""
        # TODO: Implement when database is set up
        pass
    
    async def test_redis_connection(self):
        """Test Redis connection.""" 
        # TODO: Implement when Redis integration is set up
        pass


# Performance tests
@pytest.mark.slow
class TestPerformance:
    """Performance tests for the API."""
    
    async def test_health_check_performance(self, async_client: AsyncClient):
        """Test health check endpoint performance."""
        import time
        
        start_time = time.time()
        response = await async_client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 0.1  # Should respond in under 100ms
    
    async def test_concurrent_requests(self, async_client: AsyncClient):
        """Test handling of concurrent requests."""
        import asyncio
        
        async def make_request():
            return await async_client.get("/health")
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy" 