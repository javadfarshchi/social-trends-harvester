#!/bin/bash
# Docker container test script that properly exits

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="social-trends-harvester"
CONTAINER_NAME="sth-test"
PORT=8004

echo -e "${GREEN}🐳 Testing Docker Container - GitHub Native Structure${NC}"
echo

# Function to cleanup
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set trap for cleanup
trap cleanup EXIT

# Step 1: Build Docker image
echo -e "${YELLOW}📦 Step 1: Building Docker image...${NC}"
if docker build -f docker/Dockerfile -t $IMAGE_NAME . --quiet; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi
echo

# Step 2: Run container
echo -e "${YELLOW}🚀 Step 2: Starting container...${NC}"
if docker run -d --name $CONTAINER_NAME -p $PORT:8000 $IMAGE_NAME > /dev/null; then
    echo -e "${GREEN}✅ Container started on port $PORT${NC}"
else
    echo -e "${RED}❌ Container failed to start${NC}"
    exit 1
fi

# Wait for container to be ready
echo -e "${YELLOW}⏳ Waiting for container to be ready...${NC}"
sleep 10

# Step 3: Test APIs one by one
echo -e "${YELLOW}🧪 Step 3: Testing APIs...${NC}"

BASE_URL="http://localhost:$PORT"
TESTS=(
    "health:$BASE_URL/api/v1/healthz"
    "root:$BASE_URL/"
    "trending:$BASE_URL/api/v1/trending?provider=mock&count=3"
    "hashtag:$BASE_URL/api/v1/hashtag/viral?provider=mock&count=2"
    "providers:$BASE_URL/api/v1/providers"
    "compliance:$BASE_URL/api/v1/compliance"
)

PASSED=0
TOTAL=${#TESTS[@]}

for test in "${TESTS[@]}"; do
    name=$(echo $test | cut -d: -f1)
    url=$(echo $test | cut -d: -f2-)
    
    echo -n "Testing $name... "
    
    if response=$(curl -s -w "%{http_code}" "$url" --connect-timeout 5 --max-time 10); then
        status_code="${response: -3}"
        if [ "$status_code" = "200" ]; then
            echo -e "${GREEN}✅ PASS${NC}"
            ((PASSED++))
        else
            echo -e "${RED}❌ FAIL (HTTP $status_code)${NC}"
        fi
    else
        echo -e "${RED}❌ FAIL (Connection error)${NC}"
    fi
done

echo
echo -e "${YELLOW}📊 Results: $PASSED/$TOTAL tests passed${NC}"

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Docker container is working perfectly!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
