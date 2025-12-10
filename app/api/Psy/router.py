from fastapi import APIRouter
from app.api.Psy.endpoints import general
from app.api.Psy.endpoints import assessments

api_router = APIRouter()

api_router.include_router(general.router, tags=["General"])
api_router.include_router(assessments.router, tags=["Assessments"])

