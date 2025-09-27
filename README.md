# Social Trends Harvester

![CI](https://img.shields.io/badge/CI-passing-brightgreen?style=flat) ![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)

**A site-agnostic FastAPI service** that turns messy “trending content” data into a clean, normalized API. Built with caching, simple rate limiting, and a plug-in provider interface — shipping only **safe** example providers (mock + HAR).

> If this is useful, please ⭐ the repo — it helps others find it!

---

## Why you’ll like it

* **Plug-and-play API** – hit `/api/v1/trending` and go
* **Site-agnostic** – swap in providers without changing clients
* **Compliance-first** – robots.txt respect, no bypass code, no secrets
* **Developer-friendly** – fixtures, tests, examples for cURL, Postman, n8n

---

## ⚖️ Legal & Acceptable Use (short)

This is general-purpose tooling. **You are responsible** for how you use it. Many platforms restrict automated access in their Terms. This project ships **no** anti-bot, CAPTCHA, or access-control bypass.
See **[LEGAL_CONSIDERATIONS.md](./LEGAL_CONSIDERATIONS.md)** for details.

---

## Quickstart

### 1) Run locally (Python 3.10+)

```bash
git clone https://github.com/javadfarshchi/social-trends-harvester.git
cd social-trends-harvester
pip install -e ".[dev]"   # or: pip install -e .
uvicorn social_trends_harvester.app:app --reload
```

Open: `http://localhost:8000/docs`

### 2) Docker

```bash
cp env.example .env   # optional
docker compose -f docker/docker-compose.yml up --build
# App: http://localhost:8000  (Swagger at /docs)
```

---

## Try it in 30 seconds (mock data)

```bash
# Health
curl http://localhost:8000/api/v1/healthz

# Trending (mock provider)
curl "http://localhost:8000/api/v1/trending?provider=mock&region=US&count=5"

# Hashtag (mock provider)
curl "http://localhost:8000/api/v1/hashtag/trending?provider=mock&count=3"
```

---

## Providers

This repo includes **safe** providers only:

* **`mock`** — reads sanitized JSON fixtures (great for demos & tests)
* **`har`** — parses your **own** browser HAR exports (when you have permission)

> Want to add another source? Implement `TrendsProvider` and register it — just **don’t** submit bypass code. See **[CONTRIBUTING.md](./CONTRIBUTING.md)**.

---

## API (v1)

* `GET /api/v1/healthz` – service health
* `GET /api/v1/providers` – available providers
* `GET /api/v1/trending?provider=mock&region=US&count=30`
* `GET /api/v1/hashtag/{tag}?provider=mock&region=US&count=30`
* `GET /api/v1/cache/stats` • `DELETE /api/v1/cache/clear` *(if enabled)*

### Example item (abridged)

```json
{
  "id": "content_123",
  "description": "Content description",
  "author": "username",
  "created_at": 1699920000,
  "stats": { "view_count": 1234567, "like_count": 54321, "comment_count": 987, "share_count": 321 },
  "hashtags": ["trending", "viral"],
  "media_type": "video",
  "duration": 30,
  "platform": "sample_platform",
  "thumbnail_url": null
}
```

---

## Configuration

Copy `env.example` → `.env`. Common settings:

| Key                   | What it does                           | Default |
| --------------------- | -------------------------------------- | ------- |
| `REDIS_URL`           | Optional Redis cache                   | —       |
| `CACHE_TTL_S`         | Cache TTL (seconds)                    | `300`   |
| `RATE_LIMIT_REQUESTS` | Simple per-minute limit                | `10`    |
| `LOG_LEVEL`           | `DEBUG` | `INFO` | `WARNING` | `ERROR` | `INFO`  |

---

## Examples

* **cURL:** `./examples/curl/trending.sh`
* **Postman:** `./examples/postman_collection.json`
* **n8n:** `./examples/n8n/workflow.json`

---

## Development

```bash
# run dev server
./scripts/dev.sh

# tests / lint
./scripts/test.sh
./scripts/lint.sh

# or directly
pytest -q
```

Project layout (short):

```
src/social_trends_harvester/   # app, api/v1, core, providers, schemas
tests/                          # unit, integration, fixtures
docs/                           # api.md (+ your future docs)
examples/                       # curl, Postman, n8n
```

---

## Roadmap

* [ ] Provider registry with entry points
* [ ] Optional Redis cache image in docker-compose
* [ ] Sample dashboard (Streamlit) for quick viz
* [ ] More fixtures & contract tests

If you want these, **star** the repo and open an issue — it helps prioritize work!

---

## Contributing & License

* PRs welcome (please read **[CONTRIBUTING.md](./CONTRIBUTING.md)**).
* By contributing you agree to the **MIT** license and our **Code of Conduct**.

---

**If this saved you time, a ⭐ means a lot.**
