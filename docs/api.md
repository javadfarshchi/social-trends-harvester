# API Documentation

## Overview

The Social Trends Harvester provides a RESTful API for accessing social media trends data through multiple providers while maintaining compliance with legal and ethical standards.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. This may change in future versions.

## Rate Limiting

- Default: 10 requests per minute per IP
- Configurable via `RATE_LIMIT_REQUESTS` environment variable
- Note: rate limit headers are not included in responses in this version

## Endpoints

### Health Check

**GET /api/v1/healthz**

Returns the health status of the service and all providers.

**Response:**
```json
{
  "status": "ok",
  "timestamp": 1699920000,
  "providers": {
    "mock": true,
    "har": true
  },
  "compliance_status": {
    "manager_initialized": true
  }
}
```

### Service Information

**GET /**

Returns basic service information and available endpoints.

### Trending Content

**GET /api/v1/trending**

Fetch trending content from the specified provider.

**Parameters:**
- `provider` (optional): Provider to use ("mock", "har"). Default: "mock"
- `region` (optional): Region code (ISO 3166-1 alpha-2). Default: "US"
- `count` (optional): Number of items to return (1-60). Default: 30

**Response:**
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
      "platform": "sample_platform"
    }
  ],
  "total": 1,
  "region": "US",
  "provider": "mock",
  "timestamp": 1699920000
}
```

### Hashtag Content

**GET /api/v1/hashtag/{tag}**

Fetch content for a specific hashtag.

**Parameters:**
- `tag` (required): Hashtag to search (without # prefix)
- `provider` (optional): Provider to use ("mock", "har"). Default: "mock"
- `region` (optional): Region code (ISO 3166-1 alpha-2). Default: "US"
- `count` (optional): Number of items to return (1-60). Default: 30

### Provider Information

**GET /api/v1/providers**

List all available providers and their capabilities.

**Response:**
```json
[
  {
    "name": "mock",
    "supported_regions": ["US", "GB", "CA", "AU"],
    "supported_features": ["trending", "hashtag"],
    "rate_limits": {},
    "compliance_level": "strict"
  }
]
```

### Compliance Information

**GET /api/v1/compliance**

Get compliance information and guidelines.

**Response:**
```json
{
  "robots_txt_respected": true,
  "rate_limiting_enabled": true,
  "user_agent": "SocialTrendsHarvester/1.0 (+https://github.com/javadfarshchi/social-trends-harvester)",
  "supported_protocols": ["https"],
  "guidelines": {
    "usage": "Use only with authorized data sources",
    "rate_limits": "Respect all rate limits and robots.txt directives",
    "content": "No media downloads - metadata only",
    "legal": "Users responsible for compliance with applicable laws and ToS"
  }
}
```

## Error Responses

All errors return a structured error response:

```json
{
  "error": "Error message",
  "error_code": "VALIDATION_ERROR",
  "http_status": 400,
  "timestamp": 1699920000
}
```

### Error Codes

- `400` - Bad Request (invalid parameters)
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

## Interactive Documentation

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## Compliance Notes

- All responses exclude media URLs for compliance
- Only metadata is returned
- Rate limiting is enforced
- Robots.txt is respected for external requests
- Ethical user agent is used for all requests
