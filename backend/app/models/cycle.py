from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _uuid() -> str:
    return str(uuid4())


class SettingCycle(Base):
    __tablename__ = "setting_cycles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    gym_id: Mapped[str] = mapped_column(String(36), ForeignKey("gyms.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_wall_ids: Mapped[str] = mapped_column(Text, default="")  # comma-separated
    routes_to_strip: Mapped[str] = mapped_column(Text, default="")
    routes_added: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
