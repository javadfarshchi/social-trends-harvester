# Social Trends Harvester

A platform-agnostic FastAPI service for harvesting social media trends data with built-in compliance features. Designed as a general-purpose framework that respects robots.txt, implements rate limiting, and provides interfaces for legitimate data access.

## 🚨 Important Legal Notice

**This is a general-purpose tooling framework. Users are responsible for ensuring compliance with applicable laws and platform terms of service.** 

⚠️ **Many social media platforms, including TikTok, prohibit automated access in their Terms of Service. This tool does NOT provide methods to bypass access controls or violate platform policies.**

See [LEGAL_CONSIDERATIONS.md](LEGAL_CONSIDERATIONS.md) for detailed compliance guidance.

## Features

- **Platform-Agnostic**: Generic interface for social media trends data
- **Compliance-First**: Built-in robots.txt respect, rate limiting, and ethical headers
- **Multiple Providers**: Mock provider for testing, HAR provider for user data
- **Trending Content**: Fetch trending content items by region
- **Hashtag Search**: Get content for specific hashtags/topics
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Health Checks**: Health monitoring endpoints for all providers
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## API Endpoints

### Health Check
```
GET /healthz
```
Returns service health status.

### Trending Content
```
GET /trending?provider=mock&region=US&count=30
```
- `provider`: Data provider to use (mock, har)
- `region`: Region code (ISO 3166-1 alpha-2, default: US)
- `count`: Number of items (1-60, default: 30)

### Hashtag Content
```
GET /hashtag/{tag}?provider=mock&region=US&count=30
```
- `tag`: Hashtag to search (without # prefix)
- `provider`: Data provider to use (mock, har)
- `region`: Region code (ISO 3166-1 alpha-2, default: US)
- `count`: Number of items (1-60, default: 30)

### Provider Information
```
GET /providers            # List available providers
GET /compliance           # Compliance information
```

### Utility Endpoints
```
GET /cache/stats          # Cache statistics (disabled in this version)
DELETE /cache/clear       # Clear cache (disabled in this version)
GET /                     # API information
GET /docs                 # Interactive API documentation
GET /redoc                # Alternative API documentation
```

## Response Format

All content endpoints return a structured JSON response:

### Trending Response
```json
{
  "items": [
    {
      "id": "content_123",
      "description": "Content description",
      "author": "username",
      "created_at": 1699920000,
      "stats": {
        "view_count": 1234567,
        "like_count": 54321,
        "comment_count": 987,
        "share_count": 321
      },
      "hashtags": ["trending", "viral"],
      "category": "entertainment",
      "language": "en",
      "media_type": "video",
      "duration": 30,
      "audio_title": "Popular Song",
      "platform": "sample_platform",
      "media_url": null,
      "thumbnail_url": null
    }
  ],
  "total": 1,
  "region": "US",
  "provider": "mock",
  "timestamp": 1699920000
}
```

**Note**: Media URLs are excluded in compliance mode to prevent unauthorized content distribution.

## Quick Start

### Option 1: Development Script (Recommended)

1. **Clone the repository**:
```bash
git clone https://github.com/javadfarshchi/social-trends-harvester.git
cd social-trends-harvester
```

2. **Install in development mode**:
```bash
pip install -e ".[dev]"
```

3. **Run with development script**:
```bash
./scripts/dev.sh
```

4. **Test with mock data**:
```bash
curl http://localhost:8000/api/v1/healthz
curl "http://localhost:8000/api/v1/trending?provider=mock&count=5"
curl "http://localhost:8000/api/v1/hashtag/trending?provider=mock&count=3"
```

5. **View API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Option 2: Manual Setup

```bash
# Install dependencies
pip install -e .

# Run server directly
uvicorn social_trends_harvester.app:app --host 0.0.0.0 --port 8000 --reload
```

### Option 2: HAR Provider (User-Provided Data)

1. **Create HAR data directory**:
```bash
mkdir har_data
```

2. **Add your HAR files**:
   - Export HAR files from your browser's network tab
   - Place them in the `har_data/` directory
   - Ensure you have permission to use this data

3. **Test with HAR data**:
```bash
curl "http://localhost:8000/trending?provider=har&count=5"
```

### Option 3: Docker Compose

1. **Setup environment**:
```bash
cp env.example .env
# Edit .env as needed (optional Redis configuration)
```

2. **Start services**:
```bash
docker compose -f docker/docker-compose.yml up -d
```

3. **Test the API**:
```bash
curl http://localhost:8000/api/v1/healthz
curl "http://localhost:8000/api/v1/trending?provider=mock&count=5"
```

## Examples

### cURL Examples
Run pre-built examples:
```bash
./examples/curl/trending.sh
```

### n8n Workflow
Import the workflow from `examples/n8n/workflow.json` into your n8n instance.

### Postman Collection
Import `examples/postman_collection.json` for interactive API testing.

## Configuration

Environment variables (optional - see `env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL (optional) | None |
| `CACHE_TTL_S` | Cache TTL in seconds | 300 |

## Error Handling

The API returns appropriate HTTP status codes:
- `400`: Bad request (invalid parameters)
- `429`: Rate limit exceeded
- `504`: Request timeout
- `500`: Internal server error

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black app/ tests/
isort app/ tests/
flake8 app/ tests/
```

### Building Docker Image
```bash
docker build -t tiktok-trends-api .
```

## Production Deployment

### Docker Compose Production
```bash
docker-compose -f docker-compose.yml up -d
```

### Health Checks
The service includes health check endpoints for monitoring:
- Liveness: `GET /healthz`
- Readiness: `GET /healthz`

### Monitoring
- Logs are structured and include request IDs
- Cache statistics available at `/cache/stats`
- Rate limiting metrics in health check response

## Troubleshooting

### Common Issues

1. **Browser/Playwright Issues**:
   - Ensure Docker has sufficient memory (>2GB)
   - Check Chromium installation: `playwright install chromium`

2. **TikTok API Errors**:
   - Verify `TIKTOK_VERIFY_FP` if provided
   - Check proxy configuration if using
   - Monitor rate limits

3. **Cache Issues**:
   - Verify Redis connection
   - Check Redis memory usage
   - Clear cache if needed: `DELETE /cache/clear`

### Logs
```bash
# View service logs
docker-compose logs tiktok-trends-api

# Follow logs
docker-compose logs -f tiktok-trends-api
```

## Security

- Non-root user in Docker container
- Rate limiting to prevent abuse
- Input validation and sanitization
- Proxy support for network isolation
- No sensitive data in logs

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Open an issue with reproduction steps
