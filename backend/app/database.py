# database.py — outline only, no implementation yet.
#
# This is where the SQLAlchemy engine, session, and Base live — the shared
# infrastructure every model and route depends on, but that isn't itself a
# model or a route.

# --- Base -----------------------------------------------------------------
# Base = declarative_base()
#
# Every class in models.py will import and inherit from this. It's what
# lets SQLAlchemy track "these are all my mapped tables" in one place
# (Base.metadata) instead of each model registering itself independently.

# --- Engine -----------------------------------------------------------------
# The engine is what actually knows how to talk to Postgres: host, port,
# credentials, database name, all bundled into a connection string
# (a "database URL"), e.g.:
#   postgresql://<user>:<password>@<host>:<port>/<dbname>
#
# Don't hardcode that string here — read it from an environment variable
# instead (this is exactly what .env / .env.example at the repo root are
# for). Look up: python-dotenv, or os.environ, and SQLAlchemy's
# create_engine().

# --- Session ------------------------------------------------------------
# A single engine is shared app-wide, but each request needs its own
# "conversation" with the database — that's what a Session is for.
#
# The common FastAPI pattern:
#   1. A sessionmaker bound to the engine (produces new Session objects)
#   2. A get_db() dependency function that opens a session, yields it to
#      the route, then closes it afterward (even if the route raised)
#
# Look up: SQLAlchemy sessionmaker, and FastAPI's Depends() — get_db()
# is what routes.py and auth.py will import and depend on to talk to the
# database at all.
#
# Worth thinking about:
#   - What happens if DATABASE_URL isn't set? Fail loudly at startup,
#     rather than silently, is usually the better choice.
