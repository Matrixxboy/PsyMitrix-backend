from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from api.services.auth_service import AuthService
from api.services.hf_service import HFKeyService

router = APIRouter()

class HFKeyRequest(BaseModel):
    hf_api_key: str

@router.post("/store-hf-key", status_code=status.HTTP_200_OK)
async def store_huggingface_api_key(
    request: HFKeyRequest,
    current_user: dict = Depends(AuthService().get_current_user),
    hf_key_service: HFKeyService = Depends()
):
    """
    Stores the Hugging Face API key for the authenticated user.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    await hf_key_service.store_hf_api_key(user_id, request.hf_api_key)
    return {"message": "Hugging Face API key stored successfully."}
