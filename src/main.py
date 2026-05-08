"""
FastAPI application entry point
Production-grade LLM Router with intelligent request routing
"""

import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from src.api.endpoints import api_router
from src.services.data_collection import data_collection_service
from src.services.cache import cache_service
from src.utils.logging import setup_logging, get_logger
from src.config import settings

# Initialize logging
setup_logging()
logger = get_logger(__name__)


# ============================================================================
# Middleware
# ============================================================================


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests for correlation"""

    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        request.state.request_id = request_id

        # Call the next middleware/route
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-Id"] = request_id
        return response


# ============================================================================
# Application Lifecycle Management
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info(
        "application_starting",
        env=settings.app_env,
        version="1.0.0",
    )

    # Initialize database tables
    await data_collection_service.create_tables()

    if settings.app_env == "production":
        db_ok = await data_collection_service.ping()
        cache_ok = True

        if settings.enable_caching:
            cache_ok = await cache_service.ping()

        if not db_ok:
            logger.error("startup_dependency_failed", dependency="database")
            raise RuntimeError("Database unavailable in production mode")

        if settings.enable_caching and not cache_ok:
            logger.error("startup_dependency_failed", dependency="redis")
            raise RuntimeError("Redis unavailable while caching is enabled")

        logger.info("startup_dependencies_verified")

    logger.info("application_ready")

    yield

    # Shutdown
    logger.info("application_shutting_down")

    # Close connections
    await data_collection_service.close()
    await cache_service.close()

    logger.info("application_stopped")


# ============================================================================
# Application Factory
# ============================================================================


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    app = FastAPI(
        title="Intelligent LLM Router",
        description="Production-grade multi-model LLM chat router with intelligent routing",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ========================================================================
    # Middleware Configuration
    # ========================================================================

    # Request ID middleware (must be first for proper request context)
    app.add_middleware(RequestIdMiddleware)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.app_env == "development" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted host middleware (production only)
    if settings.app_env == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure based on deployment
        )

    # ========================================================================
    # Route Registration
    # ========================================================================

    app.include_router(
        api_router,
        prefix="/api/v1",
        tags=["chat"],
    )

    # ========================================================================
    # Root Endpoint
    # ========================================================================

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "LLM Router",
            "version": "1.0.0",
            "status": "operational",
            "docs": "/docs",
        }

    return app


# ============================================================================
# Application Instance
# ============================================================================

app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower(),
    )
