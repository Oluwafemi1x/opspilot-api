from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class Organization(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)

    memberships = relationship("Membership", back_populates="organization", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="organization", cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="organization", cascade="all, delete-orphan")
