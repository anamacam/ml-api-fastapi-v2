from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable

# Configurar logger
logger = logging.getLogger(__name__)

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware para medir tiempo de respuesta"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Procesar request
        response = await call_next(request)
        
        # Calcular tiempo
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log del request
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        
        return response

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar ID único a cada request"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import uuid
        request_id = str(uuid.uuid4())
        
        # Agregar a headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response

def add_middleware(app: FastAPI) -> None:
    """Agregar todos los middlewares a la aplicación"""
    
    # Timing middleware
    app.add_middleware(TimingMiddleware)
    
    # Request ID middleware  
    app.add_middleware(RequestIDMiddleware) 