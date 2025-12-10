from fastapi import APIRouter
from app.utils.http_constants import HTTP_STATUS, HTTP_CODE
from app.utils.response_helper import make_response

router=APIRouter()

@router.get("/")
def read_root():
    return make_response(
        HTTP_STATUS["OK"],
        HTTP_CODE["OK"],
        message="Psy API workig well 🚀",
        data={}
    )
