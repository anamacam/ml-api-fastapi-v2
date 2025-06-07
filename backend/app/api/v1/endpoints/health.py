from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import redis
import psutil
import time
from datetime import datetime
from typing import Dict, Any

from app.core.config import settings
from app.models.database import get_db

router = APIRouter()

@router.get("/")
async def health_basic():
    """Health check básico"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ml-api-fastapi-v2",
        "version": settings.VERSION
    }

@router.get("/detailed")
async def health_detailed(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Health check detallado con estado de servicios"""
    
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ml-api-fastapi-v2",
        "version": settings.VERSION,
        "uptime": time.time(),
        "checks": {}
    }
    
    # Check base de datos
    try:
        db.execute("SELECT 1")
        health_data["checks"]["database"] = {
            "status": "healthy",
            "connection": "ok",
            "url": settings.DATABASE_URL.replace(settings.POSTGRES_PASSWORD, "***")
        }
    except Exception as e:
        health_data["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_data["checks"]["redis"] = {
            "status": "healthy",
            "connection": "ok"
        }
    except Exception as e:
        health_data["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # Check sistema
    try:
        health_data["checks"]["system"] = {
            "status": "healthy",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    except Exception as e:
        health_data["checks"]["system"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    return health_data

@router.get("/liveness")
async def health_liveness():
    """Liveness probe para Kubernetes"""
    return {"status": "alive"}

@router.get("/readiness")
async def health_readiness(db: Session = Depends(get_db)):
    """Readiness probe para Kubernetes"""
    try:
        # Verificar que la base de datos esté disponible
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service not ready") 