from datetime import date, datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid4())


class RouteStatus(str, Enum):
    ACTIVE = "active"
    NEEDS_REVIEW = "needs_review"
    SCHEDULED_FOR_STRIP = "scheduled_for_strip"
    ARCHIVED = "archived"


class HoldType(str, Enum):
    JUG = "jug"
    CRIMP = "crimp"
    PINCH = "pinch"
    SLOPER = "sloper"
    FOOTHOLD = "foothold"
    VOLUME = "volume"
    POCKET = "pocket"
    OTHER = "other"


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
    name: Mapped[str] = mapped_column(String(200), default="")
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    color_identifier: Mapped[str] = mapped_column(String(80), nullable=False)
    display_color: Mapped[str] = mapped_column(String(20), default="#888888")
    assigned_grade: Mapped[str] = mapped_column(String(40), nullable=False)
    grade_system: Mapped[str] = mapped_column(String(50), default="V-scale")
    styles: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default=RouteStatus.ACTIVE.value, index=True)
    set_date: Mapped[date] = mapped_column(Date, nullable=False)
    reset_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Editable cartoon scene fragment (<route>...</route>) for optimization / re-import
    scene_xml: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wall = relationship("Wall", back_populates="routes")
    setters = relationship("StaffUser", secondary=route_setters, lazy="joined")
    holds = relationship(
        "RouteHold",
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="RouteHold.sequence_index",
        lazy="joined",
    )
    feedback = relationship("Feedback", back_populates="route", cascade="all, delete-orphan")
    issues = relationship("IssueReport", back_populates="route", cascade="all, delete-orphan")

    @property
    def style_list(self) -> list[str]:
        if not self.styles:
            return []
        return [s.strip() for s in self.styles.split(",") if s.strip()]

    @property
    def cell_indices(self) -> list[int]:
        return [h.cell_index for h in self.holds]


class RouteHold(Base):
    """One hold on a route, in climb order.

    Spatial fields (x, y, size) are the source of truth for heatmap display.
    row/col/cell_index are derived coarse grid values for legacy clients.
    """

    __tablename__ = "route_holds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    route_id: Mapped[str] = mapped_column(String(36), ForeignKey("routes.id"), nullable=False, index=True)
    sequence_index: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 = start
    cell_index: Mapped[int] = mapped_column(Integer, nullable=False)  # legacy row-major
    row: Mapped[int] = mapped_column(Integer, nullable=False)  # legacy 0 = top
    col: Mapped[int] = mapped_column(Integer, nullable=False)  # legacy 0 = left
    x: Mapped[float] = mapped_column(Float, default=0.5)  # 0 = left, 1 = right
    y: Mapped[float] = mapped_column(Float, default=0.5)  # 0 = top, 1 = bottom
    size: Mapped[float] = mapped_column(Float, default=0.05)  # relative diameter
    hold_type: Mapped[str] = mapped_column(String(40), default=HoldType.OTHER.value)
    notes: Mapped[str | None] = mapped_column(String(200), nullable=True)

    route = relationship("Route", back_populates="holds")
