"""Lightweight SQLite column/table ensure for hackathon (no Alemmic)."""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_schema(engine: Engine) -> None:
    if not str(engine.url).startswith("sqlite"):
        return

    insp = inspect(engine)
    with engine.begin() as conn:
        if "walls" in insp.get_table_names():
            wall_cols = {c["name"] for c in insp.get_columns("walls")}
            if "wall_key" not in wall_cols:
                conn.execute(text("ALTER TABLE walls ADD COLUMN wall_key VARCHAR(40) DEFAULT ''"))
            if "grid_cols" not in wall_cols:
                conn.execute(text("ALTER TABLE walls ADD COLUMN grid_cols INTEGER DEFAULT 8"))
            if "grid_rows" not in wall_cols:
                conn.execute(text("ALTER TABLE walls ADD COLUMN grid_rows INTEGER DEFAULT 10"))

        if "routes" in insp.get_table_names():
            route_cols = {c["name"] for c in insp.get_columns("routes")}
            if "name" not in route_cols:
                conn.execute(text("ALTER TABLE routes ADD COLUMN name VARCHAR(200) DEFAULT ''"))
            if "display_color" not in route_cols:
                conn.execute(text("ALTER TABLE routes ADD COLUMN display_color VARCHAR(20) DEFAULT '#888888'"))
