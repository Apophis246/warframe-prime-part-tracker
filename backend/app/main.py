from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models
from .auth import router as auth_router
from .database import Base, engine
from .routes import router as routes_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)
# No CORS middleware: nginx proxies /api to this service, so the browser only
# ever talks to one origin and cross-origin requests never happen. Add it back
# if anything is ever served from a different origin than the API.
app.include_router(auth_router)
app.include_router(routes_router)
