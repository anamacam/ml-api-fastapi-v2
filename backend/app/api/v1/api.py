from fastapi import APIRouter

from app.api.v1.endpoints import health, predict, models, upload, websocket

api_router = APIRouter()

# Incluir todos los endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(predict.router, prefix="/predict", tags=["predictions"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"]) 