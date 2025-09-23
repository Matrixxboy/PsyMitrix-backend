# secure_log/middleware.py
# Middleware for creating a secure, tamper-proof audit log.

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from secure_log.log_manager import add_log
import time
import json

class SecureLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Point-wise comment: Log the request details before processing
        log_entry = {
            "timestamp": int(time.time()),
            "method": request.method,
            "url": str(request.url),
            "headers": {k: v for k, v in request.headers.items() if k.lower() in ['user-agent', 'referer']},
        }
        
        try:
            add_log(log_entry)
        except Exception as e:
            print(f"CRITICAL: Failed to write to secure audit log: {e}")

        response = await call_next(request)
        return response
