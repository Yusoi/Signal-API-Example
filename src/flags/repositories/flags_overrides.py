from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class FlagsOverridesRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def patch_is_active_by_user(
        self, key: str, user_id: UUID, is_active: bool
    ) -> None:
        await self._session.execute(
            text("""
                INSERT INTO flags_overrides (key, user_id, is_active)
                VALUES (:key, :user_id, :is_active)
                ON CONFLICT (key, user_id)
                DO UPDATE SET
                    is_active = EXCLUDED.is_active
            """),
            {
                "key": key,
                "user_id": user_id,
                "is_active": is_active,
            },
        )
