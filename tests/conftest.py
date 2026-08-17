from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

import flags.models  # noqa: F401  (registers ORM tables on Base.metadata)
from flags.deps.db import get_db_session
from flags.main import app
from flags.misc.db.base import Base


@pytest.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def client(db_engine):
    async def override_get_db_session():
        async with db_engine.begin() as connection:
            yield connection

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def seed_flag(db_engine):
    async def _seed_flag(key: str, name: str = "Test Flag", is_active: bool = True) -> UUID:
        flag_id = uuid4()
        async with db_engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO flags (id, key, name, is_active)
                    VALUES (:id, :key, :name, :is_active)
                """),
                {
                    "id": str(flag_id),
                    "key": key,
                    "name": name,
                    "is_active": is_active,
                },
            )
        return flag_id

    return _seed_flag
