#!/bin/bash
# Testing script for Social Trends Harvester

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
COVERAGE=true
VERBOSE=false
PATTERN=""

# Help function
show_help() {
    echo "Social Trends Harvester Testing Helper"
    echo
    echo "Usage: $0 [OPTIONS] [PATTERN]"
    echo
    echo "Options:"
    echo "  --no-coverage       Skip coverage reporting"
    echo "  -v, --verbose       Verbose output"
    echo "  --help              Show this help message"
    echo
    echo "Arguments:"
    echo "  PATTERN             Test pattern to match (optional)"
    echo
    echo "Examples:"
    echo "  $0                  Run all tests with coverage"
    echo "  $0 --verbose        Run tests with verbose output"
    echo "  $0 test_providers   Run only provider tests"
    echo "  $0 --no-coverage    Run tests without coverage"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            show_help
            exit 1
            ;;
        *)
            PATTERN="$1"
            shift
            ;;
    esac
done

echo -e "${GREEN}🧪 Running Social Trends Harvester Tests${NC}"
echo

# Resolve Python interpreter
find_python() {
    if command -v python3 >/dev/null 2>&1; then echo python3; return; fi
    if command -v python >/dev/null 2>&1; then echo python; return; fi
    echo ""
}

PYCMD=$(find_python)
if [[ -z "$PYCMD" ]]; then
    echo -e "${RED}❌ Python interpreter not found. Please install Python 3.x and retry.${NC}"
    exit 1
fi

# Check if test dependencies are installed (pytest and pytest-asyncio)
"$PYCMD" - <<'PY'
import sys
try:
    import pytest  # noqa: F401
    import pytest_asyncio  # noqa: F401
except Exception:
    sys.exit(1)
sys.exit(0)
PY

if [[ $? -ne 0 ]]; then
    echo -e "${YELLOW}⚠️  Test dependencies not found. Installing dev extras...${NC}"
    "$PYCMD" -m pip install -e ".[dev]"
    echo
fi

# Build pytest command
pytest_cmd="$PYCMD -m pytest"

# Add test directory
pytest_cmd="$pytest_cmd tests/"

# Add pattern if specified
if [[ -n "$PATTERN" ]]; then
    pytest_cmd="$pytest_cmd -k $PATTERN"
    echo -e "${YELLOW}🎯 Running tests matching pattern: $PATTERN${NC}"
fi

# Add verbose flag
if [[ "$VERBOSE" == "true" ]]; then
    pytest_cmd="$pytest_cmd -v"
fi

# Add coverage if enabled
if [[ "$COVERAGE" == "true" ]]; then
    pytest_cmd="$pytest_cmd --cov=src/social_trends_harvester --cov-report=term-missing --cov-report=html"
    echo -e "${YELLOW}📊 Coverage reporting enabled${NC}"
fi

# Run tests
echo -e "${GREEN}🏃 Running tests...${NC}"
echo "Command: $pytest_cmd"
echo

if eval "$pytest_cmd"; then
    echo
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    
    if [[ "$COVERAGE" == "true" ]]; then
        echo -e "${GREEN}📊 Coverage report generated in htmlcov/index.html${NC}"
    fi
    
    exit 0
else
    echo
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
