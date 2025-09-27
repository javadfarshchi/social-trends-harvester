"""Cache management routes."""

import logging
from typing import Any

from fastapi import APIRouter

from ...core.cache import cache_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cache/stats")
async def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics."""
    return await cache_manager.get_stats()


@router.delete("/cache/clear")
async def clear_cache() -> dict[str, Any]:
    """Clear all cache entries."""
    success = await cache_manager.clear_all()
    return {"success": success, "message": "Cache cleared" if success else "Failed to clear cache"}
