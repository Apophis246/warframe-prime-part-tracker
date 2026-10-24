# The tracker's four endpoints. Every route requires a valid token — either
# via the router-level dependency or by taking current_user as a parameter —
# and every query is scoped to that user. No route reads or writes another
# user's data.

from fastapi import APIRouter, Depends
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from .auth import get_current_user
from .database import get_db
from .models import InventoryEntry, PrimeItem, User
from .schemas import (
    InventoryEntryOut,
    InventoryEntryUpdate,
    PartStatusOut,
    PrimeItemOut,
    SetStatusOut,
)

router = APIRouter(tags=["inventory"])


# The static catalog — identical for every user, so it needs a token but not
# the user behind it.
@router.get("/items", dependencies=[Depends(get_current_user)], response_model=list[PrimeItemOut])
def get_items(db: Session=Depends(get_db)):
    return db.scalars(select(PrimeItem)).all()


@router.get("/inventory", response_model=list[InventoryEntryOut])
def get_inventory(current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    return db.scalars(select(InventoryEntry).where(InventoryEntry.user_id == current_user.id)).all()


# Upsert: the unique constraint on (user_id, part_requirement_id) means there
# is at most one row per user per part, so this either updates that row or
# creates it.
@router.put("/inventory/{part_requirement_id}", response_model=InventoryEntryOut)
def set_inventory_quantity(entry_update: InventoryEntryUpdate, part_requirement_id: int, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    inventory_entry = db.scalar(select(InventoryEntry).where(and_(InventoryEntry.user_id == current_user.id,
                                                  InventoryEntry.part_requirement_id == part_requirement_id)))

    if not inventory_entry:
        inventory_entry = InventoryEntry(user_id=current_user.id, part_requirement_id=part_requirement_id, quantity_owned=entry_update.quantity_owned)
        db.add(inventory_entry)
    else:
        inventory_entry.quantity_owned = entry_update.quantity_owned

    db.commit()
    return inventory_entry


# The point of the app. Status is derived per request, never stored, so it
# can't go stale. A part with no InventoryEntry row counts as zero owned.
@router.get("/sets", response_model=list[SetStatusOut])
def get_sets(current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    set_statuses = []
    prime_items = db.scalars(select(PrimeItem)).all()
    user_inventory = db.scalars(select(InventoryEntry).where(InventoryEntry.user_id == current_user.id)).all()
    items_owned = {item.part_requirement_id: item.quantity_owned for item in user_inventory}

    for item in prime_items:
        part_statuses = []
        for requirement in item.part_requirements:
            part_statuses.append(PartStatusOut(part_name=requirement.part_name,
                                               quantity_required=requirement.quantity_required,
                                               quantity_owned=items_owned.get(requirement.id, 0)))

        # Order matters: partial is whatever is left over.
        if all(part.quantity_owned >= part.quantity_required for part in part_statuses):
            set_status = "complete"
        elif all(part.quantity_owned == 0 for part in part_statuses):
            set_status = "none"
        else:
            set_status = "partial"

        set_statuses.append(SetStatusOut(id=item.id, name=item.name,
                                         status=set_status,
                                         part_status=part_statuses))

    return set_statuses
