"""FastAPI application factory for Social Trends Harvester."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .api.v1 import routes_cache, routes_health, routes_trending
from .core.compliance import compliance_manager
from .core.config import settings
from .core.logging import setup_logging
from .providers.har import HARProvider
from .providers.mock import MockProvider

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class TrendsService:
    """Service for managing multiple trends providers."""

    def __init__(self):
        """Initialize trends service."""
        self.providers = {}
        self.default_provider = "mock"

    async def initialize(self):
        """Initialize all providers."""
        try:
            # Initialize mock provider (always available)
            mock_provider = MockProvider()
            await mock_provider.initialize()
            self.providers["mock"] = mock_provider

            # Initialize HAR provider if HAR data exists
            har_provider = HARProvider()
            if await har_provider.initialize():
                self.providers["har"] = har_provider
                logger.info("HAR provider initialized")
            else:
                logger.info("HAR provider not available (no HAR data found)")

            # Initialize compliance manager
            await compliance_manager.initialize()

            logger.info(f"Trends service initialized with providers: {list(self.providers.keys())}")

        except Exception as e:
            logger.error(f"Failed to initialize trends service: {e}")
            raise

    async def cleanup(self):
        """Cleanup all providers."""
        for provider in self.providers.values():
            try:
                await provider.cleanup()
            except Exception as e:
                logger.warning(f"Error cleaning up provider: {e}")

        await compliance_manager.cleanup()
        logger.info("Trends service cleaned up")

    def get_provider(self, provider_name: str = None):
        """Get a provider by name."""
        if provider_name is None:
            provider_name = self.default_provider

        if provider_name not in self.providers:
            available = ", ".join(self.providers.keys())
            raise ValueError(f"Provider '{provider_name}' not available. Available: {available}")

        return self.providers[provider_name]


# Global service instance
trends_service = TrendsService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Social Trends Harvester...")

    try:
        await trends_service.initialize()
        logger.info("Social Trends Harvester started successfully")
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise

    yield

    logger.info("Shutting down Social Trends Harvester...")
    try:
        await trends_service.cleanup()
        logger.info("Social Trends Harvester shut down successfully")
    except Exception as e:
        logger.warning(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.SERVICE_NAME,
        description="Platform-agnostic social media trends API with compliance features",
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["*"],
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    # Include routers
    app.include_router(routes_health.router, prefix="/api/v1", tags=["health"])
    app.include_router(routes_trending.router, prefix="/api/v1", tags=["trending"])
    app.include_router(routes_cache.router, prefix="/api/v1", tags=["cache"])

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "service": settings.SERVICE_NAME,
            "version": settings.VERSION,
            "description": "Platform-agnostic social media trends API with compliance features",
            "providers": list(trends_service.providers.keys()),
            "endpoints": {
                "health": "/api/v1/healthz",
                "trending": "/api/v1/trending?provider=mock&region=US&count=30",
                "hashtag": "/api/v1/hashtag/{tag}?provider=mock&region=US&count=30",
                "providers": "/api/v1/providers",
                "compliance": "/api/v1/compliance",
            },
            "documentation": {"swagger": "/docs", "redoc": "/redoc", "openapi": "/openapi.json"},
        }

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "social_trends_harvester.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
