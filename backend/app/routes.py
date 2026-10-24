# routes.py — outline only, no implementation yet.
#
# Every route here (per the blueprint) requires a valid token — each
# should depend on get_current_user from auth.py, and every query should
# be scoped to that user. There is no route here that reads or writes
# another user's data.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from .auth import get_current_user
from .database import get_db
from .models import InventoryEntry, PartRequirement, PrimeItem, User
from .schemas import InventoryEntryOut, InventoryEntryUpdate, PartRequirementOut, PartStatusOut, PrimeItemOut, SetStatusOut

router = APIRouter(tags=["inventory"])


# --- GET /items ------------------------------------------------------
# Returns every PrimeItem with its PartRequirement rows nested
# (PrimeItemOut, list of them). This is static catalog data — same for
# every user, doesn't touch InventoryEntry at all.
@router.get("/items", dependencies=[Depends(get_current_user)], response_model=list[PrimeItemOut])
def get_items(db: Session=Depends(get_db)):
    return db.scalars(select(PrimeItem)).all()


# --- GET /inventory --------------------------------------------------
# Returns the current user's owned quantities, by part
# (list of InventoryEntryOut). Only rows belonging to get_current_user()
# — filter by user_id.
@router.get("/inventory", response_model=list[InventoryEntryOut])
def get_inventory(current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    return db.scalars(select(InventoryEntry).where(InventoryEntry.user_id == current_user.id)).all()


# --- PUT /inventory/{part_requirement_id} --------------------------
# Sets how many of that part the current user owns. Steps:
#   1. does an InventoryEntry already exist for
#      (current_user.id, part_requirement_id)?
#   2. if yes, update its quantity_owned
#   3. if no, create one
#   (this "update or create" pattern is sometimes called an upsert)
@router.put("/inventory/{part_requirement_id}", response_model=InventoryEntryOut)
def get_part_requirement(entry_update: InventoryEntryUpdate, part_requirement_id: int, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    inventory_entry = db.scalar(select(InventoryEntry).where(and_(InventoryEntry.user_id == current_user.id, 
                                                  InventoryEntry.part_requirement_id == part_requirement_id)))
    
    if not inventory_entry:
        inventory_entry = InventoryEntry(user_id=current_user.id, part_requirement_id=part_requirement_id, quantity_owned=entry_update.quantity_owned)
        db.add(inventory_entry)
    else:
        inventory_entry.quantity_owned = entry_update.quantity_owned

    db.commit()
    return inventory_entry


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
