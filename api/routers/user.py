# api/routers/user.py
# Router for user-related endpoints.

from fastapi import APIRouter, HTTPException, Depends
from models.pydantic_models import UserCreate, UserUpdate
from api.services import user_service
from api.services.auth_service import AuthService
from typing import Dict, Any

router = APIRouter()

# Point-wise comment: Endpoint to create a new user
@router.post("/", response_model=Dict[str, Any])
async def create_user(
    user: UserCreate,
    auth_service: AuthService = Depends()
):
    db_user = await auth_service.get_user(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # The service now returns the user part of the created data
    created_user_data = await user_service.create_user(user=user)
    return created_user_data

# Point-wise comment: Endpoint to get the full decrypted data for the current user
@router.get("/me/data", response_model=Dict[str, Any])
async def get_user_full_data(current_user: dict = Depends(AuthService().get_current_user)):
    # The get_current_user dependency already fetches and decrypts the data
    return current_user

# Point-wise comment: Endpoint to update the current user's information
@router.put("/me", response_model=Dict[str, Any])
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(AuthService().get_current_user),
    user_service: user_service.UserService = Depends(user_service.UserService)
):
    updated_user = await user_service.update_user(str(current_user["_id"]), user_update)
    return updated_user
