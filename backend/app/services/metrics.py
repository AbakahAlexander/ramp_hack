"""Route health metrics and dashboard helpers."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
from statistics import median

from sqlalchemy.orm import Session

from app.models.feedback import Feedback, IssueReport, IssueStatus
from app.models.route import Route, RouteStatus
from app.models.gym import Wall
from app.schemas import (
    CoverageCell,
    CoverageMatrixOut,
    FeedbackOut,
    RouteDetailOut,
    RouteHealth,
    SetterBrief,
    SetterInsightOut,
    WallHealthBucket,
)

# Simple V-scale ordering for calibration / median
V_GRADES = [f"V{i}" for i in range(0, 17)]


def _parse_styles(styles: str | list[str]) -> list[str]:
    if isinstance(styles, list):
        return styles
    if not styles:
        return []
    return [s.strip() for s in styles.split(",") if s.strip()]


def grade_rank(grade: str) -> int | None:
    g = grade.strip().upper()
    if g in V_GRADES:
        return V_GRADES.index(g)
    # tolerate lowercase v3 etc
    for i, vg in enumerate(V_GRADES):
        if g == vg.upper():
            return i
    return None


def insight_quality(sample_size: int, newest: datetime | None) -> str:
    if sample_size < 3:
        return "low"
    recent = newest and newest >= datetime.utcnow() - timedelta(days=14)
    if sample_size >= 10 and recent:
        return "high"
    if sample_size >= 5:
        return "medium"
    return "low"


def compute_route_health(route: Route, db: Session) -> RouteHealth:
    feedback: list[Feedback] = (
        db.query(Feedback).filter(Feedback.route_id == route.id).order_by(Feedback.created_at).all()
    )
    open_issues = (
        db.query(IssueReport)
        .filter(
            IssueReport.route_id == route.id,
            IssueReport.status != IssueStatus.RESOLVED.value,
        )
        .count()
    )

    sends = sum(1 for f in feedback if f.outcome == "sent")
    attempts = sum(1 for f in feedback if f.outcome == "tried")
    projects = sum(1 for f in feedback if f.outcome == "projecting")
    unique = len({f.contributor_id for f in feedback})

    perceived = [f.perceived_grade for f in feedback if f.perceived_grade]
    perceived_counts = dict(Counter(perceived))
    median_grade = None
    ranks = [grade_rank(g) for g in perceived if grade_rank(g) is not None]
    if ranks:
        mid = int(median(ranks))
        median_grade = V_GRADES[mid] if 0 <= mid < len(V_GRADES) else None

    enjoyments = [f.enjoyment for f in feedback if f.enjoyment is not None]
    enjoyment_avg = round(sum(enjoyments) / len(enjoyments), 2) if enjoyments else None

    tags: list[str] = []
    for f in feedback:
        tags.extend(f.tag_list)
    tag_counts = dict(Counter(tags))

    age_days = (date.today() - route.set_date).days if route.set_date else 0

    # Engagement trend: compare last 7 days vs previous 7
    now = datetime.utcnow()
    recent = [f for f in feedback if f.created_at >= now - timedelta(days=7)]
    prior = [
        f
        for f in feedback
        if now - timedelta(days=14) <= f.created_at < now - timedelta(days=7)
    ]
    if not feedback:
        trend = "unknown"
    elif len(recent) > len(prior) + 1:
        trend = "rising"
    elif len(recent) + 1 < len(prior):
        trend = "declining"
    else:
        trend = "steady"

    newest = feedback[-1].created_at if feedback else None
    quality = insight_quality(len(feedback), newest)

    # Transparent review score (0-100): age, declining engagement, issues, grade mismatch
    score = 0.0
    score += min(age_days / 60 * 40, 40)  # older → higher
    if trend == "declining":
        score += 20
    score += min(open_issues * 15, 30)
    assigned_rank = grade_rank(route.assigned_grade)
    if assigned_rank is not None and ranks:
        delta = abs(median(ranks) - assigned_rank)
        if delta >= 1:
            score += min(delta * 10, 20)
    if route.status == RouteStatus.NEEDS_REVIEW.value:
        score += 15
    if route.reset_date and route.reset_date <= date.today() + timedelta(days=14):
        score += 15

    return RouteHealth(
        sends=sends,
        attempts=attempts,
        projects=projects,
        unique_contributors=unique,
        perceived_grades=perceived_counts,
        median_perceived_grade=median_grade,
        enjoyment_avg=enjoyment_avg,
        enjoyment_count=len(enjoyments),
        tag_counts=tag_counts,
        open_issues=open_issues,
        age_days=age_days,
        engagement_trend=trend,  # type: ignore[arg-type]
        insight_quality=quality,  # type: ignore[arg-type]
        review_score=round(min(score, 100), 1),
    )


def route_to_detail(route: Route, db: Session) -> RouteDetailOut:
    from app.schemas import RouteHoldOut

    health = compute_route_health(route, db)
    wall = route.wall
    holds = [
        RouteHoldOut(
            id=h.id,
            sequence_index=h.sequence_index,
            cell_index=h.cell_index,
            row=h.row,
            col=h.col,
            x=float(h.x) if h.x is not None else 0.5,
            y=float(h.y) if h.y is not None else 0.5,
            size=float(h.size) if h.size is not None else 0.05,
            hold_type=h.hold_type,
            notes=h.notes,
        )
        for h in sorted(route.holds, key=lambda x: x.sequence_index)
    ]
    return RouteDetailOut(
        id=route.id,
        wall_id=route.wall_id,
        name=route.name or route.color_identifier,
        photo_url=route.photo_url,
        color_identifier=route.color_identifier,
        display_color=route.display_color or "#888888",
        assigned_grade=route.assigned_grade,
        grade_system=route.grade_system,
        styles=route.style_list,
        status=route.status,
        set_date=route.set_date,
        reset_date=route.reset_date,
        notes=route.notes,
        scene_xml=getattr(route, "scene_xml", None),
        setters=[SetterBrief(id=s.id, full_name=s.full_name) for s in route.setters],
        holds=holds,
        cells=[h.cell_index for h in holds],
        created_at=route.created_at,
        updated_at=route.updated_at,
        health=health,
        wall_name=wall.name if wall else None,
        wall_key=wall.wall_key if wall else None,
        zone=wall.zone if wall else None,
        grid_cols=wall.grid_cols if wall else None,
        grid_rows=wall.grid_rows if wall else None,
    )


def feedback_to_out(f: Feedback) -> FeedbackOut:
    return FeedbackOut(
        id=f.id,
        route_id=f.route_id,
        outcome=f.outcome,
        perceived_grade=f.perceived_grade,
        enjoyment=f.enjoyment,
        tags=f.tag_list,
        comment=f.comment,
        created_at=f.created_at,
    )


def build_wall_health(db: Session, gym_id: str) -> list[WallHealthBucket]:
    walls = db.query(Wall).filter(Wall.gym_id == gym_id, Wall.is_active.is_(True)).all()
    buckets: list[WallHealthBucket] = []
    for wall in walls:
        routes = (
            db.query(Route)
            .filter(Route.wall_id == wall.id, Route.status != RouteStatus.ARCHIVED.value)
            .all()
        )
        grade_counts: Counter[str] = Counter()
        style_counts: Counter[str] = Counter()
        for r in routes:
            grade_counts[r.assigned_grade] += 1
            for s in r.style_list:
                style_counts[s] += 1

        gaps: list[str] = []
        beginner = sum(grade_counts[g] for g in ("V0", "V1", "V2") if g in grade_counts)
        if beginner == 0 and wall.angle_type in ("slab", "vertical"):
            gaps.append(f"No beginner routes on {wall.name}")
        if "slab" in style_counts or wall.angle_type == "slab":
            easy_slab = sum(
                1
                for r in routes
                if "slab" in r.style_list and grade_rank(r.assigned_grade) is not None and grade_rank(r.assigned_grade) <= 2  # type: ignore[operator]
            )
            if wall.angle_type == "slab" and easy_slab == 0:
                gaps.append(f"No easy slab routes on {wall.name}")
        if not routes:
            gaps.append(f"{wall.name} has no active routes")

        buckets.append(
            WallHealthBucket(
                wall_id=wall.id,
                wall_name=wall.name,
                zone=wall.zone,
                angle_type=wall.angle_type,
                grade_counts=dict(grade_counts),
                style_counts=dict(style_counts),
                total_active=len(routes),
                gaps=gaps,
            )
        )
    return buckets


def build_coverage_matrix(db: Session, gym_id: str) -> CoverageMatrixOut:
    walls = db.query(Wall).filter(Wall.gym_id == gym_id, Wall.is_active.is_(True)).all()
    cells: list[CoverageCell] = []
    gaps: list[str] = []
    for wall in walls:
        routes = (
            db.query(Route)
            .filter(Route.wall_id == wall.id, Route.status != RouteStatus.ARCHIVED.value)
            .all()
        )
        combo: Counter[tuple[str, str]] = Counter()
        for r in routes:
            styles = r.style_list or ["unspecified"]
            for s in styles:
                combo[(r.assigned_grade, s)] += 1
        for (grade, style), count in combo.items():
            cells.append(
                CoverageCell(
                    wall_id=wall.id,
                    wall_name=wall.name,
                    grade=grade,
                    style=style,
                    count=count,
                )
            )
        # gap heuristics
        grades_present = {r.assigned_grade for r in routes}
        if wall.angle_type == "overhang" and not any(
            grade_rank(g) is not None and grade_rank(g) <= 3 for g in grades_present  # type: ignore[operator]
        ):
            gaps.append(f"{wall.name}: overhang routes missing easier grades")
        if wall.angle_type == "slab" and "V0" not in grades_present and "V1" not in grades_present:
            gaps.append(f"{wall.name}: no easy slab grades")

    return CoverageMatrixOut(cells=cells, gaps=gaps)


def build_reset_reasons(route: Route, health: RouteHealth) -> list[str]:
    reasons: list[str] = []
    if health.age_days >= 28:
        reasons.append(f"On wall {health.age_days} days")
    if health.engagement_trend == "declining":
        reasons.append("Declining engagement")
    if health.open_issues:
        reasons.append(f"{health.open_issues} open issue(s)")
    if health.median_perceived_grade and health.median_perceived_grade != route.assigned_grade:
        reasons.append(
            f"Grade mismatch: assigned {route.assigned_grade}, perceived ~{health.median_perceived_grade}"
        )
    if route.status == RouteStatus.NEEDS_REVIEW.value:
        reasons.append("Marked needs review")
    if route.reset_date and route.reset_date <= date.today() + timedelta(days=14):
        reasons.append(f"Reset planned {route.reset_date.isoformat()}")
    if not reasons:
        reasons.append("Low priority")
    return reasons


def build_setter_insights(db: Session, gym_id: str) -> list[SetterInsightOut]:
    from app.models.user import StaffUser

    setters = (
        db.query(StaffUser)
        .filter(StaffUser.gym_id == gym_id, StaffUser.is_setter.is_(True), StaffUser.is_active.is_(True))
        .all()
    )
    results: list[SetterInsightOut] = []
    for setter in setters:
        routes = [r for r in db.query(Route).all() if any(s.id == setter.id for s in r.setters)]
        # filter to gym via wall
        routes = [r for r in routes if r.wall and r.wall.gym_id == gym_id]

        calibrations: list[str] = []
        enjoyments: list[float] = []
        style_mix: Counter[str] = Counter()
        wall_mix: Counter[str] = Counter()
        sample = 0

        for route in routes:
            health = compute_route_health(route, db)
            sample += health.sends + health.attempts + health.projects
            for s in route.style_list:
                style_mix[s] += 1
            if route.wall:
                wall_mix[route.wall.name] += 1
            if health.enjoyment_avg is not None:
                enjoyments.append(health.enjoyment_avg)
            if (
                health.median_perceived_grade
                and health.insight_quality != "low"
                and health.median_perceived_grade != route.assigned_grade
            ):
                calibrations.append(
                    f"{route.color_identifier} {route.assigned_grade} on {route.wall.name if route.wall else '?'}: "
                    f"perceived ~{health.median_perceived_grade} (n={health.sends + health.attempts})"
                )

        avg_enjoy = round(sum(enjoyments) / len(enjoyments), 2) if enjoyments else None
        quality = insight_quality(sample, datetime.utcnow() if sample else None)

        results.append(
            SetterInsightOut(
                setter_id=setter.id,
                setter_name=setter.full_name,
                route_count=len(routes),
                grade_calibration_notes=calibrations,
                avg_enjoyment=avg_enjoy,
                style_mix=dict(style_mix),
                wall_mix=dict(wall_mix),
                sample_size=sample,
                insight_quality=quality,  # type: ignore[arg-type]
            )
        )
    return results
