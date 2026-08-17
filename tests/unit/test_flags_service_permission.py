from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from flags.exceptions.flags import FlagNotFoundException
from flags.services.flags import FlagsService


def make_service(global_flag=None, user_access=None) -> FlagsService:
    service = FlagsService(session=MagicMock())
    service._flags_repository = AsyncMock()
    service._flags_repository.get.return_value = global_flag
    service._flags_overrides_repository = AsyncMock()
    service._flags_overrides_repository.get.return_value = user_access
    return service


async def test_raises_when_flag_not_found():
    service = make_service(global_flag=None)
    user_id = uuid4()

    with pytest.raises(FlagNotFoundException):
        await service.get_user_access_by_key("missing-flag", user_id)

    service._flags_overrides_repository.get.assert_not_called()


async def test_returns_global_true_when_no_override():
    service = make_service(global_flag={"is_active": True}, user_access=None)

    result = await service.get_user_access_by_key("some-flag", uuid4())

    assert result is True


async def test_returns_global_false_when_no_override():
    service = make_service(global_flag={"is_active": False}, user_access=None)

    result = await service.get_user_access_by_key("some-flag", uuid4())

    assert result is False


async def test_override_true_wins_over_global_false():
    service = make_service(global_flag={"is_active": False}, user_access=True)

    result = await service.get_user_access_by_key("some-flag", uuid4())

    assert result is True


async def test_override_false_wins_over_global_true():
    service = make_service(global_flag={"is_active": True}, user_access=False)

    result = await service.get_user_access_by_key("some-flag", uuid4())

    assert result is False


async def test_repositories_called_with_expected_args():
    key = "some-flag"
    user_id = uuid4()
    service = make_service(global_flag={"is_active": True}, user_access=False)

    await service.get_user_access_by_key(key, user_id)

    service._flags_repository.get.assert_awaited_once_with(key)
    service._flags_overrides_repository.get.assert_awaited_once_with(key, user_id)
