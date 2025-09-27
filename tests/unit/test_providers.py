"""Tests for provider adapters."""


import pytest
import pytest_asyncio

from social_trends_harvester.providers.base import ProviderError, TrendsProvider, ValidationError
from social_trends_harvester.providers.har import HARProvider
from social_trends_harvester.providers.mock import MockProvider


class TestMockProvider:
    """Test suite for MockProvider."""

    @pytest_asyncio.fixture
    async def mock_provider(self):
        """Create a mock provider instance."""
        provider = MockProvider()
        await provider.initialize()
        return provider

    @pytest.mark.asyncio
    async def test_provider_properties(self):
        """Test provider property methods."""
        provider = MockProvider()
        await provider.initialize()
        assert provider.provider_name == "mock"
        assert isinstance(provider.supported_regions, list)
        assert "US" in provider.supported_regions
        assert "GB" in provider.supported_regions

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test provider initialization."""
        provider = MockProvider()
        result = await provider.initialize()
        assert result is True
        assert provider._initialized is True

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check functionality."""
        provider = MockProvider()
        await provider.initialize()
        result = await provider.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_fetch_trending_success(self):
        """Test successful trending fetch."""
        provider = MockProvider()
        await provider.initialize()
        result = await provider.fetch_trending(count=5, region="US")

        assert isinstance(result, list)
        assert len(result) <= 5
        assert len(result) > 0

        # Check structure of first item
        item = result[0]
        assert "id" in item
        assert "description" in item or "desc" in item
        assert "author" in item
        assert "stats" in item
        assert "hashtags" in item

    @pytest.mark.asyncio
    async def test_fetch_trending_validation(self, mock_provider):
        """Test trending fetch input validation."""
        # Test invalid count
        with pytest.raises(ValidationError):
            await mock_provider.fetch_trending(count=0)

        with pytest.raises(ValidationError):
            await mock_provider.fetch_trending(count=100)

        # Test unsupported region (should fallback, not error)
        result = await mock_provider.fetch_trending(count=5, region="XX")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_hashtag_success(self, mock_provider):
        """Test successful hashtag fetch."""
        result = await mock_provider.fetch_hashtag_content(
            hashtag="trending", count=5, region="US"
        )

        assert isinstance(result, list)
        assert len(result) <= 5
        assert len(result) > 0

        # Check structure
        item = result[0]
        assert "id" in item
        assert "hashtags" in item

    @pytest.mark.asyncio
    async def test_fetch_hashtag_validation(self, mock_provider):
        """Test hashtag fetch input validation."""
        # Test invalid count
        with pytest.raises(ValidationError):
            await mock_provider.fetch_hashtag_content(hashtag="test", count=0)

        # Test empty hashtag
        with pytest.raises(ValidationError):
            await mock_provider.fetch_hashtag_content(hashtag="", count=5)

        with pytest.raises(ValidationError):
            await mock_provider.fetch_hashtag_content(hashtag="   ", count=5)

    @pytest.mark.asyncio
    async def test_fetch_unknown_hashtag(self, mock_provider):
        """Test fetching unknown hashtag returns generic data."""
        result = await mock_provider.fetch_hashtag_content(
            hashtag="nonexistent_hashtag", count=5
        )

        assert isinstance(result, list)
        # Should return generic data or empty list


class TestHARProvider:
    """Test suite for HARProvider."""

    @pytest.fixture
    def har_provider(self):
        """Create a HAR provider instance with test directory."""
        return HARProvider(har_directory="test_har_data")

    def test_provider_properties(self, har_provider):
        """Test provider property methods."""
        assert har_provider.provider_name == "har"
        # Supported regions depend on HAR data
        assert isinstance(har_provider.supported_regions, list)

    @pytest.mark.asyncio
    async def test_initialization_no_directory(self, har_provider):
        """Test initialization when HAR directory doesn't exist."""
        result = await har_provider.initialize()
        assert result is False
        assert har_provider._initialized is False

    @pytest.mark.asyncio
    async def test_health_check_uninitialized(self, har_provider):
        """Test health check on uninitialized provider."""
        result = await har_provider.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_fetch_without_initialization(self, har_provider):
        """Test fetch operations without proper initialization."""
        with pytest.raises(ProviderError):
            await har_provider.fetch_trending(count=5)

        with pytest.raises(ProviderError):
            await har_provider.fetch_hashtag_content(hashtag="test", count=5)

    @pytest.mark.asyncio
    async def test_fetch_validation(self, har_provider):
        """Test input validation."""
        # Mock initialization to succeed
        har_provider._initialized = True
        har_provider._parsed_data = {"trending": {}, "hashtags": {}, "regions": {}}

        # Test invalid count
        with pytest.raises(ValidationError):
            await har_provider.fetch_trending(count=0)

        with pytest.raises(ValidationError):
            await har_provider.fetch_hashtag_content(hashtag="test", count=100)

        # Test empty hashtag
        with pytest.raises(ValidationError):
            await har_provider.fetch_hashtag_content(hashtag="", count=5)


class TestBaseProvider:
    """Test suite for base provider functionality."""

    def test_abstract_methods(self):
        """Test that abstract methods cannot be instantiated."""
        with pytest.raises(TypeError):
            TrendsProvider()

    def test_provider_interface(self):
        """Test that the provider interface is properly defined."""
        # Check that required methods exist
        assert hasattr(TrendsProvider, 'fetch_trending')
        assert hasattr(TrendsProvider, 'fetch_hashtag_content')
        assert hasattr(TrendsProvider, 'health_check')
        assert hasattr(TrendsProvider, 'provider_name')
        assert hasattr(TrendsProvider, 'supported_regions')


@pytest.mark.asyncio
async def test_provider_cleanup():
    """Test provider cleanup functionality."""
    provider = MockProvider()
    await provider.initialize()

    # Should not raise an error
    await provider.cleanup()


@pytest.mark.asyncio
async def test_provider_double_initialization():
    """Test that double initialization is handled properly."""
    provider = MockProvider()

    result1 = await provider.initialize()
    result2 = await provider.initialize()

    assert result1 is True
    assert result2 is True
    assert provider._initialized is True
