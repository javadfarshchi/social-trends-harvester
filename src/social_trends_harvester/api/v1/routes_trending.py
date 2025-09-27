"""Trending content routes."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from ...core.config import settings
from ...providers.base import RateLimitError, ValidationError
from ...schemas.trending import ContentItem, HashtagResponse, TrendingResponse
from ..deps import get_trends_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/trending", response_model=TrendingResponse)
async def get_trending(
    provider: Optional[str] = Query(default=None, description="Data provider to use"),
    region: str = Query(default=settings.DEFAULT_REGION, description="Region code (ISO 3166-1 alpha-2)"),
    count: int = Query(default=settings.DEFAULT_COUNT, description=f"Number of items to return (1-{settings.MAX_COUNT})"),
    service = Depends(get_trends_service)
):
    """Get trending content."""
    try:
        logger.info(f"GET /trending - provider: {provider}, region: {region}, count: {count}")
        logger.info(f"Service has providers: {list(service.providers.keys())}")
        # Manual validation to return 400 instead of 422 (aligns with README/examples)
        if count < 1 or count > settings.MAX_COUNT:
            raise HTTPException(status_code=400, detail=f"Count must be between 1 and {settings.MAX_COUNT}")

        trends_provider = service.get_provider(provider)
        logger.info(f"Got provider: {trends_provider.provider_name}")

        items_data = await trends_provider.fetch_trending(count=count, region=region)
        logger.info(f"Got {len(items_data) if items_data else 0} items from provider")

        # Convert to ContentItem objects
        items = [ContentItem(**item) for item in items_data]

        response = TrendingResponse(
            items=items,
            total=len(items),
            region=region,
            provider=trends_provider.provider_name
        )

        logger.info(f"Returning {len(items)} trending items from {trends_provider.provider_name}")
        return response

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in /trending endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending content: {str(e)}")


@router.get("/hashtag/{tag}", response_model=HashtagResponse)
async def get_hashtag_content(
    tag: str = Path(..., description="Hashtag to search for (without # prefix)"),
    provider: Optional[str] = Query(default=None, description="Data provider to use"),
    region: str = Query(default=settings.DEFAULT_REGION, description="Region code (ISO 3166-1 alpha-2)"),
    count: int = Query(default=settings.DEFAULT_COUNT, description=f"Number of items to return (1-{settings.MAX_COUNT})"),
    service = Depends(get_trends_service)
):
    """Get content for a specific hashtag."""
    try:
        logger.info(f"GET /hashtag/{tag} - provider: {provider}, region: {region}, count: {count}")
        # Manual validation to return 400 instead of 422 (aligns with README/examples)
        if count < 1 or count > settings.MAX_COUNT:
            raise HTTPException(status_code=400, detail=f"Count must be between 1 and {settings.MAX_COUNT}")

        trends_provider = service.get_provider(provider)
        items_data = await trends_provider.fetch_hashtag_content(hashtag=tag, count=count, region=region)

        # Convert to ContentItem objects
        items = [ContentItem(**item) for item in items_data]

        response = HashtagResponse(
            items=items,
            total=len(items),
            hashtag=tag,
            region=region,
            provider=trends_provider.provider_name
        )

        logger.info(f"Returning {len(items)} items for hashtag #{tag} from {trends_provider.provider_name}")
        return response

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in /hashtag/{tag} endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch hashtag content: {str(e)}")
