from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from config.settings import settings
import os

# Simple API Key security
# In production, this should be more robust (e.g., JWT, OAuth2)


async def api_key_middleware(request: Request, call_next):
    # Skip security for health check and docs
    if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc", "/stream"]:
        return await call_next(request)

    # Allow OPTIONS requests for CORS
    if request.method == "OPTIONS":
        return await call_next(request)

    # Enforce API Key for protected endpoints (default to 'las-secret-key' if not set)
    api_key = os.getenv("LAS_API_KEY") or "las-secret-key"
    request_key = request.headers.get("X-API-Key")
    if not request_key or request_key != api_key:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Invalid or missing API Key"},
        )

    response = await call_next(request)
    return response
