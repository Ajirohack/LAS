#!/usr/bin/env python3

import os, sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sources.logger import Logger
from services.interaction_service import get_interaction_service
from routers import query, stream, models, preferences, ollama_admin
from config.settings import settings

# Initialize database
from database.models import init_db

init_db()

app = FastAPI(title="LAS API", description="Local Agentic System API", version="0.1.0")
logger = Logger("api.log")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup security middleware (headers + rate limiting)
from middleware.security_middleware import setup_security_middleware

setup_security_middleware(app)
from middleware.security import api_key_middleware

app.middleware("http")(api_key_middleware)


# Wire core services at startup to avoid heavy initialization on import
@app.on_event("startup")
async def _wire_services_on_startup():
    try:
        query.set_interaction_service(get_interaction_service())
        logger.info("Interaction service wired to query router")
    except Exception as e:
        logger.error(f"Failed to wire interaction service: {e}")


# Include Routers - Legacy (backward compatibility)
app.include_router(query.router, prefix="/api", tags=["query-legacy"])  # versioned
app.include_router(stream.router, prefix="/api", tags=["stream-legacy"])  # versioned
app.include_router(models.router, prefix="/api", tags=["models-legacy"])  # versioned
app.include_router(query.router, tags=["query-compat"])  # root for tests/compat
app.include_router(stream.router, tags=["stream-compat"])  # root for tests/compat

# Create v1 API router
from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1")

# Include all routers under v1
v1_router.include_router(query.router, tags=["query"])
v1_router.include_router(stream.router, tags=["stream"])
v1_router.include_router(models.router, tags=["models"])
v1_router.include_router(preferences.router, tags=["preferences"])
v1_router.include_router(ollama_admin.router, tags=["ollama"])

# Import and register authentication router (high priority)
from routers import auth

v1_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

try:
    from routers import memory

    v1_router.include_router(memory.router, prefix="/memory", tags=["memory"])
except Exception as e:
    logger.error(f"Memory router load failed: {e}")

try:
    from routers import voice

    v1_router.include_router(
        voice.router, prefix="/voice", tags=["voice", "multimodal"]
    )
except Exception as e:
    logger.error(f"Voice router load failed: {e}")

try:
    from routers import plugins

    v1_router.include_router(plugins.router, prefix="/plugins", tags=["plugins"])
except Exception as e:
    logger.error(f"Plugins router load failed: {e}")

try:
    from routers import mcp_inspector

    v1_router.include_router(mcp_inspector.router, prefix="/mcp", tags=["mcp"])
except Exception as e:
    logger.error(f"MCP inspector router load failed: {e}")

try:
    from routers import webhooks

    v1_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
except Exception as e:
    logger.error(f"Webhooks router load failed: {e}")

try:
    from routers import performance

    v1_router.include_router(performance.router, prefix="/perf", tags=["performance"])
except Exception as e:
    logger.error(f"Performance router load failed: {e}")

try:
    from routers import security

    v1_router.include_router(security.router, prefix="/security", tags=["security"])
except Exception as e:
    logger.error(f"Security router load failed: {e}")

try:
    from routers import workflows

    v1_router.include_router(workflows.router, tags=["workflows"])
except Exception as e:
    logger.error(f"Workflows router load failed: {e}")

try:
    from routers import huggingface

    v1_router.include_router(huggingface.router, tags=["huggingface", "ai-models"])
except Exception as e:
    logger.error(f"HuggingFace router load failed: {e}")

# Mount v1 router under /api
app.include_router(v1_router, prefix="/api")

# Keep legacy routes for backward compatibility (deprecated - remove in 12 weeks)
# Note: These provide temporary backward compatibility alongside v1


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "healthy", "version": "0.1.0", "api_version": "v1"}


from fastapi.openapi.utils import get_openapi


def custom_openapi():
    """Generate custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="LAS API - Local Agent System",
        version="1.0.0",
        description="""
        # Local Agent System (LAS) API
        
        A comprehensive API for AI-powered agent interactions, workflow management, and multi-provider LLM integration.
        
        ## Features
        - 🔐 **JWT Authentication** with role-based access control
        - 🤖 **8 LLM Providers** (OpenAI, Claude, Gemini, Groq, etc.)
        - 📝 **Workflow Builder** for complex agent tasks
        - 🧠 **Memory Management** with knowledge graphs
        - 🔌 **Plugin System** for extensibility
        - ⚡ **Performance Optimized** with Redis caching & connection pooling
        
        ## Authentication
        
        Most endpoints require JWT authentication. To authenticate:
        
        1. Register: `POST /api/v1/auth/register`
        2. Login: `POST /api/v1/auth/login` → Get `access_token`
        3. Use token: Add header `Authorization: Bearer {access_token}`
        
        ## Rate Limiting
        
        - **Auth endpoints**: 5 requests/minute
        - **Query endpoints**: 60 requests/minute  
        - **Default**: 100 requests/minute
        
        ## API Versioning
        
        All endpoints are versioned under `/api/v1/`. Legacy `/api/` routes are deprecated.
        """,
        routes=app.routes,
        contact={
            "name": "LAS Support",
            "email": "support@las.local",
        },
        license_info={
            "name": "MIT",
        },
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from `/api/v1/auth/login`",
        }
    }

    # Add tags for organization
    openapi_schema["tags"] = [
        {
            "name": "Authentication",
            "description": "User authentication and authorization",
        },
        {"name": "Query", "description": "LLM query and response endpoints"},
        {"name": "Providers", "description": "LLM provider management"},
        {"name": "Memory", "description": "Knowledge graph and skill management"},
        {"name": "Workflows", "description": "Workflow creation and execution"},
        {"name": "Plugins", "description": "Plugin discovery and management"},
        {"name": "Performance", "description": "Performance monitoring and caching"},
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":

    def is_running_in_docker():
        try:
            if os.path.exists("/.dockerenv"):
                return True
            with open("/proc/1/cgroup", "r") as f:
                return "docker" in f.read()
        except Exception:
            return False

    if is_running_in_docker():
        print("[LAS Core] Starting in Docker container...")
    else:
        print("[LAS Core] Starting on host machine...")

    envport = os.getenv("BACKEND_PORT")
    port = int(envport) if envport else 7777
    uvicorn.run(app, host="0.0.0.0", port=port)
