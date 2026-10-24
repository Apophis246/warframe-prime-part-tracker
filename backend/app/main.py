from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8180"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(routes_router)
