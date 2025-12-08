from fastapi import APIRouter

from app.api.v1.endpoints import general, questions, report, transcribe

api_router = APIRouter()

api_router.include_router(general.router, tags=["General"])
api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
api_router.include_router(report.router, prefix="/report", tags=["Report"])
api_router.include_router(transcribe.router, tags=["Transcribe"]) # /transcribe is root level in app.py, so no prefix or handle carefully
