from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class FlagsOverridesRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, key: str, user_id: UUID) -> bool | None:
        result = await self._session.execute(
            text("""
                SELECT fo.is_active
                FROM flags_overrides fo
                INNER JOIN flags f
                    ON fo.flag_id = f.id
                WHERE 
                    fo.user_id = :user_id AND
                    f.key = :key 
            """),
            {"key": key, "user_id": str(user_id)},
        )
        return result.scalar_one_or_none()

    async def patch_is_active_by_user(
        self, key: str, user_id: UUID, is_active: bool
    ) -> None:
        await self._session.execute(
            text("""
                INSERT INTO flags_overrides (flag_id, user_id, is_active)
                SELECT id, :user_id, :is_active
                FROM flags
                WHERE key = :key
                ON CONFLICT (flag_id, user_id)
                DO UPDATE SET
                    is_active = EXCLUDED.is_active
            """),
            {
                "key": key,
                "user_id": str(user_id),
                "is_active": is_active,
            },
        )
