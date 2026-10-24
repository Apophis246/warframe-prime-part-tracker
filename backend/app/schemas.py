# Pydantic models — separate from the SQLAlchemy models in
# models.py. SQLAlchemy models describe database tables; these describe
# the shape of JSON going in and out of the API. Keeping them separate
# means you control exactly what a client can send (e.g. never accept a
# raw password_hash) and exactly what gets returned (e.g. never return
# password_hash at all).

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator
from typing import List, Literal, Optional, Self

# --- Auth schemas -----------------------------------------------------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    @model_validator(mode='after')
    def check_valid_info(self) -> Self:
        if self.username is None and self.email is None:
            raise ValueError("You must provide a username or email")
        return self

class Token(BaseModel):
    access_token: str
    token_type: str

# --- PrimeItem / PartRequirement schemas (read-only) -----------------
class PartRequirementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    part_name: str
    quantity_required: int
    
class PrimeItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    item_type: str
    part_requirements: List[PartRequirementOut]

# --- InventoryEntry schemas -------------------------------------------
class InventoryEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    part_requirement_id: int
    quantity_owned: int

class InventoryEntryUpdate(BaseModel):
    quantity_owned: int

# --- Sets schema ---------------------------------------------------------
class PartStatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    part_name: str
    quantity_required: int
    quantity_owned: int

class SetStatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    status: Literal["complete", "partial", "none"]
    part_status: List[PartStatusOut]
