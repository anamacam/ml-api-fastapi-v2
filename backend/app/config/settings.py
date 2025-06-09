"""
⚙️ Configuración de la aplicación por entornos
"""
import os
import logging
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import Field, validator, ValidationError
from pydantic_settings import BaseSettings

# Configurar logger
logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Entornos disponibles"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Configuración de la aplicación basada en variables de entorno"""
    
    # 🌍 Entorno
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Entorno de ejecución"
    )
    debug: bool = Field(
        default=True,
        description="Modo debug"
    )
    
    # 🤖 Machine Learning
    ml_models_path: Path = Field(
        default=Path("data/models"),
        description="Directorio de modelos ML"
    )
    use_real_models: bool = Field(
        default=True,
        description="Usar modelos reales (false para mocks en testing)"
    )
    max_prediction_batch_size: int = Field(
        default=100,
        description="Tamaño máximo de batch para predicciones"
    )
    
    # 🗄️ Base de datos
    database_url: Optional[str] = Field(
        default=None,
        description="URL de conexión a la base de datos"
    )
    
    # 🔐 Seguridad
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Clave secreta para JWT"
    )
    
    # 📊 API
    api_title: str = Field(
        default="ML API FastAPI v2",
        description="Título de la API"
    )
    api_version: str = Field(
        default="2.0.0",
        description="Versión de la API"
    )
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Orígenes permitidos para CORS"
    )
    
    # 📁 Archivos
    upload_dir: Path = Field(
        default=Path("data/uploads"),
        description="Directorio de uploads"
    )
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Tamaño máximo de archivo en bytes"
    )
    
    # 📝 Logging
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging"
    )
    log_file: Optional[Path] = Field(
        default=Path("data/logs/app.log"),
        description="Archivo de logs"
    )
    
    @property
    def is_development(self) -> bool:
        """¿Está en modo desarrollo?"""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_testing(self) -> bool:
        """¿Está en modo testing?"""
        return self.environment == Environment.TESTING
    
    @property
    def is_production(self) -> bool:
        """¿Está en modo producción?"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def should_use_real_models(self) -> bool:
        """¿Debería usar modelos reales?"""
        # En testing siempre usar mocks, en otros entornos según configuración
        if self.is_testing:
            return False
        return self.use_real_models
    
    @validator('secret_key')
    def validate_secret_key(cls, v, values):
        """Validar que la secret key sea segura en producción"""
        environment = values.get('environment')
        if environment == Environment.PRODUCTION:
            if v == "dev-secret-key-change-in-production":
                raise ValueError("SECRET_KEY must be changed in production environment")
            if len(v) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v
    
    @validator('debug')
    def validate_debug(cls, v, values):
        """Validar que debug esté desactivado en producción"""
        environment = values.get('environment')
        if environment == Environment.PRODUCTION and v is True:
            raise ValueError("DEBUG must be False in production environment")
        return v
    
    @validator('ml_models_path')
    def validate_models_path(cls, v):
        """Validar que el path de modelos sea seguro"""
        path_str = str(v)
        dangerous_patterns = [
            "..",
            "/etc/",
            "/var/",
            "/root/",
            "System32",
            "Windows\\System32",
            "passwd",
            "shadow",
            "secrets"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in path_str:
                raise ValueError(f"Dangerous path detected: {path_str}")
        
        return v
    
    @validator('use_real_models', pre=True)
    def validate_use_real_models(cls, v, values):
        """Validar y proveer fallback seguro para use_real_models"""
        # Si es un string corrupto, usar fallback seguro
        if isinstance(v, str):
            if v.lower() in ['true', '1', 'yes', 'on']:
                return True
            elif v.lower() in ['false', '0', 'no', 'off']:
                return False
            else:
                # Fallback seguro: False para testing/desarrollo, True para producción
                environment = values.get('environment', 'development')
                return environment == 'production'
        return v
    
    def __init__(self, **values):
        """Inicialización con validaciones y logging"""
        # Validar variables requeridas en producción
        if values.get('environment') == 'production':
            required_vars = ['secret_key']
            missing = []
            
            for var in required_vars:
                # Verificar en values o variables de entorno
                if var not in values:
                    env_var = var.upper()
                    if env_var not in os.environ:
                        missing.append(var)
            
            if missing:
                raise ValueError(f"Required environment variables missing for production: {missing}")
        
        # Inicialización normal
        super().__init__(**values)
        
        # Logging de advertencias de seguridad
        self._log_security_warnings()
        
        # Hacer configuración inmutable
        self.__dict__['_frozen'] = True
    
    def _log_security_warnings(self):
        """Loggear advertencias de seguridad"""
        if self.secret_key == "dev-secret-key-change-in-production":
            logger.warning("Using default SECRET_KEY - change in production!")
        
        if self.debug and self.environment != Environment.DEVELOPMENT:
            logger.warning(f"Debug mode enabled in {self.environment} environment")
    
    def __setattr__(self, name, value):
        """Prevenir modificaciones después de inicialización"""
        if hasattr(self, '_frozen') and self._frozen:
            raise AttributeError(f"Configuration is immutable - cannot modify {name}")
        super().__setattr__(name, value)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Mapeo de variables de entorno
        fields = {
            "environment": {"env": "ENV"},
            "ml_models_path": {"env": "ML_MODELS_PATH"},
            "use_real_models": {"env": "USE_REAL_MODELS"},
            "database_url": {"env": "DATABASE_URL"},
            "secret_key": {"env": "SECRET_KEY"},
        }


# 🌍 Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """Obtener configuración (útil para inyección de dependencias)"""
    return settings 