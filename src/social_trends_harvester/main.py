"""FastAPI main application for Social Trends Harvester."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from .core.compliance import compliance_manager
from .core.models import (
    ComplianceInfo,
    ContentItem,
    ErrorResponse,
    HashtagResponse,
    HealthResponse,
    ProviderInfo,
    TrendingResponse,
)
from .providers.base import ProviderError, RateLimitError, TrendsProvider, ValidationError
from .providers.har import HARProvider
from .providers.mock import MockProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TrendsService:
    """Service for managing multiple trends providers."""

    def __init__(self):
        """Initialize trends service."""
        self.providers: dict[str, TrendsProvider] = {}
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

    def get_provider(self, provider_name: Optional[str] = None) -> TrendsProvider:
        """Get a provider by name."""
        if provider_name is None:
            provider_name = self.default_provider

        if provider_name not in self.providers:
            available = ", ".join(self.providers.keys())
            raise ValidationError(
                f"Provider '{provider_name}' not available. Available: {available}"
            )

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


# Create FastAPI app
app = FastAPI(
    title="Social Trends Harvester",
    description="Platform-agnostic API for harvesting social media trends data with compliance features",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
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


# Ensure service initialized lazily for test environments where lifespan may not run
async def ensure_initialized():
    """Initialize trends service if not already initialized."""
    try:
        if not trends_service.providers:
            await trends_service.initialize()
    except Exception as e:
        logger.error(f"Lazy initialization failed: {e}")
        raise


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=str(exc),
            error_code="VALIDATION_ERROR",
            http_status=400,
            timestamp=int(datetime.now().timestamp()),
        ).dict(),
    )


@app.exception_handler(RateLimitError)
async def rate_limit_handler(request, exc):
    """Handle rate limit errors."""
    return JSONResponse(
        status_code=429,
        content=ErrorResponse(
            error=str(exc),
            error_code="RATE_LIMIT_EXCEEDED",
            http_status=429,
            timestamp=int(datetime.now().timestamp()),
        ).dict(),
    )


@app.exception_handler(ProviderError)
async def provider_error_handler(request, exc):
    """Handle provider errors."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=str(exc),
            error_code="PROVIDER_ERROR",
            http_status=500,
            timestamp=int(datetime.now().timestamp()),
        ).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            http_status=500,
            timestamp=int(datetime.now().timestamp()),
        ).dict(),
    )


# API Routes
@app.get("/", response_model=dict[str, Any])
async def root():
    """Root endpoint with API information."""
    await ensure_initialized()
    return {
        "service": "Social Trends Harvester",
        "version": "1.0.0",
        "description": "Platform-agnostic social media trends API with compliance features",
        "providers": list(trends_service.providers.keys()),
        "endpoints": {
            "health": "/healthz",
            "trending": "/trending?provider=mock&region=US&count=30",
            "hashtag": "/hashtag/{tag}?provider=mock&region=US&count=30",
            "providers": "/providers",
            "compliance": "/compliance",
        },
        "documentation": {"swagger": "/docs", "redoc": "/redoc"},
    }


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        await ensure_initialized()
        provider_health = {}
        overall_status = "ok"

        for name, provider in trends_service.providers.items():
            try:
                is_healthy = await provider.health_check()
                provider_health[name] = is_healthy
                if not is_healthy:
                    overall_status = "degraded"
            except Exception as e:
                logger.error(f"Health check failed for provider {name}: {e}")
                provider_health[name] = False
                overall_status = "degraded"

        return HealthResponse(
            status=overall_status,
            providers=provider_health,
            compliance_status={
                "manager_initialized": compliance_manager._request_session is not None
            },
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(status="error", providers={})


@app.get("/trending", response_model=TrendingResponse)
async def get_trending(
    provider: Optional[str] = Query(default=None, description="Data provider to use"),
    region: str = Query(default="US", description="Region code (ISO 3166-1 alpha-2)"),
    count: int = Query(default=30, description="Number of items to return (1-60)"),
):
    """Get trending content."""
    try:
        logger.info(f"GET /trending - provider: {provider}, region: {region}, count: {count}")
        await ensure_initialized()
        # Manual validation to return 400 instead of 422
        if count < 1 or count > 60:
            raise ValidationError("Count must be between 1 and 60")

        trends_provider = trends_service.get_provider(provider)
        items_data = await trends_provider.fetch_trending(count=count, region=region)

        # Convert to ContentItem objects
        items = [ContentItem(**item) for item in items_data]

        response = TrendingResponse(
            items=items, total=len(items), region=region, provider=trends_provider.provider_name
        )

        logger.info(f"Returning {len(items)} trending items from {trends_provider.provider_name}")
        return response

    except (ValidationError, RateLimitError, ProviderError):
        raise
    except Exception as e:
        logger.error(f"Error in /trending endpoint: {e}")
        raise ProviderError(f"Failed to fetch trending content: {str(e)}")


@app.get("/hashtag/{tag}", response_model=HashtagResponse)
async def get_hashtag_content(
    tag: str = Path(..., description="Hashtag to search for (without # prefix)"),
    provider: Optional[str] = Query(default=None, description="Data provider to use"),
    region: str = Query(default="US", description="Region code (ISO 3166-1 alpha-2)"),
    count: int = Query(default=30, description="Number of items to return (1-60)"),
):
    """Get content for a specific hashtag."""
    try:
        logger.info(f"GET /hashtag/{tag} - provider: {provider}, region: {region}, count: {count}")
        await ensure_initialized()
        # Manual validation to return 400 instead of 422
        if count < 1 or count > 60:
            raise ValidationError("Count must be between 1 and 60")

        trends_provider = trends_service.get_provider(provider)
        items_data = await trends_provider.fetch_hashtag_content(
            hashtag=tag, count=count, region=region
        )

        # Convert to ContentItem objects
        items = [ContentItem(**item) for item in items_data]

        response = HashtagResponse(
            items=items,
            total=len(items),
            hashtag=tag,
            region=region,
            provider=trends_provider.provider_name,
        )

        logger.info(
            f"Returning {len(items)} items for hashtag #{tag} from {trends_provider.provider_name}"
        )
        return response

    except (ValidationError, RateLimitError, ProviderError):
        raise
    except Exception as e:
        logger.error(f"Error in /hashtag/{tag} endpoint: {e}")
        raise ProviderError(f"Failed to fetch hashtag content: {str(e)}")


@app.get("/providers", response_model=list[ProviderInfo])
async def get_providers():
    """Get information about available providers."""
    await ensure_initialized()
    providers_info = []

    for name, provider in trends_service.providers.items():
        try:
            info = ProviderInfo(
                name=provider.provider_name,
                supported_regions=provider.supported_regions,
                supported_features=["trending", "hashtag"],
                compliance_level="strict",
            )
            providers_info.append(info)
        except Exception as e:
            logger.warning(f"Failed to get info for provider {name}: {e}")

    return providers_info


@app.get("/compliance", response_model=ComplianceInfo)
async def get_compliance_info():
    """Get compliance information and guidelines."""
    await ensure_initialized()
    return ComplianceInfo(
        robots_txt_respected=True,
        rate_limiting_enabled=True,
        user_agent=compliance_manager.user_agent,
        supported_protocols=["https"],
        data_retention_policy="No data retention - requests processed in real-time",
    )


# Cache management endpoints (optional)
@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics (if caching is implemented)."""
    return {"message": "Cache statistics not implemented in this version", "status": "disabled"}


@app.delete("/cache/clear")
async def clear_cache():
    """Clear cache (if caching is implemented)."""
    return {"message": "Cache clearing not implemented in this version", "status": "disabled"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")  # nosec B104
