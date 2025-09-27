"""HAR file provider for user-provided data exports."""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import ProviderError, ValidationError

logger = logging.getLogger(__name__)


class HARProvider(TrendsProvider):
    {{ ... }}

    async def fetch_trending(
        self,
        count: int = 30,
        region: str = "US",
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Fetch trending content from HAR data."""
        if not self._initialized:
            if not await self.initialize():
                raise ProviderError("Failed to initialize HAR provider")

    {{ ... }}
    async def fetch_hashtag_content(
        self,
        hashtag: str,
        count: int = 30,
        region: str = "US",
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Fetch hashtag content from HAR data."""
        if not self._initialized:
            if not await self.initialize():
                raise ProviderError("Failed to initialize HAR provider")
        # Validate parameters
        if count < 1 or count > 60:
            raise ValidationError("Count must be between 1 and 60")

        if not hashtag or not hashtag.strip():
            raise ValidationError("Hashtag cannot be empty")

        # Clean hashtag
        clean_hashtag = hashtag.strip().lower().lstrip('#')

        # Get hashtag data
        hashtag_data = self._parsed_data["hashtags"].get(clean_hashtag, [])

        if not hashtag_data:
            logger.warning(f"No data available for hashtag #{clean_hashtag} in HAR files")
            return []

        # Return requested count
        result = hashtag_data[:count] if len(hashtag_data) >= count else hashtag_data

        logger.info(f"HAR provider returned {len(result)} items for hashtag #{clean_hashtag}")
        return result

    async def health_check(self) -> bool:
        """Check if the provider is healthy."""
        return self._initialized or await self.initialize()

    async def _parse_har_file(self, har_file: Path):
        """Parse a single HAR file and extract social media data."""
        try:
            with open(har_file, encoding='utf-8') as f:
                har_data = json.load(f)

            entries = har_data.get("log", {}).get("entries", [])

            for entry in entries:
                request = entry.get("request", {})
                response = entry.get("response", {})

                # Skip non-JSON responses
                content_type = response.get("content", {}).get("mimeType", "")
                if "json" not in content_type:
                    continue

                # Extract URL and response content
                url = request.get("url", "")
                response_text = response.get("content", {}).get("text", "")

                if not response_text:
                    continue

                # Try to parse JSON response
                try:
                    response_data = json.loads(response_text)
                    await self._extract_content_from_response(url, response_data)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

        except Exception as e:
            logger.warning(f"Failed to parse HAR file {har_file}: {e}")

    async def _extract_content_from_response(self, url: str, response_data: dict[str, Any]):
        """Extract content items from API response data."""
        try:
            # Look for common patterns in social media API responses
            items = []

            # Common data structures in social media APIs
            if isinstance(response_data, dict):
                # Try various common keys for content arrays
                for key in ["data", "items", "results", "videos", "posts", "content"]:
                    if key in response_data and isinstance(response_data[key], list):
                        items = response_data[key]
                        break

                # Single item responses
                if not items and "id" in response_data:
                    items = [response_data]

            elif isinstance(response_data, list):
                items = response_data

            # Normalize each item
            normalized_items = []
            for item in items:
                if isinstance(item, dict):
                    normalized_item = self._normalize_item(item)
                    if normalized_item:
                        normalized_items.append(normalized_item)

            # Categorize based on URL patterns
            if "trending" in url.lower() or "trend" in url.lower():
                region = self._extract_region_from_url(url)
                if region not in self._parsed_data["trending"]:
                    self._parsed_data["trending"][region] = []
                self._parsed_data["trending"][region].extend(normalized_items)
                self._parsed_data["regions"][region] = True

            elif "hashtag" in url.lower() or "tag" in url.lower():
                hashtag = self._extract_hashtag_from_url(url)
                if hashtag:
                    if hashtag not in self._parsed_data["hashtags"]:
                        self._parsed_data["hashtags"][hashtag] = []
                    self._parsed_data["hashtags"][hashtag].extend(normalized_items)

        except Exception as e:
            logger.warning(f"Failed to extract content from response: {e}")

    def _normalize_item(self, item: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Normalize a content item to standard format."""
        try:
            # Extract common fields with fallbacks
            normalized = {
                "id": str(item.get("id", item.get("videoId", item.get("postId", "unknown")))),
                "desc": item.get("desc", item.get("description", item.get("caption", ""))),
                "author": item.get("author", item.get("username", item.get("user", {}).get("username", ""))),
                "create_time": self._parse_timestamp(item.get("create_time", item.get("createdAt", item.get("timestamp", 0)))),
                "stats": {
                    "playCount": int(item.get("stats", {}).get("playCount", item.get("viewCount", 0))),
                    "diggCount": int(item.get("stats", {}).get("diggCount", item.get("likeCount", 0))),
                    "commentCount": int(item.get("stats", {}).get("commentCount", item.get("commentCount", 0))),
                    "shareCount": int(item.get("stats", {}).get("shareCount", item.get("shareCount", 0)))
                },
                "music_title": item.get("music", {}).get("title", item.get("audio", {}).get("title", "")),
                "hashtags": self._extract_hashtags(item),
                "video_url": None,  # Exclude media URLs for compliance
                "cover": None
            }

            return normalized

        except Exception as e:
            logger.warning(f"Failed to normalize item: {e}")
            return None

    def _parse_timestamp(self, timestamp) -> int:
        """Parse various timestamp formats to Unix timestamp."""
        if isinstance(timestamp, int):
            # Handle both seconds and milliseconds
            if timestamp > 1e10:  # Milliseconds
                return int(timestamp / 1000)
            return timestamp

        if isinstance(timestamp, str):
            try:
                # Try parsing ISO format
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return int(dt.timestamp())
            except Exception:
                pass

        return int(datetime.now().timestamp())

    def _extract_hashtags(self, item: dict[str, Any]) -> list[str]:
        """Extract hashtags from various fields."""
        hashtags = []

        # Direct hashtags field
        if "hashtags" in item and isinstance(item["hashtags"], list):
            hashtags.extend([tag.strip('#').lower() for tag in item["hashtags"] if isinstance(tag, str)])

        # Extract from description
        desc = item.get("desc", item.get("description", item.get("caption", "")))
        if isinstance(desc, str):
            found_tags = re.findall(r'#(\w+)', desc)
            hashtags.extend([tag.lower() for tag in found_tags])

        return list(set(hashtags))  # Remove duplicates

    def _extract_region_from_url(self, url: str) -> str:
        """Extract region code from URL parameters."""
        # Look for common region parameters
        region_patterns = [
            r'region=([A-Z]{2})',
            r'country=([A-Z]{2})',
            r'locale=([A-Z]{2})'
        ]

        for pattern in region_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        return "US"  # Default region

    def _extract_hashtag_from_url(self, url: str) -> Optional[str]:
        """Extract hashtag from URL path or parameters."""
        # Look for hashtag in URL path or parameters
        hashtag_patterns = [
            r'/hashtag/([^/\?&]+)',
            r'/tag/([^/\?&]+)',
            r'[?&]tag=([^&]+)',
            r'[?&]hashtag=([^&]+)'
        ]

        for pattern in hashtag_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1).lower().lstrip('#')

        return None
