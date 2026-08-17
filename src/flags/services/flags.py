from uuid import UUID

from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from flags.exceptions.flags import FlagNotFoundException
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

    async def get_user_access_by_key(self, key: str, user_id: UUID) -> bool:
        global_flag = await self._flags_repository.get(key)
        if global_flag is None:
            raise FlagNotFoundException(f'Flag with key "{key}" wasn\'t found')

        global_access = global_flag["is_active"]
        user_access = await self._flags_overrides_repository.get(key, user_id)

        # Following the predetermined order in the challenge
        if user_access is not None:
            return user_access

        return global_access

    async def patch_is_active_by_user(
        self, key: str, user_id: UUID, is_active: bool
    ) -> None:
        return await self._flags_overrides_repository.patch_is_active_by_user(
            key, user_id, is_active
        )
