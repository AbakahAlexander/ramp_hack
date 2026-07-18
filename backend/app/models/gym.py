from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid4())


class Gym(Base):
    __tablename__ = "gyms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    locations: Mapped[list] = mapped_column(JSON, default=list)
    grade_system: Mapped[str] = mapped_column(String(50), default="V-scale")  # V-scale | French | etc
    tag_vocabulary: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    walls: Mapped[list["Wall"]] = relationship(back_populates="gym", cascade="all, delete-orphan")
    staff: Mapped[list["StaffUser"]] = relationship(back_populates="gym", cascade="all, delete-orphan")


class Wall(Base):
    __tablename__ = "walls"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    gym_id: Mapped[str] = mapped_column(String(36), ForeignKey("gyms.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    zone: Mapped[str] = mapped_column(String(120), default="")
    angle_type: Mapped[str] = mapped_column(String(80), default="vertical")  # slab, vertical, overhang, cave
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    gym: Mapped["Gym"] = relationship(back_populates="walls")
    routes: Mapped[list["Route"]] = relationship(back_populates="wall")


# Late imports for type hints / relationship resolution
from app.models.user import StaffUser  # noqa: E402
from app.models.route import Route  # noqa: E402
