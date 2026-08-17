from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from flags.deps.db import DBSessionDep
from flags.exceptions.flags import FlagNotFoundException
from flags.schemas.flags import CreateFlagRequest, GetFlagResponse
from flags.services.flags import FlagsService

router = APIRouter(prefix="/flags", tags=["Flags"])


@router.post("")
async def create_flag(session: DBSessionDep, body: CreateFlagRequest) -> UUID:
    try:
        result = await FlagsService(session).create(body)
    except Exception as e:
        logger.error(f"Error while creating flag {e}")
        raise e
    return result


@router.get("/{key}")
async def get_flag(session: DBSessionDep, key: str) -> GetFlagResponse:
    try:
        result = await FlagsService(session).get(key)
    except Exception as e:
        logger.error(f"Error while getting flag {e}")

    if result is None:
        raise HTTPException(status_code=404, detail="Flag does not exist")

    return GetFlagResponse(**result)


@router.patch("/{key}")
async def patch_flag(
    session: DBSessionDep, key: str, is_active: bool = Query(...)
) -> None:
    try:
        result = await FlagsService(session).patch_is_active(key, is_active)
    except Exception as e:
        logger.error(f"Error while patching flag {e}")
        raise e


@router.get("/{key}/users/{user_id}")
async def get_user_access_by_key(
    session: DBSessionDep, key: str, user_id: UUID
) -> bool:
    try:
        return await FlagsService(session).get_user_access_by_key(
            key,
            user_id,
        )
    except FlagNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error while getting flag access by user {e}")
        raise e


@router.patch("/{key}/users/{user_id}")
async def patch_flag_for_user(
    session: DBSessionDep, key: str, user_id: UUID, is_active: bool = Query(...)
) -> None:
    try:
        result = await FlagsService(session).patch_is_active_by_user(
            key, user_id, is_active
        )
    except Exception as e:
        logger.error(f"Error while patching flag by user {e}")
        raise e
