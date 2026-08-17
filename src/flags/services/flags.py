from uuid import UUID

from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from flags.repositories.flags import FlagsRepository
from flags.repositories.flags_overrides import FlagsOverridesRepository
from flags.schemas.flags import CreateFlagRequest


class FlagsService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._flags_repository = FlagsRepository(self._session)
        self._flags_overrides_repository = FlagsOverridesRepository(self._session)

    async def create(self, data: CreateFlagRequest) -> UUID:
        return await self._flags_repository.create(data)

    async def get(self, key: str) -> RowMapping | None:
        return await self._flags_repository.get(key)

    async def patch_is_active(self, key: str, is_active: bool) -> None:
        return await self._flags_repository.patch_is_active(key, is_active)

    async def patch_is_active_by_user(
        self, key: str, user_id: UUID, is_active: bool
    ) -> None:
        return await self._flags_overrides_repository.patch_is_active_by_user(
            key, user_id, is_active
        )
