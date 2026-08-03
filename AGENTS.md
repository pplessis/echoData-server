# echoData-server — Agent Guide

## Project Overview
Flask REST API serving structured knowledge (international days, days off, saints, horoscopes) from JSON files and external scraping. Deployed on Vercel (serverless).

## Architecture
- **Entry point**: `app.py` → `api.create_app()` → registers blueprints
- **Blueprints** (in `api/routes/`):
  - `home` — root `/`
  - `events_v100` — `/v100/international_day`, `/v100/daysOff`, `/v100/saints`, `/v100/random`
  - `oracle_v100` — `/v100/oracle?sign=<SIGN>`
- **Services** (in `api/services/`):
  - `service_events_day.py` — loads/filters JSON event data
  - `service_oracle.py` — scrapes 20minutes.fr for horoscopes
- **Models** (in `api/models/`): dataclasses for `EventDay`, `Horoscope`, `Sign`, `Section`
- **Config**: `api/config.py` — env-based, loads `.env`, sets up logging
- **Static data**: `api/static/data/events/*.json` (internationalDays, daysOff, saints)

## Developer Commands

### Local Development
```bash
# Install deps
pip install -r requirements.txt

# Run Flask dev server (port 5055)
python app.py

# Or with Vercel CLI (simulates serverless)
vercel dev
```

### Deployment (Vercel)
```bash
# Production deploy
vercel --prod
```
Required Vercel env vars: `SECRET_KEY`, `FLASK_DEBUG`, optionally `DATABASE_JSON_PATH`, `MAIL_SERVER`.

### Testing
No test suite configured. Add tests in `tests/` mirroring `api/` structure if needed.

## Key Patterns & Conventions

### Response Format
All endpoints return `myJsonResponce` structure:
```json
{
  "status": "success|error|warning|info|unknown",
  "event": "fetched|info|created|...|unknown",
  "message": "Human readable",
  "data": [...],
  "errors": [{"key": "value"}],
  "meta": {"len": N, "requestDate": "YYYYMMDDThhmmss"},
  "$schema": "https://rapid-night-e462.paix-principal-56.workers.dev"
}
```
Import: `from api.libs.src.json.myJsonResponce import myJsonResponce, RESULT_STATUS, RESULT_EVENTS`

### Error Handling
- Global 404/500 handlers in `api/__init__.py` return JSON
- Services raise exceptions; routes catch, log, return error response

### Data Loading
- JSON files loaded on each request (serverless-safe, no in-memory caching across invocations)
- Paths from `Config.DATABASE_JSON_EVENTS`, `DATABASE_JSON_DAYOFF`, `DATABASE_JSON_SAINTS`
- Override via `DATABASE_JSON_PATH` env var

### Logging
- Stdout only on Vercel (`VERCEL=1`); file logging locally in `api/logs/app.log`
- Use `from api.config import logger`

### Adding New Endpoints
1. Create blueprint in `api/routes/<name>.py`
2. Register in `api/__init__.py`: `app.register_blueprint(bp, url_prefix='/v100')`
3. Use `myJsonResponce` for consistent output
4. Put business logic in `api/services/`

## Known Constraints
- **Serverless**: No local file writes persist. Don't write to JSON files.
- **Horoscope scraping**: Relies on 20minutes.fr HTML structure; brittle.
- **No auth** currently implemented.
- **Python 3.11** target (Vercel default).

## File Map (High-Level)
```
app.py                    # WSGI entry
api/
  __init__.py             # create_app(), blueprints, error handlers
  config.py               # Config, logging, paths
  routes/
    home.py               # GET /
    events_v100.py        # International days, days off, saints
    oracle_v100.py        # Horoscope scraping
  services/
    service_events_day.py # JSON load/filter by date/type
    service_oracle.py     # HTTP scrape + BeautifulSoup parse
  models/
    dataClasses_EventDay.py
    dataClasses_Horoscope.py
  libs/src/json/
    myJsonResponce.py     # Standardized response builder
  static/data/events/     # Source JSON files
vercel.json               # Vercel routing + CORS
requirements.txt          # Flask, requests, beautifulsoup4, gunicorn, python-dotenv
```

## Environment Variables
| Var | Default | Notes |
|-----|---------|-------|
| `FLASK_HOST` | `[IP_ADDRESS]` | Dev only |
| `FLASK_PORT` | `5055` | Dev only |
| `FLASK_DEBUG` | `False` | `True` for debug |
| `SECRET_KEY` | `dev-secret-key-change-me` | **Must override in prod** |
| `DATABASE_JSON_PATH` | `api/static/data/events` | JSON file directory |
| `MAIL_SERVER` | — | Optional |
| `VERCEL` | — | Set to `1` by Vercel; disables file logging |