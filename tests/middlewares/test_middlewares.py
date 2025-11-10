"""
Tests for middleware components.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request, Response
from fastapi.responses import JSONResponse


@pytest.mark.middlewares
@pytest.mark.unit
class TestAuthenticationMiddleware:
    """Test cases for authentication middleware."""
    
    @pytest.fixture
    def auth_middleware(self):
        """Create authentication middleware for testing."""
        from middlewares.authetication import AuthenticationMiddleware
        
        app = Mock()
        return AuthenticationMiddleware(app)
    
    @pytest.mark.asyncio
    async def test_dispatch_unprotected_route(self, auth_middleware):
        """Test middleware allows unprotected routes."""
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.urn = "test-urn"
        request.url.path = "/health"
        request.method = "GET"
        
        call_next = AsyncMock(return_value=Response())
        
        with patch('middlewares.authetication.unprotected_routes', {"/health"}):
            response = await auth_middleware.dispatch(request, call_next)
        
        assert response is not None
        assert call_next.called
    
    @pytest.mark.asyncio
    async def test_dispatch_protected_route_no_token(self, auth_middleware):
        """Test middleware blocks protected routes without token."""
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.urn = "test-urn"
        request.url.path = "/api/protected"
        request.method = "GET"
        request.headers.get.return_value = None
        
        call_next = AsyncMock()
        
        with patch('middlewares.authetication.unprotected_routes', set()):
            response = await auth_middleware.dispatch(request, call_next)
        
        assert isinstance(response, JSONResponse)
        assert not call_next.called
    
    @pytest.mark.asyncio
    async def test_dispatch_valid_token(self, auth_middleware):
        """Test middleware allows valid tokens."""
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.urn = "test-urn"
        request.url.path = "/api/protected"
        request.method = "GET"
        request.headers.get.return_value = "Bearer valid.token.here"
        
        mock_user = Mock()
        mock_user.id = 1
        mock_user.urn = "user-urn"
        
        call_next = AsyncMock(return_value=Response())
        
        with patch('middlewares.authetication.unprotected_routes', set()):
            with patch('middlewares.authetication.JWTUtility') as mock_jwt:
                mock_jwt.return_value.decode_token.return_value = {
                    "user_id": 1,
                    "user_urn": "user-urn"
                }
                with patch('middlewares.authetication.UserRepository') as mock_repo:
                    mock_repo.return_value.retrieve_record_by_id_and_is_logged_in.return_value = mock_user
                    
                    response = await auth_middleware.dispatch(request, call_next)
        
        assert call_next.called


@pytest.mark.middlewares
@pytest.mark.unit
class TestRateLimitMiddleware:
    """Test cases for rate limit middleware."""
    
    @pytest.fixture
    def rate_limit_middleware(self):
        """Create rate limit middleware for testing."""
        from middlewares.rate_limit import RateLimitMiddleware, RateLimitConfig
        
        app = Mock()
        config = RateLimitConfig(
            requests_per_minute=10,
            requests_per_hour=100
        )
        return RateLimitMiddleware(app, config)
    
    @pytest.mark.asyncio
    async def test_dispatch_within_limit(self, rate_limit_middleware):
        """Test middleware allows requests within limit."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers.get.return_value = None
        
        call_next = AsyncMock(return_value=Response())
        
        with patch('middlewares.rate_limit.unprotected_routes', set()):
            response = await rate_limit_middleware.dispatch(request, call_next)
        
        assert call_next.called
        assert hasattr(response, 'headers')
    
    @pytest.mark.asyncio
    async def test_dispatch_excluded_path(self, rate_limit_middleware):
        """Test middleware skips excluded paths."""
        request = Mock(spec=Request)
        request.url.path = "/health"
        request.method = "GET"
        
        call_next = AsyncMock(return_value=Response())
        
        with patch('middlewares.rate_limit.unprotected_routes', {"/health"}):
            rate_limit_middleware.excluded_paths = {"/health"}
            response = await rate_limit_middleware.dispatch(request, call_next)
        
        assert call_next.called
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_rate_limit_exceeded(self, rate_limit_middleware):
        """Test middleware blocks when rate limit is exceeded."""
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.urn = "test-urn"
        request.url.path = "/api/test"
        request.method = "GET"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers.get.return_value = None
        
        call_next = AsyncMock(return_value=Response())
        
        # Force rate limit to be exceeded
        rate_limit_middleware.store._sliding_windows["test-key"] = Mock()
        rate_limit_middleware.store.check_sliding_window = AsyncMock(
            return_value=(False, 100)
        )
        
        with patch('middlewares.rate_limit.unprotected_routes', set()):
            response = await rate_limit_middleware.dispatch(request, call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 429  # Too Many Requests


@pytest.mark.middlewares
@pytest.mark.unit
class TestRequestContextMiddleware:
    """Test cases for request context middleware."""
    
    @pytest.mark.asyncio
    async def test_adds_urn_to_request(self):
        """Test middleware adds URN to request state."""
        from middlewares.request_context import RequestContextMiddleware
        
        app = Mock()
        middleware = RequestContextMiddleware(app)
        
        request = Mock(spec=Request)
        request.state = Mock()
        
        call_next = AsyncMock(return_value=Response())
        
        await middleware.dispatch(request, call_next)
        
        assert hasattr(request.state, 'urn')
        assert request.state.urn is not None
        assert call_next.called

