#!/bin/bash
# Example cURL commands for Social Trends Harvester API

# Allow overriding BASE_URL via environment variable. Defaults to localhost:8000
BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "=== Social Trends Harvester API Examples ==="
echo

echo "1. Health Check:"
curl -s "${BASE_URL}/api/v1/healthz" | python3 -m json.tool
echo

echo "2. Get Trending Content (Mock Provider):"
curl -s "${BASE_URL}/api/v1/trending?provider=mock&region=US&count=5" | python3 -m json.tool
echo

echo "3. Get Hashtag Content:"
curl -s "${BASE_URL}/api/v1/hashtag/trending?provider=mock&region=US&count=3" | python3 -m json.tool
echo

echo "4. List Available Providers:"
curl -s "${BASE_URL}/api/v1/providers" | python3 -m json.tool
echo

echo "5. Get Compliance Information:"
curl -s "${BASE_URL}/api/v1/compliance" | python3 -m json.tool
echo

echo "6. Cache Statistics:"
curl -s "${BASE_URL}/api/v1/cache/stats" | python3 -m json.tool
echo

echo "7. Different Regions:"
echo "US Trending:"
curl -s "${BASE_URL}/api/v1/trending?provider=mock&region=US&count=2" | python3 -c "import sys,json; data=json.load(sys.stdin); print(f'Region: {data[\"region\"]}, Items: {len(data[\"items\"])}')"

echo "GB Trending:"  
curl -s "${BASE_URL}/api/v1/trending?provider=mock&region=GB&count=2" | python3 -c "import sys,json; data=json.load(sys.stdin); print(f'Region: {data[\"region\"]}, Items: {len(data[\"items\"])}')"

echo "CA Trending:"
curl -s "${BASE_URL}/api/v1/trending?provider=mock&region=CA&count=2" | python3 -c "import sys,json; data=json.load(sys.stdin); print(f'Region: {data[\"region\"]}, Items: {len(data[\"items\"])}')"
echo

echo "8. Error Handling Examples:"
echo "Invalid count (should return 400):"
curl -s "${BASE_URL}/api/v1/trending?provider=mock&count=0" | python3 -c "import sys,json; data=json.load(sys.stdin); print(f'Error: {data.get(\"detail\", \"Unknown error\")}')"

echo "Invalid provider (should return 400):"
curl -s "${BASE_URL}/api/v1/trending?provider=nonexistent&count=5" | python3 -c "import sys,json; data=json.load(sys.stdin); print(f'Error: {data.get(\"detail\", \"Unknown error\")}')"

echo
echo "=== Done ==="
