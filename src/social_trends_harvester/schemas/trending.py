"""Platform-agnostic data transfer objects for social media content."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ContentStats(BaseModel):
    """Statistics for social media content."""

    view_count: int = Field(default=0, description="Number of views/plays", ge=0)
    like_count: int = Field(default=0, description="Number of likes/reactions", ge=0)
    comment_count: int = Field(default=0, description="Number of comments", ge=0)
    share_count: int = Field(default=0, description="Number of shares/reposts", ge=0)

    # Legacy compatibility fields (deprecated)
    playCount: Optional[int] = Field(default=None, description="Legacy: use view_count")
    diggCount: Optional[int] = Field(default=None, description="Legacy: use like_count")

    def __init__(self, **data):
        """Initialize with backward compatibility."""
        # Handle legacy field names
        if "playCount" in data and "view_count" not in data:
            data["view_count"] = data["playCount"]
        if "diggCount" in data and "like_count" not in data:
            data["like_count"] = data["diggCount"]
        if "commentCount" in data and "comment_count" not in data:
            data["comment_count"] = data["commentCount"]
        if "shareCount" in data and "share_count" not in data:
            data["share_count"] = data["shareCount"]

        super().__init__(**data)


class ContentItem(BaseModel):
    """Normalized social media content item."""

    id: str = Field(..., description="Unique content identifier")
    title: Optional[str] = Field(default=None, description="Content title")
    description: Optional[str] = Field(default=None, description="Content description/caption")
    author: Optional[str] = Field(default=None, description="Content author/creator")
    author_id: Optional[str] = Field(default=None, description="Author unique identifier")
    created_at: int = Field(default=0, description="Creation timestamp (Unix)", ge=0)
    updated_at: Optional[int] = Field(
        default=None, description="Last update timestamp (Unix)", ge=0
    )

    # Engagement metrics
    stats: ContentStats = Field(default_factory=ContentStats, description="Content statistics")

    # Content classification
    hashtags: list[str] = Field(default_factory=list, description="Associated hashtags")
    mentions: list[str] = Field(default_factory=list, description="User mentions")
    category: Optional[str] = Field(default=None, description="Content category")
    language: Optional[str] = Field(default=None, description="Content language code")

    # Media information (metadata only, no URLs in compliance mode)
    media_type: Optional[str] = Field(default=None, description="Media type (video, image, text)")
    duration: Optional[int] = Field(default=None, description="Media duration in seconds", ge=0)
    dimensions: Optional[dict[str, int]] = Field(
        default=None, description="Media dimensions (width, height)"
    )

    # Audio/Music information
    audio_title: Optional[str] = Field(default=None, description="Background audio/music title")
    audio_artist: Optional[str] = Field(default=None, description="Audio artist")

    # Platform-specific metadata
    platform: Optional[str] = Field(default=None, description="Source platform")
    platform_specific: dict[str, Any] = Field(
        default_factory=dict, description="Platform-specific data"
    )

    # Compliance fields (no media URLs)
    media_url: Optional[str] = Field(
        default=None, description="Media URL (excluded in compliance mode)"
    )
    thumbnail_url: Optional[str] = Field(
        default=None, description="Thumbnail URL (excluded in compliance mode)"
    )

    # Legacy compatibility fields (deprecated)
    desc: Optional[str] = Field(default=None, description="Legacy: use description")
    create_time: Optional[int] = Field(default=None, description="Legacy: use created_at")
    music_title: Optional[str] = Field(default=None, description="Legacy: use audio_title")
    video_url: Optional[str] = Field(
        default=None, description="Legacy: excluded in compliance mode"
    )
    cover: Optional[str] = Field(default=None, description="Legacy: excluded in compliance mode")

    def __init__(self, **data):
        """Initialize with backward compatibility."""
        # Handle legacy field names
        if "desc" in data and "description" not in data:
            data["description"] = data["desc"]
        if "create_time" in data and "created_at" not in data:
            data["created_at"] = data["create_time"]
        if "music_title" in data and "audio_title" not in data:
            data["audio_title"] = data["music_title"]

        # Ensure compliance mode (no media URLs)
        data["media_url"] = None
        data["thumbnail_url"] = None
        data["video_url"] = None
        data["cover"] = None

        super().__init__(**data)


class TrendingResponse(BaseModel):
    """Response model for trending content."""

    items: list[ContentItem] = Field(..., description="List of trending content items")
    total: int = Field(..., description="Total number of items returned", ge=0)
    region: str = Field(..., description="Region code (ISO 3166-1 alpha-2)")
    provider: str = Field(..., description="Data provider name")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()), description="Response timestamp"
    )

    # Pagination support
    has_more: bool = Field(default=False, description="Whether more items are available")
    next_cursor: Optional[str] = Field(default=None, description="Cursor for next page")


class HashtagResponse(BaseModel):
    """Response model for hashtag-based content."""

    items: list[ContentItem] = Field(..., description="List of hashtag content items")
    total: int = Field(..., description="Total number of items returned", ge=0)
    hashtag: str = Field(..., description="Searched hashtag (without # prefix)")
    region: str = Field(..., description="Region code (ISO 3166-1 alpha-2)")
    provider: str = Field(..., description="Data provider name")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()), description="Response timestamp"
    )

    # Pagination support
    has_more: bool = Field(default=False, description="Whether more items are available")
    next_cursor: Optional[str] = Field(default=None, description="Cursor for next page")


class ProviderInfo(BaseModel):
    """Information about a data provider."""

    name: str = Field(..., description="Provider name")
    supported_regions: list[str] = Field(..., description="Supported region codes")
    supported_features: list[str] = Field(
        ..., description="Supported features (trending, hashtag, etc.)"
    )
    rate_limits: dict[str, int] = Field(default_factory=dict, description="Rate limits by feature")
    compliance_level: str = Field(
        default="standard", description="Compliance level (strict, standard, permissive)"
    )


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(default="ok", description="Service status (ok, degraded, error)")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()),
        description="Health check timestamp",
    )
    providers: dict[str, bool] = Field(default_factory=dict, description="Provider health status")
    cache_status: Optional[dict[str, Any]] = Field(default=None, description="Cache system status")
    compliance_status: Optional[dict[str, Any]] = Field(
        default=None, description="Compliance system status"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Machine-readable error code")
    http_status: int = Field(..., description="HTTP status code", ge=100, le=599)
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()), description="Error timestamp"
    )
    request_id: Optional[str] = Field(default=None, description="Request identifier for tracing")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional error details")


class ComplianceInfo(BaseModel):
    """Compliance information and guidelines."""

    robots_txt_respected: bool = Field(default=True, description="Whether robots.txt is respected")
    rate_limiting_enabled: bool = Field(
        default=True, description="Whether rate limiting is enabled"
    )
    user_agent: str = Field(..., description="User agent string used for requests")
    supported_protocols: list[str] = Field(default=["https"], description="Supported protocols")
    data_retention_policy: Optional[str] = Field(default=None, description="Data retention policy")

    guidelines: dict[str, str] = Field(
        default_factory=lambda: {
            "usage": "Use only with authorized data sources",
            "rate_limits": "Respect all rate limits and robots.txt directives",
            "content": "No media downloads - metadata only",
            "legal": "Users responsible for compliance with applicable laws and ToS",
        },
        description="Compliance guidelines",
    )


# Legacy compatibility - map old names to new classes
TrendItem = ContentItem  # For backward compatibility
VideoStats = ContentStats  # For backward compatibility
