from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configuración centralizada de la aplicación"""
    
    # Información del proyecto
    PROJECT_NAME: str = "ML API FastAPI v2"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "API para Machine Learning con FastAPI, React y monitoreo completo"
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend Web
        "http://localhost:3001",  # Frontend Admin
        "http://localhost:80",    # Nginx
        "http://localhost:8080",  # Desarrollo
    ]
    
    # Base de datos PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ml_api_db"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_URL(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Archivos
    UPLOAD_DIR: str = "data/uploads"
    MODELS_DIR: str = "data/models"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # WebSocket
    WEBSOCKET_PORT: int = 8001
    
    # Monitoreo
    PROMETHEUS_PORT: int = 8002
    GRAFANA_PORT: int = 3000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "data/logs/app.log"
    
    # Desarrollo
    DEBUG: bool = True
    RELOAD: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

# Crear directorios necesarios
def create_directories():
    """Crear directorios necesarios si no existen"""
    dirs = [
        settings.UPLOAD_DIR,
        settings.MODELS_DIR,
        Path(settings.LOG_FILE).parent,
        "data/postgres",
        "data/redis",
        "data/grafana"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

# Crear directorios al importar
create_directories() 