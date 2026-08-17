# Signal-API-Example

A feature-flags API built with FastAPI and SQLAlchemy (async, SQLite). Create flags, look them up by key, toggle a flag globally, and override a flag's active state for a specific user.

## Prerequisites

- Python `>=3.14` (see `.python-version`)
- [`uv`](https://docs.astral.sh/uv/) for dependency management

## Setup

```bash
# Install dependencies (app + dev/test dependencies)
uv sync
```

## Running the application

```bash
uv run fastapi dev src/flags/main.py
```

This starts the API with auto-reload at `http://127.0.0.1:8000`. For a production-style run (no reload) use `uv run fastapi run src/flags/main.py` instead.

### API documentation

Once the server is running, interactive docs are available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Raw OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

### Available endpoints

All routes are prefixed with `/flags`.

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/flags` | Create a new flag (`key`, `name`, `is_active`) |
| `GET` | `/flags/{key}` | Look up a flag by its key |
| `PATCH` | `/flags/{key}?is_active=<bool>` | Toggle a flag's `is_active` globally |
| `GET` | `/flags/{key}/users/{user_id}` | Get the effective access for a specific user (user override takes precedence over the global value) |
| `PATCH` | `/flags/{key}/users/{user_id}?is_active=<bool>` | Set a per-user override for a flag |

See the Swagger UI for full request/response schemas.

## Running the tests

Test dependencies (`pytest`, `pytest-asyncio`, `httpx`) are installed as part of `uv sync`.

```bash
uv run pytest -v
```

Tests live under `tests/`:

- `tests/unit/` — unit tests exercising business logic in isolation (e.g. the user-override precedence logic), with repositories mocked out.
- `tests/integration/` — integration tests that exercise the full HTTP stack against an in-memory SQLite database.
