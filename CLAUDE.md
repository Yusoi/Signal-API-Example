# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A feature-flags API built with FastAPI and SQLAlchemy (async, SQLite via `aiosqlite`). It lets clients create flags, look them up by key, toggle a flag globally, and override a flag's active state for a specific user. The project is early-stage: there is no test suite and no lint configuration.

## Commands

Package management is via `uv` (see `uv.lock`, Python `>=3.14` per `.python-version`).

```bash
# Install dependencies
uv sync

# Apply DB migrations (creates/updates the SQLite file at DB_FILE_PATH)
uv run alembic upgrade head

# Generate a new migration after changing models/
uv run alembic revision --autogenerate -m "description"
```

Note: `uvicorn`/`fastapi[standard]` are not installed, so `fastapi dev`/`fastapi run` won't work out of the box (only the bare `fastapi` CLI extra is present, which errors asking for `fastapi[standard]`). To actually serve the app, add that dependency first, or run it in-process (e.g. via `fastapi.testclient.TestClient`, which only needs `httpx` — `uv run --with httpx python -c "..."`).

### Configuration

Settings are loaded via `pydantic-settings` in [src/flags/config.py](src/flags/config.py) with env prefix `DB_`, and are read from `.env` at the repo root (`env_file=".env"` on `DBSettings`):

- `DB_FILE_PATH` — required, path to the SQLite database file. Currently set to `./flags.db` in `.env` (gitignored).
- `DB_DRIVER` — optional, defaults to `sqlite+aiosqlite`.

`alembic/env.py` reads the same `settings.db` object to build `sqlalchemy.url`, so migrations always target whatever `.env` points at — the `sqlalchemy.url` placeholder in `alembic.ini` is unused.

## Architecture

Layered structure under `src/flags/`, request flow goes **controllers → services → repositories → DB**:

- `controllers/` — FastAPI `APIRouter`s (HTTP layer only: parse request, call a service, translate errors to `HTTPException`). Registered onto the app in `controllers/__init__.py` and mounted in `main.py`.
- `services/` — orchestration layer between controllers and repositories (e.g. `FlagsService` composes `FlagsRepository` and `FlagsOverridesRepository`).
- `repositories/` — data access. Note these execute **raw SQL via SQLAlchemy Core `text()`**, not the ORM, even though `models/` defines SQLAlchemy declarative ORM models (`Base` subclasses for `Flags`, `FlagOverrides`, `Users`) used only for `Base.metadata` (Alembic autogenerate). Because raw `text()` inserts bypass ORM-level Python defaults, repositories generate values like UUIDs themselves (see `FlagsRepository.create`) rather than relying on the model. Keep this in mind when adding new data access code, and match whichever pattern the surrounding code already uses.
- `schemas/` — Pydantic request/response models (distinct from the ORM models in `models/`).
- `deps/db.py` — FastAPI dependency (`DBSessionDep`) that yields an `AsyncConnection` (one per request, via `engine.begin()`, auto-commit/rollback on scope exit) from the app-wide `AsyncEngine`.
- `misc/db/` — `engine.py` builds the single `AsyncEngine` from `settings.db` (instantiated once in `main.py`'s `lifespan` and stored on `app.state.db_engine`, disposed on shutdown); `base.py` holds the shared SQLAlchemy `DeclarativeBase`.

### Data model

- `flags` — `id` (UUID, primary key), `key` (unique, indexed, used for all lookups/mutations), `name`, `is_active`.
- `flags_overrides` — per-user override of a flag's `is_active`; composite PK of `key` (FK → `flags.key`) + `user_id` (FK → `users.id`).
- `users` — `id`, `name`, `email`, `password`. Exists in `models/` but has no repository/service/controller yet.

Migrations live in `alembic/versions/`; the initial migration (`create flags tables`) creates all three tables and should stay the source of truth for schema history going forward — modify models + autogenerate a new revision rather than hand-editing existing ones.
