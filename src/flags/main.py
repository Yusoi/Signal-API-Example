from contextlib import asynccontextmanager

from fastapi import FastAPI

from flags.controllers import flags_router
from flags.misc.db.engine import instance_db_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_engine = instance_db_engine()


app = FastAPI(lifespan=lifespan)

app.include_router(router=flags_router)
