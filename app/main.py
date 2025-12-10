import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
# from pydub import AudioSegment

from app.api.v1.router import api_router
from app.api.Psy.router import api_router as psy_api_router
from app.utils.http_constants import HTTP_STATUS, HTTP_CODE
from app.utils.response_helper import make_response

# Configure AudioSegment
# Note: These paths should ideally be in environment variables or configuration
# AudioSegment.converter = "/var/www/python-counsellor-india/ffmpeg-bin/ffmpeg"

app = FastAPI(title="MBAI Python Backend", version="1.0.0")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Convert FastAPI’s validation error into your standard structure
    error_messages = []
    # print(request) # Log request if needed
    for err in exc.errors():
        loc = " -> ".join(map(str, err.get("loc", [])))
        msg = err.get("msg", "")
        error_messages.append(f"{loc}: {msg}")

    return make_response(
        HTTP_STATUS["BAD_REQUEST"],
        HTTP_CODE["VALIDATION"],
        "Validation error",
        {"errors": error_messages}
    )

# Include Routers
app.include_router(api_router) # All routes are under / or specific prefixes in the router
app.include_router(prefix="/psy",router=psy_api_router) # All routes are under / or specific prefixes in the router

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is healthy"}
