"""
Security Middleware - Add security headers and rate limiting.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline';"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Custom rate limiting for specific patterns."""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_counts = {}  # In production, use Redis
        self.window = 60  # 60 seconds
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        
        # Strict rate limits for sensitive endpoints
        strict_limits = {
            "/api/v1/auth/login": {"limit": 5, "window": 60},
            "/api/v1/auth/register": {"limit": 3, "window": 3600},
            "/api/v1/auth/refresh": {"limit": 10, "window": 60},
        }
        
        # Check if path needs strict limiting
        for pattern, config in strict_limits.items():
            if pattern in path:
                key = f"{client_ip}:{pattern}"
                current_time = time.time()
                
                # Initialize or clean up old entries
                if key not in self.request_counts:
                    self.request_counts[key] = []
                
                # Remove old timestamps
                self.request_counts[key] = [
                    ts for ts in self.request_counts[key]
                    if current_time - ts < config["window"]
                ]
                
                # Check limit
                if len(self.request_counts[key]) >= config["limit"]:
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "error": "Rate limit exceeded",
                            "retry_after": config["window"]
                        }
                    )
                
                # Add current timestamp
                self.request_counts[key].append(current_time)
        
        response = await call_next(request)
        return response

def setup_security_middleware(app):
    """Setup all security middleware."""
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add rate limiting
    app.add_middleware(RateLimitMiddleware)
    
    # Add rate limit exception handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    return app
