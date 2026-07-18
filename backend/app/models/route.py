from datetime import date, datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid4())


class RouteStatus(str, Enum):
    ACTIVE = "active"
    NEEDS_REVIEW = "needs_review"
    SCHEDULED_FOR_STRIP = "scheduled_for_strip"
    ARCHIVED = "archived"


route_setters = Table(
    "route_setters",
    Base.metadata,
    Column("route_id", String(36), ForeignKey("routes.id"), primary_key=True),
    Column("staff_id", String(36), ForeignKey("staff_users.id"), primary_key=True),
)


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    wall_id: Mapped[str] = mapped_column(String(36), ForeignKey("walls.id"), nullable=False, index=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    color_identifier: Mapped[str] = mapped_column(String(80), nullable=False)
    assigned_grade: Mapped[str] = mapped_column(String(40), nullable=False)
    grade_system: Mapped[str] = mapped_column(String(50), default="V-scale")
    styles: Mapped[str] = mapped_column(Text, default="")  # comma-separated for SQLite simplicity
    status: Mapped[str] = mapped_column(String(40), default=RouteStatus.ACTIVE.value, index=True)
    set_date: Mapped[date] = mapped_column(Date, nullable=False)
    reset_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wall = relationship("Wall", back_populates="routes")
    setters = relationship("StaffUser", secondary=route_setters, lazy="joined")
    feedback = relationship("Feedback", back_populates="route", cascade="all, delete-orphan")
    issues = relationship("IssueReport", back_populates="route", cascade="all, delete-orphan")

    @property
    def style_list(self) -> list[str]:
        if not self.styles:
            return []
        return [s.strip() for s in self.styles.split(",") if s.strip()]
