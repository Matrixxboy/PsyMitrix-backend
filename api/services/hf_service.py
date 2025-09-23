from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from core.db import get_mongo_db

class HFKeyService:
    def __init__(self, db: AsyncIOMotorClient = Depends(get_mongo_db)):
        self.db = db

    async def store_hf_api_key(self, user_id: str, hf_api_key: str):
        # In a real application, you would encrypt and securely store the API key
        # For now, we'll simulate storage.
        print(f"Storing Hugging Face API key for user {user_id}: {hf_api_key[:5]}...")
        users_collection = self.db.get_collection("users")
        await users_collection.update_one(
            {"_id": user_id},
            {"$set": {"hf_api_key": hf_api_key}},
            upsert=True
        )
