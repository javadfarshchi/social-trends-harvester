"""Base adapter interface for social media trends providers."""

from abc import ABC, abstractmethod
from typing import Any


class TrendsProvider(ABC):
    """Abstract base class for social media trends providers."""

    @abstractmethod
    async def fetch_trending(
        self,
        count: int = 30,
        region: str = "US",
        **kwargs
    ) -> list[dict[str, Any]]:
        """
        Fetch trending content items.
        
        Args:
            count: Number of items to fetch (1-60)
            region: Region code (ISO 3166-1 alpha-2)
            **kwargs: Provider-specific parameters
            
        Returns:
            List of normalized content items
            
        Raises:
            ProviderError: When fetch operation fails
            ValidationError: When parameters are invalid
        """
        pass

    @abstractmethod
    async def fetch_hashtag_content(
        self,
        hashtag: str,
        count: int = 30,
        region: str = "US",
        **kwargs
    ) -> list[dict[str, Any]]:
        """
        Fetch content for a specific hashtag.
        
        Args:
            hashtag: Hashtag to search (without # prefix)
            count: Number of items to fetch (1-60)
            region: Region code (ISO 3166-1 alpha-2)
            **kwargs: Provider-specific parameters
            
        Returns:
            List of normalized content items
            
        Raises:
            ProviderError: When fetch operation fails
            ValidationError: When parameters are invalid
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy and operational.
        
        Returns:
            True if healthy, False otherwise
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name."""
        pass

    @property
    @abstractmethod
    def supported_regions(self) -> list[str]:
        """Get list of supported region codes."""
        pass

    async def initialize(self) -> bool:
        """
        Initialize the provider (optional override).

        Returns:
            True if initialization successful, False otherwise
        """
        return True

    async def cleanup(self):
        """
        Clean up provider resources (optional override).
        """
        return None


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class ValidationError(ProviderError):
    """Exception raised when input validation fails."""
    pass


class RateLimitError(ProviderError):
    """Exception raised when rate limit is exceeded."""
    pass


class TimeoutError(ProviderError):
    """Exception raised when request times out."""
    pass
