"""Mock provider that loads content from fixtures for testing and demonstration."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .base import ProviderError, TrendsProvider, ValidationError

logger = logging.getLogger(__name__)


class MockProvider(TrendsProvider):
    """Mock provider that reads from fixture files."""

    def __init__(self, fixtures_path: Optional[str] = None):
        """
        Initialize mock provider.

        Args:
            fixtures_path: Path to fixtures directory
        """
        self.fixtures_path = Path(fixtures_path) if fixtures_path else Path("tests/fixtures")
        self._trending_data: dict[str, list[dict[str, Any]]] = {}
        self._hashtag_data: dict[str, list[dict[str, Any]]] = {}
        self._initialized = False

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "mock"

    @property
    def supported_regions(self) -> list[str]:
        """Get list of supported region codes."""
        return ["US", "GB", "CA", "AU", "DE", "FR", "JP", "BR", "IN", "KR"]

    async def initialize(self) -> bool:
        """Load fixture data."""
        if self._initialized:
            return True

        try:
            # Load trending fixtures
            trending_file = self.fixtures_path / "trending_sample.json"
            if trending_file.exists():
                with open(trending_file, encoding="utf-8") as f:
                    self._trending_data = json.load(f)
            else:
                logger.warning(f"Trending fixture file not found: {trending_file}")
                self._trending_data = self._generate_sample_trending()

            # Load hashtag fixtures
            hashtag_file = self.fixtures_path / "hashtag_sample.json"
            if hashtag_file.exists():
                with open(hashtag_file, encoding="utf-8") as f:
                    self._hashtag_data = json.load(f)
            else:
                logger.warning(f"Hashtag fixture file not found: {hashtag_file}")
                self._hashtag_data = self._generate_sample_hashtags()

            self._initialized = True
            logger.info("Mock provider initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize mock provider: {e}")
            return False

    async def fetch_trending(
        self,
        count: int = 30,
        region: str = "US",
        **kwargs,
    ) -> list[dict[str, Any]]:
        """Fetch trending content from fixtures."""
        if not self._initialized:
            if not await self.initialize():
                raise ProviderError("Failed to initialize mock provider")

        # Validate parameters
        if count < 1 or count > 60:
            raise ValidationError("Count must be between 1 and 60")

        if region not in self.supported_regions:
            logger.warning(f"Region {region} not in fixtures, using US data")
            region = "US"

        # Get trending data for region (fallback to US)
        region_data = self._trending_data.get(region, self._trending_data.get("US", []))

        # Return requested count
        result = region_data[:count] if len(region_data) >= count else region_data

        logger.info(f"Mock provider returned {len(result)} trending items for region {region}")
        return result

    async def fetch_hashtag_content(
        self,
        hashtag: str,
        count: int = 30,
        region: str = "US",
        **kwargs,
    ) -> list[dict[str, Any]]:
        """Fetch hashtag content from fixtures."""
        if not self._initialized:
            if not await self.initialize():
                raise ProviderError("Failed to initialize mock provider")

        # Validate parameters
        if count < 1 or count > 60:
            raise ValidationError("Count must be between 1 and 60")

        if not hashtag or not hashtag.strip():
            raise ValidationError("Hashtag cannot be empty")

        # Clean hashtag
        clean_hashtag = hashtag.strip().lower().lstrip("#")

        # Get hashtag data (fallback to generic data)
        hashtag_data = self._hashtag_data.get(clean_hashtag, self._hashtag_data.get("generic", []))

        # Return requested count
        result = hashtag_data[:count] if len(hashtag_data) >= count else hashtag_data
        logger.info(f"Mock provider returned {len(result)} items for hashtag #{clean_hashtag}")
        return result

    async def health_check(self) -> bool:
        """Check if the provider is healthy."""
        return self._initialized or await self.initialize()

    def _generate_sample_trending(self) -> dict[str, list[dict[str, Any]]]:
        """Generate sample trending data for demonstration."""
        base_time = int(datetime.now(timezone.utc).timestamp())

        sample_items = []
        for i in range(50):
            item = {
                "id": f"mock_trending_{i:03d}",
                "desc": f"Sample trending content item #{i+1}",
                "author": f"user_{i % 10 + 1}",
                "create_time": base_time - (i * 3600),  # Spread over hours
                "stats": {
                    "playCount": 1000000 - (i * 10000),
                    "diggCount": 50000 - (i * 500),
                    "commentCount": 2000 - (i * 20),
                    "shareCount": 1000 - (i * 10),
                },
                "music_title": f"Popular Song {i % 5 + 1}",
                "hashtags": ["trending", "popular", f"tag{i % 3 + 1}"],
                "video_url": None,  # No media URLs in compliance mode
                "cover": None,
            }
            sample_items.append(item)

        return {
            "US": sample_items,
            "GB": sample_items[:30],
            "CA": sample_items[:25],
            "AU": sample_items[:20],
        }

    def _generate_sample_hashtags(self) -> dict[str, list[dict[str, Any]]]:
        """Generate sample hashtag data for demonstration."""
        base_time = int(datetime.now(timezone.utc).timestamp())

        sample_items = []
        for i in range(30):
            item = {
                "id": f"mock_hashtag_{i:03d}",
                "desc": f"Sample hashtag content item #{i+1}",
                "author": f"creator_{i % 8 + 1}",
                "create_time": base_time - (i * 1800),  # Spread over 30 min intervals
                "stats": {
                    "playCount": 500000 - (i * 5000),
                    "diggCount": 25000 - (i * 250),
                    "commentCount": 1000 - (i * 10),
                    "shareCount": 500 - (i * 5),
                },
                "music_title": f"Trending Sound {i % 4 + 1}",
                "hashtags": ["viral", "fyp", "example"],
                "video_url": None,  # No media URLs in compliance mode
                "cover": None,
            }
            sample_items.append(item)

        return {
            "trending": sample_items,
            "viral": sample_items[:20],
            "fyp": sample_items[:25],
            "generic": sample_items[:15],
        }
