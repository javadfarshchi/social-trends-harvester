"""Configuration settings for Social Trends Harvester."""

import os
from typing import Optional


class Settings:
    """Application settings."""

    # Service Configuration
    SERVICE_NAME: str = "Social Trends Harvester"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")  # nosec B104 - intentional binding to all interfaces
    PORT: int = int(os.getenv("PORT", "8000"))

    # Cache Configuration
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    CACHE_TTL_S: int = int(os.getenv("CACHE_TTL_S", "300"))

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))

    # Request Configuration
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Data Paths
    FIXTURES_PATH: str = os.getenv("FIXTURES_PATH", "data/fixtures")
    HAR_DATA_PATH: str = os.getenv("HAR_DATA_PATH", "data/har")

    # API Configuration
    DEFAULT_REGION: str = "US"
    DEFAULT_COUNT: int = 30
    MAX_COUNT: int = 60

    # Compliance
    RESPECT_ROBOTS_TXT: bool = True
    ETHICAL_USER_AGENT: str = (
        "SocialTrendsHarvester/1.0 (+https://github.com/javadfarshchi/social-trends-harvester)"
    )


# Global settings instance
settings = Settings()
