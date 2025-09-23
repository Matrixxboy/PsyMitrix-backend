# api/services/auth_service.py
# Service for handling authentication logic.

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends, HTTPException, status
from core.db import get_mongo_db
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from core.config import settings
from models.pydantic_models import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

class AuthService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.users_collection = self.db.get_collection("users")

    async def get_user(self, email: str) -> Optional[dict]:
        user = await self.users_collection.find_one({"email": email})
        return user

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception
        
        user = await self.users_collection.find_one({"email": token_data.email})
        
        if user is None:
            raise credentials_exception
        return user

    async def get_current_active_user(self, current_user: dict = Depends(get_current_user)):
        return current_user

# Dependency function to get the AuthService instance
def get_auth_service(db: AsyncIOMotorClient = Depends(get_mongo_db)):
    """
    Dependency function to provide a properly instantiated AuthService.
    """
    return AuthService(db)

# The missing dependency function
async def get_current_authenticated_user(
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Depends(oauth2_scheme)
):
    """
    A dependency that returns the authenticated user dictionary.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # Use the injected service to get the user
    user = await auth_service.get_user(email=token_data.email)
    
    if user is None:
        raise credentials_exception
    return user