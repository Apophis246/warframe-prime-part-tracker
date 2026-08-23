# schemas.py — outline only, no implementation yet.
#
# These are Pydantic models — separate from the SQLAlchemy models in
# models.py. SQLAlchemy models describe database tables; these describe
# the shape of JSON going in and out of the API. Keeping them separate
# means you control exactly what a client can send (e.g. never accept a
# raw password_hash) and exactly what gets returned (e.g. never return
# password_hash at all).
#
# Look up: Pydantic BaseModel, and FastAPI's response_model= parameter
# on route decorators.

# --- Auth schemas -----------------------------------------------------
# UserCreate   -> what /auth/register accepts: username, email, password
#                 (plaintext here — hashing happens in auth.py, never in
#                 the schema or the route)
# UserLogin    -> what /auth/login accepts: username/email + password
# Token        -> what /auth/login returns: access_token, token_type

# --- PrimeItem / PartRequirement schemas (read-only) -----------------
# PartRequirementOut  -> id, part_name, quantity_required
# PrimeItemOut        -> id, name, item_type, and a nested list of
#                         PartRequirementOut (this is the /items response
#                         shape — the static catalog)
#
# Worth thinking about: nesting one schema inside another is normal in
# Pydantic, and it's how you'll express "an item and all its parts" in
# one response without a second request.

# --- InventoryEntry schemas -------------------------------------------
# InventoryEntryOut     -> part_requirement_id, quantity_owned
# InventoryEntryUpdate  -> what PUT /inventory/{part_requirement_id}
#                           accepts in its body: just quantity_owned

# --- Sets schema ---------------------------------------------------------
# PartStatusOut  -> part_name, quantity_required, quantity_owned
# SetStatusOut   -> prime_item id/name, status ("complete"/"partial"/
#                    "none"), and the list of PartStatusOut so the
#                    frontend can show exactly what's missing on a
#                    partial set
