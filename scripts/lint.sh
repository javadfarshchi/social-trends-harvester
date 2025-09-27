#!/bin/bash
# Linting and formatting script for Social Trends Harvester

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
FIX=false
CHECK_ONLY=false

# Help function
show_help() {
    echo "Social Trends Harvester Linting Helper"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --fix               Auto-fix issues where possible"
    echo "  --check-only        Only check, don't make changes"
    echo "  --help              Show this help message"
    echo
    echo "Examples:"
    echo "  $0                  Run all linting checks"
    echo "  $0 --fix            Run checks and fix issues"
    echo "  $0 --check-only     Only check without fixing"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX=true
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            show_help
            exit 1
            ;;
    esac
done

echo -e "${GREEN}🔍 Running Social Trends Harvester Code Quality Checks${NC}"
echo

# Check if development dependencies are installed
if ! python -c "import ruff, black, isort, mypy" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Development dependencies not found. Installing...${NC}"
    pip install -e ".[dev]"
    echo
fi

# Function to run a command and capture its output
run_check() {
    local name="$1"
    local cmd="$2"
    
    echo -e "${YELLOW}Running $name...${NC}"
    
    if eval "$cmd"; then
        echo -e "${GREEN}✅ $name passed${NC}"
        return 0
    else
        echo -e "${RED}❌ $name failed${NC}"
        return 1
    fi
}

# Initialize error counter
errors=0

# 1. Ruff (Python linting)
echo -e "${GREEN}🐍 Python Linting with Ruff${NC}"
if [[ "$FIX" == "true" ]]; then
    if ! run_check "Ruff (auto-fix)" "ruff check src/ tests/ --fix"; then
        ((errors++))
    fi
else
    if ! run_check "Ruff" "ruff check src/ tests/"; then
        ((errors++))
    fi
fi
echo

# 2. Black (Code formatting)
echo -e "${GREEN}🎨 Code Formatting with Black${NC}"
if [[ "$CHECK_ONLY" == "true" ]]; then
    if ! run_check "Black (check only)" "black --check src/ tests/"; then
        ((errors++))
    fi
elif [[ "$FIX" == "true" ]]; then
    if ! run_check "Black (format)" "black src/ tests/"; then
        ((errors++))
    fi
else
    if ! run_check "Black (check)" "black --check src/ tests/"; then
        ((errors++))
    fi
fi
echo

# 3. isort (Import sorting)
echo -e "${GREEN}📦 Import Sorting with isort${NC}"
if [[ "$CHECK_ONLY" == "true" ]]; then
    if ! run_check "isort (check only)" "isort --check-only src/ tests/"; then
        ((errors++))
    fi
elif [[ "$FIX" == "true" ]]; then
    if ! run_check "isort (sort)" "isort src/ tests/"; then
        ((errors++))
    fi
else
    if ! run_check "isort (check)" "isort --check-only src/ tests/"; then
        ((errors++))
    fi
fi
echo

# 4. MyPy (Type checking)
echo -e "${GREEN}🔍 Type Checking with MyPy${NC}"
if ! run_check "MyPy" "mypy src/ --ignore-missing-imports"; then
    ((errors++))
fi
echo

# Summary
echo -e "${GREEN}📊 Summary${NC}"
if [[ $errors -eq 0 ]]; then
    echo -e "${GREEN}🎉 All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $errors check(s) failed${NC}"
    echo
    if [[ "$FIX" != "true" && "$CHECK_ONLY" != "true" ]]; then
        echo -e "${YELLOW}💡 Tip: Run with --fix to automatically fix some issues${NC}"
    fi
    exit 1
fi
