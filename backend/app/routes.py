# routes.py — outline only, no implementation yet.
#
# Every route here (per the blueprint) requires a valid token — each
# should depend on get_current_user from auth.py, and every query should
# be scoped to that user. There is no route here that reads or writes
# another user's data.

# --- GET /items ------------------------------------------------------
# Returns every PrimeItem with its PartRequirement rows nested
# (PrimeItemOut, list of them). This is static catalog data — same for
# every user, doesn't touch InventoryEntry at all.

# --- GET /inventory --------------------------------------------------
# Returns the current user's owned quantities, by part
# (list of InventoryEntryOut). Only rows belonging to get_current_user()
# — filter by user_id.

# --- PUT /inventory/{part_requirement_id} --------------------------
# Sets how many of that part the current user owns. Steps:
#   1. does an InventoryEntry already exist for
#      (current_user.id, part_requirement_id)?
#   2. if yes, update its quantity_owned
#   3. if no, create one
#   (this "update or create" pattern is sometimes called an upsert)
#
# Worth checking: does part_requirement_id in the URL actually exist?
# What should happen if it doesn't?

# --- GET /sets -------------------------------------------------------
# The core logic of the whole app. For each PrimeItem:
#   1. get its PartRequirement rows
#   2. for each one, look up the current user's InventoryEntry
#      (missing entry = 0 owned, per the blueprint — don't require a
#      row to exist)
#   3. compare quantity_owned vs quantity_required for every part
#   4. derive status:
#        - complete: every part meets its required quantity
#        - partial:  at least one part owned, but not enough for all
#        - none:     zero parts owned toward this item
#   5. return a SetStatusOut per item, including per-part detail so a
#      partial set can show exactly what's missing
#
# This is computed at request time, not stored anywhere — there's no
# "status" column to keep in sync.
