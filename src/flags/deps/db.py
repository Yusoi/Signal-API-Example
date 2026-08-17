from typing import Annotated

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine
from loguru import logger


async def get_db_session(request: Request):
    engine: AsyncEngine = request.app.state.db_engine

    try:
        async with engine.begin() as session:
            yield session
    except Exception as e:
        logger.error(e)


DBSessionDep = Annotated[AsyncEngine, get_db_session()]
