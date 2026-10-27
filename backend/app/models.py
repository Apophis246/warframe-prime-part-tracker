# SQLAlchemy models — the four tables the whole app is built on.
#
# PrimeItem and PartRequirement are the catalog (what exists, what it needs);
# User and InventoryEntry are per-user data. Set completeness is computed in
# routes.py at request time and never stored.

import enum

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class ItemType(enum.Enum):
    WARFRAME = "warframe"
    WEAPON = "weapon"
    ARCHWING = "archwing"
    SENTINEL = "sentinel"


class User(Base):
    """
    Fields:
        id               -> primary key
        username         -> string, should be unique
        email            -> string, should be unique
        password_hash    -> string (never store the raw password)

    Relationship:
        one User -> many InventoryEntry (a user's owned parts)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()

    inventory_entries: Mapped[list["InventoryEntry"]] = relationship(back_populates="user")


class PrimeItem(Base):
    """
    Fields:
        id           -> primary key
        name         -> string, e.g. "Volt Prime"
        item_type    -> constrained to "warframe" or "weapon" (enum column, or a
                        plain string + validation — your call)

    Relationship:
        one PrimeItem -> many PartRequirement (the parts that make up this item)
    """

    __tablename__ = "prime_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    item_type: Mapped[ItemType]

    part_requirements: Mapped[list["PartRequirement"]] = relationship(back_populates="prime_item")


class PartRequirement(Base):
    """
    Fields:
        id                   -> primary key
        prime_item_id        -> foreign key -> PrimeItem.id
        part_name            -> string, e.g. "Neuroptics", "Blueprint"
        quantity_required    -> integer (most are 1, some weapons need 2 — see
                                Fang Prime / Glaive Prime in the blueprint)

    Relationships:
        many PartRequirement -> one PrimeItem  (belongs to)
        one PartRequirement -> many InventoryEntry (one per user who owns any)
    """

    __tablename__ = "part_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    prime_item_id: Mapped[int] = mapped_column(ForeignKey("prime_items.id"))
    part_name: Mapped[str] = mapped_column()
    quantity_required: Mapped[int] = mapped_column()

    prime_item: Mapped[PrimeItem] = relationship(back_populates="part_requirements")
    inventory_entries: Mapped[list["InventoryEntry"]] = relationship(back_populates="part_requirement")


class InventoryEntry(Base):
    """
    Fields:
        id                     -> primary key
        user_id                -> foreign key -> User.id
        part_requirement_id    -> foreign key -> PartRequirement.id
        quantity_owned         -> integer, how many of that part this user has

    Relationships:
        many InventoryEntry -> one User            (belongs to)
        many InventoryEntry -> one PartRequirement  (belongs to)
    """

    __tablename__ = "inventory_entries"
    __table_args__ = (UniqueConstraint("user_id", "part_requirement_id", name="uq_user_part"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    part_requirement_id: Mapped[int] = mapped_column(ForeignKey("part_requirements.id"))
    quantity_owned: Mapped[int] = mapped_column()

    user: Mapped[User] = relationship(back_populates="inventory_entries")
    part_requirement: Mapped[PartRequirement] = relationship(back_populates="inventory_entries")
