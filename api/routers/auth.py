# api/routers/auth.py
# Router for authentication endpoints.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.pydantic_models import Token
from api.services.auth_service import get_auth_service  # <-- Changed import here
from security.encryption import decrypt_data
import json

router = APIRouter()

# Point-wise comment: Endpoint to login and get an access token
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: get_auth_service = Depends(get_auth_service)  # <-- Changed injection here
):
    user = await auth_service.get_user(email=form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decrypt the user data to get the hashed_password
    try:
        decrypted_data_str = decrypt_data(user['data'])
        decrypted_user_data = json.loads(decrypted_data_str)
        hashed_password = decrypted_user_data.get("hashed_password")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error decrypting user data",
        )

    if not hashed_password or not auth_service.verify_password(form_data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(
        data={"sub": user['email']}
    )
    return {"access_token": access_token, "token_type": "bearer"}