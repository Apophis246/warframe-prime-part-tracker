# auth.py — outline only, no implementation yet.
#
# Handles the two unauthenticated routes plus the shared logic every
# other route depends on for knowing "who is making this request."
#
# Packages (already in requirements.txt — rebuild the image if you
# haven't since they were added):
#   pwdlib[argon2]  -> password hashing
#   pyjwt           -> token creation/verification

from pwdlib import PasswordHash

# --- Password hashing -------------------------------------------------
# Never store or compare plaintext passwords. Hash on register, verify
# the hash on login.
#
# Use pwdlib's PasswordHash.recommended() — it picks Argon2 with sane
# parameters, generates a salt per password, and encodes the algorithm and
# its settings into the stored hash string, so verification works without
# you tracking any of that yourself. Create it once at module level and
# reuse it; building it per request is wasted work.
#
# It gives you two methods: one to hash a new password, one to verify a
# plaintext attempt against a stored hash. Look those up rather than
# guessing the names.
#
# Why not hashlib: SHA-256 and friends are built to be fast, which is
# exactly wrong here — a leaked database can be brute-forced at billions
# of guesses per second. Argon2 is deliberately slow and memory-hard.
# (hashlib.scrypt and hashlib.pbkdf2_hmac ARE real password KDFs, but
# then you manage salts and the stored format by hand.)
#
# Note: passlib is what most older tutorials use. It's effectively
# unmaintained — last release 2020, broken on Python 3.13 — so don't.


# --- POST /auth/register ------------------------------------------
# Accepts UserCreate (schemas.py). Steps:
#   1. check username/email isn't already taken
#   2. hash the password
#   3. create and save a User row
#   4. return... what? (a Token, so they're logged in immediately? Or
#      just a success response and they log in separately? Your call.)
#
# Worth thinking about: your User model has unique constraints on both
# username and email, so the database will reject a duplicate even if
# step 1 is skipped — but it'd surface as an IntegrityError, not a clean
# 409/400 with a useful message.


# --- POST /auth/login ---------------------------------------------
# Accepts UserLogin. Steps:
#   1. look up the user by username OR email (the decision from earlier —
#      UserLogin allows either, so the query has to match on both fields)
#   2. verify the password against the stored hash
#   3. if valid, issue a JWT with pyjwt containing enough to identify the
#      user later (conventionally their id, as the token's "sub" claim)
#      plus an expiry ("exp" claim — pyjwt enforces it automatically on
#      decode)
#   4. return a Token
#
# Worth thinking about: give the same error for "no such user" and "wrong
# password". Distinguishing them tells an attacker which usernames exist.


# --- get_current_user dependency ------------------------------------
# This is the piece every OTHER route in routes.py depends on. It:
#   1. reads the Authorization header (Bearer <token>)
#   2. decodes/verifies the JWT (checks signature + expiry)
#   3. looks up and returns the corresponding User row
#   4. raises a 401 if any of that fails
#
# Look up: FastAPI's OAuth2PasswordBearer (or a plain Depends() reading
# the header yourself), and pyjwt's encode/decode — note that decode
# raises distinct exceptions for an expired token vs a bad signature, and
# both should become a 401 rather than a 500.
#
# It depends on get_db from database.py for the user lookup, exactly like
# the routes do.


# --- The signing secret ------------------------------------------------
# SETUP STEP, do this before writing the JWT code:
#   - add JWT_SECRET_KEY to .env (and .env.example with a placeholder)
#   - read it here with os.environ["JWT_SECRET_KEY"], same fail-loud
#     pattern as DATABASE_URL in database.py
#   - never hardcode it, never commit it
#
# This one matters more than the Postgres password: anyone who knows it
# can mint a valid token for any user. Locally, anything random is fine.
# For the VM, Terraform's random_password generates it and it goes into
# Vault, per the blueprint.
#
# You also need to pick a signing algorithm (HS256 is the usual symmetric
# default) and a token lifetime.
