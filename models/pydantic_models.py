# models/pydantic_models.py
# Pydantic models for data validation and serialization.

from pydantic import BaseModel, EmailStr, Field
from typing import Any, Dict, Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    # Use this method for Pydantic v2
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler) -> Dict[str, Any]:
        return {"type": "string"}

class UserBase(BaseModel):
    email: EmailStr
    
class UserCreate(UserBase):
    password: str
    huggingface_adapter_id: Optional[str] = None

class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    huggingface_adapter_id: Optional[str] = None

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    huggingface_adapter_id: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        json_encoders = {
            ObjectId: str
        }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None