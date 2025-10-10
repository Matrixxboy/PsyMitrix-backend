# utils/response_helper.py

from fastapi.responses import JSONResponse
from typing import Any, Optional

def make_response(status_code: int, code: str, message: str, data: Optional[Any] = None):
    """Standardized JSON response wrapper"""
    response_body = {
        "http_status": status_code,
        "http_code": code,
        "message": message,
    }#
    if data is not None:
        response_body["data"] = data

    return JSONResponse(status_code=status_code, content=response_body)
