#!/bin/bash
# Development helper script for Social Trends Harvester

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
PORT=8000
HOST="0.0.0.0"
RELOAD=true

# Help function
show_help() {
    echo "Social Trends Harvester Development Helper"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -p, --port PORT     Port to run on (default: 8000)"
    echo "  -h, --host HOST     Host to bind to (default: 0.0.0.0)"
    echo "  --no-reload         Disable auto-reload"
    echo "  --help              Show this help message"
    echo
    echo "Examples:"
    echo "  $0                  Run with defaults"
    echo "  $0 -p 8001          Run on port 8001"
    echo "  $0 --no-reload      Run without auto-reload"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        --no-reload)
            RELOAD=false
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

echo -e "${GREEN}🚀 Starting Social Trends Harvester Development Server${NC}"
echo -e "${YELLOW}Host: ${HOST}${NC}"
echo -e "${YELLOW}Port: ${PORT}${NC}"
echo -e "${YELLOW}Auto-reload: ${RELOAD}${NC}"
echo

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}⚠️  No virtual environment detected. Consider activating one.${NC}"
    echo
fi

# Check if dependencies are installed
if ! python -c "import social_trends_harvester" 2>/dev/null; then
    echo -e "${RED}❌ Package not installed. Installing in development mode...${NC}"
    pip install -e ".[dev]"
    echo
fi

# Start the server
echo -e "${GREEN}🎯 Starting server at http://${HOST}:${PORT}${NC}"
echo -e "${GREEN}📚 API docs available at http://${HOST}:${PORT}/docs${NC}"
echo -e "${GREEN}🔍 Health check: http://${HOST}:${PORT}/api/v1/healthz${NC}"
echo

if [[ "$RELOAD" == "true" ]]; then
    uvicorn social_trends_harvester.app:app --host "$HOST" --port "$PORT" --reload
else
    uvicorn social_trends_harvester.app:app --host "$HOST" --port "$PORT"
fi
