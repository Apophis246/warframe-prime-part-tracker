# models.py — outline only, no implementation yet.
#
# This assumes SQLAlchemy (the standard ORM pairing for FastAPI + Postgres).
# If you decide on something else, this structure still applies conceptually.
#
# Whatever you use will need:
#   - a declarative Base (usually defined in database.py, imported here)
#   - a Column type + primary key convention
#   - a way to express foreign keys and relationships between classes
#
# Look up: SQLAlchemy declarative models, Column, ForeignKey, relationship(),
# and (if you want item_type constrained) Python's enum.Enum used as a column type.


# --- User ---------------------------------------------------------------
# Fields:
#   id               -> primary key
#   username         -> string, should be unique
#   email            -> string, should be unique
#   password_hash    -> string (never store the raw password)
#
# Relationship:
#   one User -> many InventoryEntry (a user's owned parts)


# --- PrimeItem ------------------------------------------------------------
# Fields:
#   id           -> primary key
#   name         -> string, e.g. "Volt Prime"
#   item_type    -> constrained to "warframe" or "weapon" (enum column, or a
#                    plain string + validation — your call)
#
# Relationship:
#   one PrimeItem -> many PartRequirement (the parts that make up this item)


# --- PartRequirement --------------------------------------------------------
# Fields:
#   id                   -> primary key
#   prime_item_id        -> foreign key -> PrimeItem.id
#   part_name            -> string, e.g. "Neuroptics", "Blueprint"
#   quantity_required    -> integer (most are 1, some weapons need 2 — see
#                            Fang Prime / Glaive Prime in the blueprint)
#
# Relationships:
#   many PartRequirement -> one PrimeItem  (belongs to)
#   one PartRequirement -> many InventoryEntry (one per user who owns any)


# --- InventoryEntry ---------------------------------------------------------
# Fields:
#   id                     -> primary key
#   user_id                -> foreign key -> User.id
#   part_requirement_id    -> foreign key -> PartRequirement.id
#   quantity_owned         -> integer, how many of that part this user has
#
# Relationships:
#   many InventoryEntry -> one User            (belongs to)
#   many InventoryEntry -> one PartRequirement  (belongs to)
#
# Worth thinking about:
#   - Should (user_id, part_requirement_id) be constrained unique? A user
#     should only have one inventory row per part requirement — a duplicate
#     would make "how many do I own" ambiguous.
#   - A missing InventoryEntry row means "owns zero" (per the blueprint) —
#     that's a query-time default, not something to backfill with rows.
