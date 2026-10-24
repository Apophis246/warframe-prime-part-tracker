"""Load the prime item catalog from the WFCD dataset into the database.

Not a route and not test data: this is the only thing that ever creates
PrimeItem / PartRequirement rows, locally and in production. It never touches
User or InventoryEntry - those belong to real users.

Safe to re-run. Intended to run on a schedule (weekly cron on the VM) so new
primes appear without anyone editing the app.

    docker compose run --rm backend python -m app.seed
"""

import httpx
import logging

from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import PrimeItem, PartRequirement, ItemType

logger = logging.getLogger(__name__)


# Pinned to a commit, not master: WFCD changed their schema on 2026-09-23 and
# dropped `name` and `tradable` from components, which broke the parser below.
# 859cb0a7f290 (2026-09-23) is the last commit with the full format.
# Bump this when you want newer items, and re-check the format still matches.
BASE_URL = "https://raw.githubusercontent.com/WFCD/warframe-items/859cb0a7f290/data/json"
SOURCES = {
    "Warframes.json": ItemType.WARFRAME,
    "Primary.json": ItemType.WEAPON,
    "Secondary.json": ItemType.WEAPON,
    "Melee.json": ItemType.WEAPON
}


def fetch_sources():
    """
    Download every source file up front and return a list of
    (item_type, parsed_json) pairs.
    """
    payloads = []

    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        for filename, item_type in SOURCES.items():
            response = client.get(BASE_URL + "/" + filename)
            response.raise_for_status()
            payloads.append((item_type, response.json()))

    return payloads


def extract_catalog(payloads):
    """
    Flatten the raw JSON into a simple list of
    (name, item_type, [(part_name, quantity), ...])
    so the database code below doesn't have to know anything about WFCD's
    field names.
    """
    catalog = []
    seen = set()

    for item_type, entries in payloads:
        for entry in entries:
            name = entry["name"]
            if "prime" not in name.lower() or name in seen:
                continue

            parts = [(component["name"], component["itemCount"]) 
                     for component in entry.get("components") or [] 
                     if component.get("tradable")]
            
            if not parts:
                continue

            seen.add(name)
            catalog.append((name, item_type, parts))
    
    return catalog


def seed():
    Base.metadata.create_all(engine)
    catalog = extract_catalog(fetch_sources())

    new_items = 0
    new_parts = 0

    with SessionLocal() as session:
        existing = set(session.scalars(select(PrimeItem.name)))

        for name, item_type, parts in catalog:
            if name in existing:
                continue
            item = PrimeItem(name=name, item_type=item_type)
            for part_name, quantity in parts:
                PartRequirement(part_name=part_name, quantity_required=quantity, prime_item=item)
                new_parts+=1
            session.add(item)
            new_items+=1
        
        session.commit()
    
    logger.info("%d items in source; added %d new items and %d new parts", len(catalog), new_items, new_parts)
    

# --- Run as a script -------------------------------------------------------
# basicConfig belongs here, in the entrypoint, not at module level: importing a
# module should never reconfigure logging for the whole program. Anything that
# imports seed.py still gets the logger, just under its own config.

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    seed()


# --- Expected result, to check against (as of September 3, 2026) -------------------------------------
#   150 items, 551 part rows (50 warframes, 100 weapons)
#   Second run adds 0 of each.
#
#   Volt Prime   [warframe] Blueprint x1, Chassis x1, Neuroptics x1, Systems x1
#   Braton Prime [weapon]   Barrel x1, Blueprint x1, Receiver x1, Stock x1
#   Fang Prime   [weapon]   Blade x2, Blueprint x1, Handle x2
#   Glaive Prime [weapon]   Blade x2, Blueprint x1, Disc x1
#   Venka Prime  [weapon]   Blades x2, Blueprint x1, Gauntlet x2
#
#   Zero PartRequirement rows named "Orokin Cell" / "Argon Crystal" /
#   "Neurodes" / "Forma".
#
#   (The blueprint PDF lists Glaive Prime without its Disc — the wiki and the
#   dataset both confirm the Disc is required. The list above is correct.)
