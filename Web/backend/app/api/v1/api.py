from fastapi import APIRouter
from app.api.v1.endpoints import auth, violations, users, cameras, statistics, officer, reports, citizen

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(violations.router, prefix="/violations", tags=["violations"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(officer.router, prefix="/officer", tags=["officer"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(citizen.router, prefix="/citizen", tags=["citizen"])
