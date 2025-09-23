# main.py
# Main entry point for the FastAPI application.
# This file initializes the FastAPI app, includes routers, and sets up middleware.

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routers import auth, generation, user, hf_key
from secure_log.middleware import SecureLogMiddleware
from core.config import settings
from core.db import connect_to_mongo, close_mongo_connection, connect_to_qdrant

# Point-wise comment: Initialize the FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)
print(f"Starting {settings.PROJECT_NAME} version {settings.PROJECT_VERSION}")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Point-wise comment: Add middleware
# The secure log middleware is added here to create a tamper-proof audit trail.
app.add_middleware(SecureLogMiddleware)

# Point-wise comment: Add event handlers for database connections
# Connect to MongoDB and Qdrant on startup, and close connections on shutdown.
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("startup", connect_to_qdrant)
app.add_event_handler("shutdown", close_mongo_connection)

# Point-wise comment: Include API routers
# Routers for authentication, generation, and user management are included here.
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/users", tags=["users"])
app.include_router(generation.router, prefix="/api/generate", tags=["generation"])
app.include_router(hf_key.router, prefix="/api/hf-key", tags=["huggingface"])

# Point-wise comment: Root endpoint
# A simple root endpoint to confirm the API is running.
@app.get("/")
async def root():
    return {"message": "Welcome to PsyMitrix AI Backend"}