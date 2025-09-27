"""Compliance module for respecting robots.txt, rate limits, and ethical data access."""

import asyncio
import logging
import time
from typing import Dict
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx

logger = logging.getLogger(__name__)


class ComplianceManager:
    """Manager for compliance features including robots.txt and rate limiting."""

    def __init__(self):
        """Initialize compliance manager."""
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.user_agent = "SocialTrendsHarvester/1.0 (+https://github.com/javadfarshchi/social-trends-harvester)"
        self._request_session = None

    async def initialize(self):
        """Initialize the compliance manager."""
        self._request_session = httpx.AsyncClient(
            headers={"User-Agent": self.user_agent},
            timeout=httpx.Timeout(10.0)
        )
        logger.info("Compliance manager initialized")

    async def cleanup(self):
        """Cleanup resources."""
        if self._request_session:
            await self._request_session.aclose()
            self._request_session = None

    async def check_robots_permission(self, url: str, user_agent: str = "*") -> bool:
        """
        Check if the URL is allowed by robots.txt.
        
        Args:
            url: URL to check
            user_agent: User agent to check for (defaults to *)
            
        Returns:
            True if allowed, False if disallowed
        """
        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # Check cache first
            if domain not in self.robots_cache:
                await self._load_robots_txt(domain)

            robots_parser = self.robots_cache.get(domain)
            if robots_parser is None:
                # If we can't load robots.txt, be conservative
                logger.warning(f"Could not load robots.txt for {domain}, denying access")
                return False

            # Check if the URL is allowed
            is_allowed = robots_parser.can_fetch(user_agent, url)

            if not is_allowed:
                logger.info(f"Access denied by robots.txt for {url}")

            return is_allowed

        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            # Be conservative on error
            return False

    async def _load_robots_txt(self, domain: str):
        """Load and parse robots.txt for a domain."""
        try:
            robots_url = urljoin(domain, "/robots.txt")

            if not self._request_session:
                await self.initialize()

            response = await self._request_session.get(robots_url)

            robots_parser = RobotFileParser()
            robots_parser.set_url(robots_url)

            if response.status_code == 200:
                robots_content = response.text
                robots_parser.read_string(robots_content)
                logger.info(f"Loaded robots.txt for {domain}")
            else:
                # If robots.txt doesn't exist, assume everything is allowed
                robots_parser.read_string("")
                logger.info(f"No robots.txt found for {domain}, assuming allowed")

            self.robots_cache[domain] = robots_parser

        except Exception as e:
            logger.error(f"Failed to load robots.txt for {domain}: {e}")
            # Store None to indicate failure
            self.robots_cache[domain] = None

    def get_rate_limiter(self, domain: str, requests_per_minute: int = 10) -> 'RateLimiter':
        """
        Get or create a rate limiter for a domain.
        
        Args:
            domain: Domain to rate limit
            requests_per_minute: Maximum requests per minute
            
        Returns:
            RateLimiter instance
        """
        if domain not in self.rate_limiters:
            self.rate_limiters[domain] = RateLimiter(requests_per_minute)

        return self.rate_limiters[domain]

    async def respect_crawl_delay(self, domain: str) -> bool:
        """
        Check and respect crawl-delay from robots.txt.
        
        Args:
            domain: Domain to check
            
        Returns:
            True if delay was respected, False if robots.txt unavailable
        """
        try:
            if domain not in self.robots_cache:
                await self._load_robots_txt(domain)

            robots_parser = self.robots_cache.get(domain)
            if robots_parser is None:
                return False

            # Get crawl delay for our user agent
            crawl_delay = robots_parser.crawl_delay(self.user_agent)
            if crawl_delay is None:
                crawl_delay = robots_parser.crawl_delay("*")

            if crawl_delay is not None and crawl_delay > 0:
                logger.info(f"Respecting crawl-delay of {crawl_delay}s for {domain}")
                await asyncio.sleep(crawl_delay)

            return True

        except Exception as e:
            logger.error(f"Error respecting crawl delay for {domain}: {e}")
            return False


class RateLimiter:
    """Simple rate limiter with exponential backoff."""

    def __init__(self, requests_per_minute: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests: list = []
        self.backoff_until: float = 0
        self.consecutive_failures: int = 0

    def is_allowed(self) -> bool:
        """Check if a request is allowed."""
        now = time.time()

        # Check if we're in backoff period
        if now < self.backoff_until:
            return False

        # Clean old requests (older than 1 minute)
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]

        # Check if we can make a request
        return len(self.requests) < self.requests_per_minute

    def record_request(self):
        """Record a request."""
        self.requests.append(time.time())
        self.consecutive_failures = 0  # Reset on successful request

    def record_failure(self):
        """Record a failure and apply exponential backoff."""
        self.consecutive_failures += 1

        # Exponential backoff: 2^failures seconds, max 300 seconds (5 minutes)
        backoff_seconds = min(2 ** self.consecutive_failures, 300)
        self.backoff_until = time.time() + backoff_seconds

        logger.warning(f"Rate limiter applying backoff of {backoff_seconds}s after {self.consecutive_failures} failures")

    def time_until_reset(self) -> float:
        """Get time until rate limit resets."""
        now = time.time()

        # Check backoff first
        if now < self.backoff_until:
            return self.backoff_until - now

        # Check rate limit window
        if not self.requests:
            return 0

        oldest_request = min(self.requests)
        return max(0, 60 - (now - oldest_request))


class EthicalHeaders:
    """Generate ethical HTTP headers for requests."""

    @staticmethod
    def get_headers(respect_robots: bool = True) -> Dict[str, str]:
        """
        Get ethical HTTP headers.
        
        Args:
            respect_robots: Whether this client respects robots.txt
            
        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "User-Agent": "SocialTrendsHarvester/1.0 (+https://github.com/javadfarshchi/social-trends-harvester)",
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",  # Do Not Track
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        if respect_robots:
            headers["X-Robots-Tag"] = "noarchive,nofollow"

        return headers


# Global compliance manager instance
compliance_manager = ComplianceManager()


async def check_url_compliance(url: str) -> bool:
    """
    Check if accessing a URL is compliant.
    
    Args:
        url: URL to check
        
    Returns:
        True if compliant, False otherwise
    """
    try:
        # Initialize if needed
        if compliance_manager._request_session is None:
            await compliance_manager.initialize()

        # Check robots.txt
        robots_allowed = await compliance_manager.check_robots_permission(url)
        if not robots_allowed:
            return False

        # Check rate limiting
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        rate_limiter = compliance_manager.get_rate_limiter(domain)

        if not rate_limiter.is_allowed():
            logger.info(f"Rate limit exceeded for {domain}")
            return False

        # Respect crawl delay
        await compliance_manager.respect_crawl_delay(domain)

        return True

    except Exception as e:
        logger.error(f"Error checking compliance for {url}: {e}")
        return False


async def record_request_metrics(url: str, success: bool = True):
    """
    Record request metrics for compliance tracking.
    
    Args:
        url: URL that was accessed
        success: Whether the request was successful
    """
    try:
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        rate_limiter = compliance_manager.get_rate_limiter(domain)

        if success:
            rate_limiter.record_request()
        else:
            rate_limiter.record_failure()

    except Exception as e:
        logger.error(f"Error recording request metrics: {e}")
