"""FastAPI dependencies for API routes."""

from collections.abc import Awaitable
from typing import Any, Callable, Optional

from fastapi import Depends, HTTPException, status

from ..providers.base import TrendsProvider


async def get_trends_service():
    """Get the trends service instance."""
    from ..app import trends_service

    return trends_service


def get_provider(provider_name: Optional[str] = None) -> Callable[[Any], Awaitable[TrendsProvider]]:
    """Get a trends provider dependency."""

    async def _get_provider(service=Depends(get_trends_service)) -> TrendsProvider:
        try:
            provider: TrendsProvider = service.get_provider(provider_name)
            return provider
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return _get_provider
