"""Test configuration for Social Trends Harvester."""

import asyncio

# Add the project root to Python path
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_fixtures_path():
    """Path to test fixtures."""
    return Path(__file__).parent.parent / "data" / "fixtures"


@pytest.fixture
def test_har_path():
    """Path to test HAR data."""
    return Path(__file__).parent.parent / "data" / "har"
