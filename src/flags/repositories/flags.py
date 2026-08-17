from uuid import UUID, uuid4

from sqlalchemy import RowMapping, text
from sqlalchemy.ext.asyncio import AsyncSession

from flags.schemas.flags import CreateFlagRequest


class FlagsRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: CreateFlagRequest) -> UUID:
        result = await self._session.execute(
            text("""
                INSERT INTO flags
                    (id, key, name, is_active)
                VALUES
                    (:id, :key, :name, :is_active)
                RETURNING id
            """),
            {
                "id": str(uuid4()),
                "key": data.key,
                "name": data.name,
                "is_active": data.is_active,
            },
        )

        return result.scalar_one_or_none()

    async def get(self, key: str) -> RowMapping | None:
        result = await self._session.execute(
            text("""
                SELECT id, key, name, is_active
                FROM flags
                WHERE key = :key
            """),
            {"key": key},
        )

        return result.mappings().one_or_none()

    async def patch_is_active(self, key: str, is_active: bool) -> None:
        await self._session.execute(
            text("""
                UPDATE flags
                SET is_active = :is_active
                WHERE key = :key
            """),
            {
                "key": key,
                "is_active": is_active,
            },
        )
