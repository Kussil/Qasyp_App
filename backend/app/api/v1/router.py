from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, users, survey, demo, matches

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(survey.router)
api_router.include_router(demo.router)
api_router.include_router(matches.router)
