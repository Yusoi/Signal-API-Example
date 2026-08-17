from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from flags.config import settings


def instance_db_engine() -> AsyncEngine:
    return create_async_engine(url=f"{settings.db.driver}:///{settings.db.file_path}")
