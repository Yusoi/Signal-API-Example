from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine


async def get_db_session(request: Request):
    engine: AsyncEngine = request.app.state.db_engine

    async with engine.begin() as connection:
        yield connection


DBSessionDep = Annotated[AsyncConnection, Depends(get_db_session)]
