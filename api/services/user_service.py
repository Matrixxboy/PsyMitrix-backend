from fastapi import Depends, HTTPException
from models.pydantic_models import UserCreate, UserUpdate
from typing import Annotated
from api.services.auth_service import AuthService
from core.db import get_mongo_db
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class UserService:
    def __init__(self, db: Annotated[AsyncIOMotorClient, Depends(get_mongo_db)], auth_service: AuthService = Depends()):
        self.db = db
        self.users_collection = self.db.get_collection("users")
        self.auth_service = auth_service

    async def get_user_by_username(self, username: str):
        user = await self.users_collection.find_one({"username": username})
        return user

    async def get_user_by_email(self, email: str):
        user = await self.users_collection.find_one({"email": email})
        return user

    async def get_user_by_id(self, user_id: str):
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user

    async def create_user(self, user: UserCreate):
        hashed_password = self.auth_service.get_password_hash(user.password)
        user_data = user.model_dump()
        user_data["hashed_password"] = hashed_password
        del user_data["password"]
        
        # Default hf_adapter_id to None if not provided
        if "huggingface_adapter_id" not in user_data:
            user_data["huggingface_adapter_id"] = None

        result = await self.users_collection.insert_one(user_data)
        new_user = await self.users_collection.find_one({"_id": result.inserted_id})
        return new_user

    async def update_user(self, user_id: str, user_update: UserUpdate):
        db_user = await self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Handle password hashing if password is being updated
        if "password" in update_data:
            update_data["hashed_password"] = self.auth_service.get_password_hash(update_data["password"])
            del update_data["password"]

        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return updated_user

    async def delete_user(self, user_id: str):
        db_user = await self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await self.users_collection.delete_one({"_id": ObjectId(user_id)})