from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.middleware import add_middleware

# Configurar logging
setup_logging()

# Crear instancia FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para Machine Learning con FastAPI",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar middleware personalizado
add_middleware(app)

# Incluir routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Servir archivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Endpoint raíz
@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "🚀 ML API FastAPI v2",
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "running"
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "service": "ml-api-fastapi-v2",
        "version": settings.VERSION
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 