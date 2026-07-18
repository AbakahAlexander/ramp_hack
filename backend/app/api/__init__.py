from fastapi import APIRouter

from app.api import dashboard, feedback, gyms, insights, issues, public, routes, staff

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(gyms.router)
api_router.include_router(staff.router)
api_router.include_router(routes.router)
api_router.include_router(feedback.router)
api_router.include_router(issues.router)
api_router.include_router(dashboard.router)
api_router.include_router(public.router)
api_router.include_router(insights.router)
