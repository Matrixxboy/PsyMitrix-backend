# api/routers/generation.py
# Router for the AI response generation endpoint.

from fastapi import APIRouter, Depends, HTTPException
from api.services import generation_service
from api.services.auth_service import get_current_authenticated_user # <-- Import the new dependency
from typing import Annotated

router = APIRouter()

# Point-wise comment: Endpoint to generate a personalized AI response
@router.post("/", response_model=str)
async def generate_response_endpoint(
    prompt: str,
    current_user: Annotated[dict, Depends(get_current_authenticated_user)] # <-- Use the new dependency
):
    if not current_user.get('huggingface_adapter_id'):
        raise HTTPException(status_code=400, detail="User does not have a Hugging Face adapter configured.")
    
    response = await generation_service.generate_response(
        prompt=prompt,
        user_id=str(current_user['_id']),
        adapter_id=current_user['huggingface_adapter_id']
    )
    return response