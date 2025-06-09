"""
Modelos Pydantic para API - FASE LIMPIEZA: Migrados a Pydantic V2.

REFACTORED: Eliminando warnings y migrando a Pydantic V2
- Migración @validator → @field_validator
- Protected namespaces configurados
- ConfigDict para configuración moderna
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

# ===== REQUEST MODELS =====

class PredictionFeatures(BaseModel):
    """Modelo para features de predicción con validación robusta."""
    model_config = ConfigDict(protected_namespaces=())
    
    age: float = Field(..., ge=0, le=150, description="Edad en años")
    income: float = Field(..., ge=0, description="Ingresos anuales")
    category: str = Field(..., min_length=1, description="Categoría del cliente")
    score: float = Field(..., ge=0, le=1, description="Score de 0 a 1")
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        """Validar categorías permitidas."""
        allowed = ['premium', 'standard', 'basic', 'unknown_category']
        if v not in allowed:
            raise ValueError(f'Category must be one of: {allowed}')
        return v

class PredictionRequest(BaseModel):
    """Request para predicción mejorado."""
    model_config = ConfigDict(protected_namespaces=())
    
    features: Dict[str, Any] = Field(..., description="Features para predicción")
    model_id: Optional[str] = Field(
        default="default_model",
        description="ID del modelo a usar"
    )
    include_validation_details: Optional[bool] = Field(
        default=True,
        description="Incluir detalles de validación en respuesta"
    )

class ModelUploadRequest(BaseModel):
    """Request para subida de modelo mejorado."""
    model_config = ConfigDict(protected_namespaces=())
    
    model_name: str = Field(..., min_length=1, max_length=100)
    model_type: str = Field(..., description="Tipo de modelo ML")
    model_data: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(default_factory=list)
    
    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v):
        """Validar nombre del modelo."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Model name must be alphanumeric with _ or -')
        return v

# ===== RESPONSE MODELS =====

class ValidationDetails(BaseModel):
    """Detalles de validación."""
    model_config = ConfigDict(protected_namespaces=())
    
    input_valid: bool
    model_valid: bool
    validation_time_ms: Optional[float] = None
    warnings: Optional[List[str]] = Field(default_factory=list)

class ModelInfo(BaseModel):
    """Información del modelo."""
    model_config = ConfigDict(protected_namespaces=())
    
    model_id: str
    status: str
    type: Optional[str] = None
    version: Optional[str] = None
    last_updated: Optional[datetime] = None

class PredictionResponse(BaseModel):
    """Response de predicción estructurada."""
    model_config = ConfigDict(protected_namespaces=())
    
    prediction: List[float]
    validation_details: Optional[ValidationDetails] = None
    model_info: ModelInfo
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ModelUploadResponse(BaseModel):
    """Response de subida de modelo."""
    model_config = ConfigDict(protected_namespaces=())
    
    message: str
    model_name: str
    status: str
    model_type: Optional[str] = None
    upload_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """Response de error estandarizada."""
    model_config = ConfigDict(protected_namespaces=())
    
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None

# ===== UTILITY MODELS =====

class HealthResponse(BaseModel):
    """Response de health check."""
    model_config = ConfigDict(protected_namespaces=())
    
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Optional[Dict[str, str]] = Field(default_factory=dict)

class ModelsListResponse(BaseModel):
    """Response para listado de modelos."""
    model_config = ConfigDict(protected_namespaces=())
    
    models: List[str]
    total_count: int
    available_types: List[str] 