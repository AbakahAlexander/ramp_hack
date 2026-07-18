from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid4())


class FeedbackOutcome(str, Enum):
    SENT = "sent"
    TRIED = "tried"
    PROJECTING = "projecting"


class IssueStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class IssueType(str, Enum):
    SHARP = "sharp"
    BROKEN_HOLD = "broken_hold"
    SPINNER = "spinner"
    UNSAFE = "unsafe"
    OTHER = "other"


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    route_id: Mapped[str] = mapped_column(String(36), ForeignKey("routes.id"), nullable=False, index=True)
    outcome: Mapped[str] = mapped_column(String(40), nullable=False)
    perceived_grade: Mapped[str | None] = mapped_column(String(40), nullable=True)
    enjoyment: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
    tags: Mapped[str] = mapped_column(Text, default="")  # comma-separated
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    contributor_id: Mapped[str] = mapped_column(String(64), nullable=False)  # anonymized
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    route = relationship("Route", back_populates="feedback")

    @property
    def tag_list(self) -> list[str]:
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class IssueReport(Base):
    __tablename__ = "issue_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    route_id: Mapped[str] = mapped_column(String(36), ForeignKey("routes.id"), nullable=False, index=True)
    issue_type: Mapped[str] = mapped_column(String(40), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default=IssueStatus.OPEN.value, index=True)
    owner_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("staff_users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    route = relationship("Route", back_populates="issues")
    owner = relationship("StaffUser")
