from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models
from .auth import router as auth_router
from .database import Base, engine
from .routes import router as routes_router

# What belongs here:
#   - create the FastAPI() app instance
#   - register/include the routers from routes.py and auth.py (look up:
#     APIRouter, app.include_router())
#   - CORS middleware — the frontend (a different origin: nginx on some
#     port) needs to be allowed to call this API from the browser. Look
#     up: FastAPI's CORSMiddleware.
#   - something to create the database tables on startup, OR a decision
#     to use Alembic migrations instead. Base.metadata.create_all() is
#     the quick version; migrations are the "proper" version. Your call
#     for a project this size.
#
# What does NOT belong here: route logic itself (routes.py/auth.py),
# model definitions (models.py). This file wires things together, it
# doesn't implement them.

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
