from uuid import UUID

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
                    (key, name, is_active)
                VALUES
                    (:key, :name, :is_active)   
                RETURNING id   
            """),
            {
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
                UPDATE flags (id, is_active)
                VALUES (:id, :is_active)
            """),
            {
                "id": str(id),
                "is_active": is_active,
            },
        )
