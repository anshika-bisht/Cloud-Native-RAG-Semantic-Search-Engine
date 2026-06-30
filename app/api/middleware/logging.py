import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger

class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Latency: {process_time:.4f}s")
        
        # Add latency header for client debugging
        response.headers["X-Process-Time"] = str(process_time)
        return response
