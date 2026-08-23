# auth.py — outline only, no implementation yet.
#
# Handles the two unauthenticated routes plus the shared logic every
# other route depends on for knowing "who is making this request."

# --- Password hashing -------------------------------------------------
# Never store or compare plaintext passwords. Hash on register, verify
# the hash on login. Look up: passlib (bcrypt scheme) or a similar
# library — don't hand-roll hashing.

# --- POST /auth/register ------------------------------------------
# Accepts UserCreate (schemas.py). Steps:
#   1. check username/email isn't already taken
#   2. hash the password
#   3. create and save a User row
#   4. return... what? (a Token, so they're logged in immediately? Or
#      just a success response and they log in separately? Your call.)

# --- POST /auth/login ---------------------------------------------
# Accepts UserLogin. Steps:
#   1. look up the user by username/email
#   2. verify the password against the stored hash
#   3. if valid, issue a JWT (look up: python-jose or PyJWT) containing
#      enough to identify the user later (commonly just their id, as the
#      token's "sub" claim)
#   4. return a Token

# --- get_current_user dependency ------------------------------------
# This is the piece every OTHER route in routes.py depends on. It:
#   1. reads the Authorization header (Bearer <token>)
#   2. decodes/verifies the JWT (checks signature + expiry)
#   3. looks up and returns the corresponding User row
#   4. raises a 401 if any of that fails
#
# Look up: FastAPI's OAuth2PasswordBearer (or a plain Depends() reading
# the header yourself), and how JWT signing/verification uses a secret
# key — this needs to come from an environment variable (JWT secret in
# .env.example), never hardcoded.
