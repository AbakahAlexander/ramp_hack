from datetime import datetime
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_demo_gym
from app.models.gym import Gym, Wall
from app.models.route import Route
from app.models.user import StaffUser
from app.schemas import (
    FromImageBatchOut,
    RouteCreate,
    RouteDetailOut,
    RouteListOut,
    RouteStatusUpdate,
    RouteUpdate,
)
from app.services.metrics import route_to_detail

router = APIRouter(prefix="/routes", tags=["Routes"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _gym_walls(db: Session, gym_id: str) -> list[str]:
    return [w.id for w in db.query(Wall).filter(Wall.gym_id == gym_id).all()]


def _get_route_for_gym(db: Session, route_id: str, gym_id: str) -> Route:
    route = (
        db.query(Route)
        .options(joinedload(Route.wall), joinedload(Route.setters), joinedload(Route.holds))
        .filter(Route.id == route_id)
        .first()
    )
    if not route or not route.wall or route.wall.gym_id != gym_id:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


def _apply_holds(route: Route, wall: Wall, hold_inputs: list) -> None:
    from app.services.seed import build_holds_for_wall

    try:
        route.holds = build_holds_for_wall(wall, hold_inputs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _save_upload(raw: bytes, content_type: str | None) -> str:
    ext = ".jpg"
    if content_type == "image/png":
        ext = ".png"
    elif content_type == "image/webp":
        ext = ".webp"
    name = f"{uuid4().hex}{ext}"
    path = UPLOAD_DIR / name
    path.write_bytes(raw)
    return name


@router.post(
    "/from-image",
    response_model=FromImageBatchOut,
    status_code=201,
    summary="Extract all routes from one wall photo → XML + DB",
    response_description="Every detected route persisted, plus editable wall scene XML",
    description=(
        "Upload one wall photo. Auto-detects every colored route (no color picker). "
        "Returns cartoon-ready <wall> XML with holds at positions/shapes/colors, "
        "and creates one DB route per color line."
    ),
)
async def create_routes_from_image(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
    wall_id: Annotated[str, Form()],
    image: Annotated[UploadFile, File(description="Photo of the wall / routes")],
):
    from datetime import date

    from app.services.route_xml import build_wall_xml, route_fragment_xml
    from app.services.vision_route import extract_all_routes_from_image

    wall = db.query(Wall).filter(Wall.id == wall_id, Wall.gym_id == gym.id).first()
    if not wall:
        raise HTTPException(status_code=400, detail="Invalid wall_id")

    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty image upload")
    if len(raw) > 12_000_000:
        raise HTTPException(status_code=400, detail="Image too large (max ~12MB)")

    try:
        batch = extract_all_routes_from_image(
            raw,
            image.content_type or "image/jpeg",
            wall.grid_cols or 8,
            wall.grid_rows or 10,
            wall_name=wall.name,
            wall_id=wall.id,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Vision extraction failed: {exc}") from exc

    created_ids: list[str] = []
    persisted: list[dict] = []
    for extracted in batch.get("routes") or []:
        route = Route(
            wall_id=wall.id,
            name=extracted.get("name") or "New route",
            color_identifier=extracted.get("color_identifier") or "Mixed",
            display_color=extracted.get("display_color") or "#888888",
            assigned_grade=extracted.get("assigned_grade") or "V?",
            styles=",".join(extracted.get("styles") or ["technical"]),
            status="active",
            set_date=date.today(),
            notes=extracted.get("notes"),
            photo_url=None,
            scene_xml=None,
        )
        _apply_holds(route, wall, extracted.get("holds") or [])
        db.add(route)
        db.flush()
        fragment = route_fragment_xml(
            {
                "id": route.id,
                "name": route.name,
                "color_identifier": route.color_identifier,
                "display_color": route.display_color,
                "assigned_grade": route.assigned_grade,
                "holds": extracted.get("holds") or [],
            }
        )
        route.scene_xml = fragment
        created_ids.append(route.id)
        persisted.append(
            {
                "id": route.id,
                "name": route.name,
                "color_identifier": route.color_identifier,
                "display_color": route.display_color,
                "assigned_grade": route.assigned_grade,
                "holds": extracted.get("holds") or [],
            }
        )

    db.commit()

    # Rebuild wall XML with real route UUIDs
    wall_xml = build_wall_xml(wall_name=wall.name, wall_id=wall.id, routes=persisted)
    details = [route_to_detail(_get_route_for_gym(db, rid, gym.id), db) for rid in created_ids]
    return FromImageBatchOut(
        routes=details,
        xml=wall_xml,
        provider=batch.get("provider") or "opencv",
        total=len(details),
    )


@router.get(
    "/photos/{filename}",
    summary="Serve an uploaded route photo",
    include_in_schema=False,
)
def get_route_photo(filename: str):
    safe = Path(filename).name
    path = UPLOAD_DIR / safe
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Photo not found")
    media = "image/jpeg"
    if safe.endswith(".png"):
        media = "image/png"
    elif safe.endswith(".webp"):
        media = "image/webp"
    return FileResponse(path, media_type=media)


@router.get(
    "",
    response_model=RouteListOut,
    summary="List / filter routes",
    response_description="Routes with computed health metrics",
    description=(
        "Staff route inventory. Each item includes `health`, `holds` (sequence/type/location), "
        "and `cells` for lighting the board."
    ),
)
def list_routes(
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
    status: str | None = Query(
        default=None,
        description="active | needs_review | scheduled_for_strip | archived",
        examples=["active"],
    ),
    wall_id: str | None = Query(default=None, description="Filter to one wall UUID"),
    zone: str | None = Query(default=None, description="Filter by wall zone, e.g. Front"),
    grade: str | None = Query(default=None, description="Assigned grade, e.g. V3"),
    style: str | None = Query(default=None, description="Style tag substring, e.g. slab"),
    setter_id: str | None = Query(default=None, description="Staff UUID of a setter"),
    include_archived: bool = Query(default=False, description="Include archived routes"),
    q: str | None = Query(default=None, description="Search color identifier or notes"),
):
    wall_ids = _gym_walls(db, gym.id)
    query = (
        db.query(Route)
        .options(joinedload(Route.wall), joinedload(Route.setters), joinedload(Route.holds))
        .filter(Route.wall_id.in_(wall_ids))
    )
    if status:
        query = query.filter(Route.status == status)
    elif not include_archived:
        query = query.filter(Route.status != "archived")
    if wall_id:
        query = query.filter(Route.wall_id == wall_id)
    if grade:
        query = query.filter(Route.assigned_grade == grade)
    if zone:
        query = query.join(Wall).filter(Wall.zone == zone)
    if style:
        query = query.filter(Route.styles.contains(style))
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Route.color_identifier.ilike(like))
            | (Route.notes.ilike(like))
            | (Route.name.ilike(like))
        )

    routes = query.order_by(Route.set_date.desc()).all()
    if setter_id:
        routes = [r for r in routes if any(s.id == setter_id for s in r.setters)]

    items = [route_to_detail(r, db) for r in routes]
    return RouteListOut(items=items, total=len(items))


@router.post(
    "",
    response_model=RouteDetailOut,
    status_code=201,
    summary="Create a route with hold sequence",
    response_description="Created route including holds",
    description=(
        "Gym owner / setter creates a route: metadata + ordered `holds` on the wall grid.\n\n"
        "Each hold needs `sequence_index`, `row`, `col`, and `hold_type` "
        "(jug | crimp | pinch | sloper | foothold | volume | pocket | other)."
    ),
)
def create_route(
    payload: RouteCreate,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    wall = db.query(Wall).filter(Wall.id == payload.wall_id, Wall.gym_id == gym.id).first()
    if not wall:
        raise HTTPException(status_code=400, detail="Invalid wall_id for demo gym")

    setters: list[StaffUser] = []
    if payload.setter_ids:
        setters = (
            db.query(StaffUser)
            .filter(StaffUser.id.in_(payload.setter_ids), StaffUser.gym_id == gym.id)
            .all()
        )
        if len(setters) != len(set(payload.setter_ids)):
            raise HTTPException(status_code=400, detail="One or more setter_ids invalid")

    route = Route(
        wall_id=payload.wall_id,
        name=payload.name or payload.color_identifier,
        photo_url=payload.photo_url,
        color_identifier=payload.color_identifier,
        display_color=payload.display_color,
        assigned_grade=payload.assigned_grade,
        grade_system=payload.grade_system,
        styles=",".join(payload.styles),
        status=payload.status,
        set_date=payload.set_date,
        reset_date=payload.reset_date,
        notes=payload.notes,
    )
    route.setters = setters
    if payload.holds:
        _apply_holds(route, wall, payload.holds)
    db.add(route)
    db.commit()
    db.refresh(route)
    route = _get_route_for_gym(db, route.id, gym.id)
    return route_to_detail(route, db)


@router.get(
    "/{route_id}",
    response_model=RouteDetailOut,
    summary="Get route detail",
    response_description="Full route record + health signals",
    description="Staff detail view for one route, including feedback-derived health metrics.",
)
def get_route(
    route_id: str,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    route = _get_route_for_gym(db, route_id, gym.id)
    return route_to_detail(route, db)


@router.patch(
    "/{route_id}",
    response_model=RouteDetailOut,
    summary="Update a route",
    response_description="Updated route detail",
    description="Partial update. Only send fields you want to change.",
)
def update_route(
    route_id: str,
    payload: RouteUpdate,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    route = _get_route_for_gym(db, route_id, gym.id)
    data = payload.model_dump(exclude_unset=True)
    if "styles" in data and data["styles"] is not None:
        data["styles"] = ",".join(data["styles"])
    setter_ids = data.pop("setter_ids", None)
    holds_in = data.pop("holds", None)
    if "wall_id" in data:
        wall = db.query(Wall).filter(Wall.id == data["wall_id"], Wall.gym_id == gym.id).first()
        if not wall:
            raise HTTPException(status_code=400, detail="Invalid wall_id")
    for k, v in data.items():
        setattr(route, k, v)
    if setter_ids is not None:
        setters = (
            db.query(StaffUser)
            .filter(StaffUser.id.in_(setter_ids), StaffUser.gym_id == gym.id)
            .all()
        )
        route.setters = setters
    if holds_in is not None:
        _apply_holds(route, route.wall, holds_in)
    route.updated_at = datetime.utcnow()
    db.commit()
    route = _get_route_for_gym(db, route_id, gym.id)
    return route_to_detail(route, db)


@router.patch(
    "/{route_id}/status",
    response_model=RouteDetailOut,
    summary="Change route status only",
    response_description="Route with new status",
    description="Shortcut to move a route between active / needs_review / scheduled_for_strip / archived.",
)
def update_status(
    route_id: str,
    payload: RouteStatusUpdate,
    gym: Annotated[Gym, Depends(get_demo_gym)],
    db: Annotated[Session, Depends(get_db)],
):
    route = _get_route_for_gym(db, route_id, gym.id)
    route.status = payload.status
    route.updated_at = datetime.utcnow()
    db.commit()
    route = _get_route_for_gym(db, route_id, gym.id)
    return route_to_detail(route, db)
