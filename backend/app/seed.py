# seed.py — outline only, no implementation yet.
#
# A standalone script (not a route) that populates PrimeItem and
# PartRequirement with the five curated items from the blueprint, so
# there's real data to build and test everything else against.

# The five items and their parts (from the blueprint — verify quantities
# against wiki.warframe.com's Duplicate Prime Parts Required page before
# trusting these, per the blueprint's own instruction):
#
#   Volt Prime (warframe):   Neuroptics x1, Chassis x1, Systems x1, Blueprint x1
#   Mag Prime  (warframe):   Neuroptics x1, Chassis x1, Systems x1, Blueprint x1
#   Braton Prime (weapon):   Barrel x1, Receiver x1, Stock x1, Blueprint x1
#   Fang Prime   (weapon):   Blade x2, Handle x2, Blueprint x1
#   Glaive Prime (weapon):   Blade x2, Blueprint x1
#
# Structure:
#   1. open a database session (reuse get_db()/SessionLocal from
#      database.py — or a standalone session, your call, since this
#      runs outside a request)
#   2. for each item: create the PrimeItem row, then its PartRequirement
#      rows
#   3. guard against running this twice — either check "does this item
#      already exist" before inserting, or make it safe to wipe and
#      re-seed. Running it twice and silently duplicating everything is
#      the failure mode to avoid.
#
# How this eventually runs (undecided/for later): a one-off local
# command, or something the container runs on startup — worth deciding
# once Docker is in the picture, not now.
