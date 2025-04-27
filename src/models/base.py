from typing import Dict, List
import uuid
from sqlalchemy import (
    Column, Integer, String, Text, Float,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    DeclarativeBase, relationship
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        "user_id", String,
        primary_key=True,
        nullable=False
    )

    name = Column("name", String, nullable=False)
    # у пользователя может быть несколько вишлистов
    wishlists = relationship(
        "WishList",
        back_populates="user",
        cascade="all, delete-orphan"
    )



    def to_dict(self) -> Dict:
        return {
            "user_id": str(self.user_id),
            "name": str(self.name),
            "wishlists": [wl.to_dict() for wl in self.wishlists]
        }


class Celery(Base):
    __tablename__ = "celery"

    celery_id = Column(
        "celery_id", UUID(as_uuid=True),
        primary_key=True
    )
    category = Column("category", String)

    photo = Column(
        "photo_id", String
    )
    label = Column(
        "label", String
    )
    about = Column(
        "about", Text
    )
    cost = Column(
        "cost", Float
    )

    # все элементы, где этот товар попал в вишлист
    wishlist_items = relationship(
        "WishListItem",
        back_populates="celery",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict:
        return {
            "celery_id": str(self.celery_id),
            "photo": self.photo,
            "category": self.category,
            "label": self.label,
            "about": self.about,
            "cost": self.cost
        }


class WishList(Base):
    __tablename__ = "wishlists"

    id = Column(
        "wishlist_id", UUID(as_uuid=True),
        primary_key=True
    )
    user_id = Column(
        "user_id", String,
        ForeignKey("users.user_id"),
        nullable=False
    )
    name = Column(
        "name", String,
        nullable=False
    )
    list_type = Column(
        "list_type", Text,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="wishlists"
    )
    items = relationship(
        "WishListItem",
        back_populates="wishlist",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "list_type": self.list_type,
            "items": [item.to_dict() for item in self.items]
        }

    


class WishListItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    wishlist_id = Column(
        "wishlist_id", UUID(as_uuid=True),
        ForeignKey("wishlists.wishlist_id"),
        nullable=False
    )
    celery_id = Column(
        "celery_id", UUID(as_uuid=True),
        ForeignKey("celery.celery_id"),
        nullable=False
    )
    status = Column(
        "status", String,
        nullable=False,
        default="active"
    )
    count = Column(
        "count", Integer,
        nullable=False,
        default=1
    )

    # навигационные атрибуты
    wishlist = relationship(
        "WishList",
        back_populates="items"
    )
    celery = relationship(
        "Celery",
        back_populates="wishlist_items"
    )

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id),
            "wishlist_id": str(self.wishlist_id),
            "celery_id": str(self.celery_id),
            "status": self.status,
            "count": self.count,
            "celery": self.celery.to_dict() if self.celery else None
        }
