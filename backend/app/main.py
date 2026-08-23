# main.py — outline only, no implementation yet.
#
# This is the FastAPI application's entrypoint — what uvicorn actually
# runs.

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
