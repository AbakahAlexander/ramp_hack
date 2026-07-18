from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import api_router
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.services.seed import seed_if_empty

# Ensure models are registered on metadata
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    if settings.seed_on_startup:
        db = SessionLocal()
        try:
            seed_if_empty(db)
        finally:
            db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "Crux API — staff dashboard and climber QR feedback for climbing-gym routesetting.\n\n"
            "Hackathon MVP: **no auth** — all endpoints are open. Demo gym is seeded on startup."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
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

    @application.get("/health", tags=["Health"])
    def health():
        return {"status": "ok", "version": __version__}

    return application


app = create_app()
