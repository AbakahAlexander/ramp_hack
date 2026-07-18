from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import api_router
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.schema_migrate import ensure_schema
from app.services.seed import clear_all_routes, seed_if_empty

import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_schema(engine)
    settings = get_settings()
    if settings.seed_on_startup:
        db = SessionLocal()
        try:
            seed_if_empty(db)
            if settings.clear_routes_on_startup:
                clear_all_routes(db)
        finally:
            db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "## Crux API\n\n"
            "Staff dashboard + climber QR feedback for climbing-gym routesetting.\n\n"
            "**Hackathon MVP:** no auth — all endpoints are open.\n\n"
            "### Quick start for frontend\n"
            "1. `GET /api/v1/seed-status` — confirm demo gym/walls are loaded\n"
            "2. `POST /api/v1/routes/from-image` — upload a photo → AI grid holds\n"
            "3. `GET /api/v1/routes` — inventory (empty until you add routes)\n"
            "4. Climber loop: `GET /api/v1/public/routes/{id}` → "
            "`POST /api/v1/public/routes/{id}/feedback`\n\n"
            "Demo gym **Summit Lab Climbing** seeds walls + staff only — "
            "no hardcoded routes."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {"name": "Health", "description": "Liveness check for Koyeb / load balancers"},
            {"name": "Meta", "description": "Seed / data sanity checks"},
            {"name": "Gym & Walls", "description": "Gym profile and wall inventory"},
            {"name": "Staff", "description": "Staff and setter list (for route attribution)"},
            {"name": "Routes", "description": "Route CRUD, filters, and health metrics"},
            {"name": "Feedback", "description": "Staff view of climber feedback"},
            {
                "name": "Public (climber QR)",
                "description": "Unauthenticated mobile/QR climber flow",
            },
            {"name": "Issues", "description": "Safety and hold issue queue"},
            {
                "name": "Dashboard",
                "description": "Overview, reset planner, coverage, setter insights",
            },
            {
                "name": "AI Insights",
                "description": (
                    "Paste climber feedback → OpenAI recommends keep / monitor / change_out per route"
                ),
            },
        ],
    )
    origins = settings.cors_origin_list or ["*"]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins != ["*"] else ["*"],
        allow_credentials=origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)

    @application.get(
        "/health",
        tags=["Health"],
        summary="Health check",
        description="Returns ok when the API process is up. Used by Koyeb health checks.",
        response_description="Status and API version",
    )
    def health():
        return {"status": "ok", "version": __version__}

    return application


app = create_app()
