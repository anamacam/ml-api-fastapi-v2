from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict, List
from datetime import datetime
from enum import Enum
import uuid

# Enums
class PredictionStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED" 
    FAILED = "FAILED"

class ModelStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TRAINING = "TRAINING"

class FileType(str, Enum):
    MODEL = "model"
    DATASET = "dataset"
    OTHER = "other"

# Esquemas de Request
class PredictionRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    model_id: str = Field(..., description="ID del modelo a usar")
    input_data: Dict[str, Any] = Field(..., description="Datos de entrada")
    async_mode: bool = Field(default=False, description="Procesamiento asíncrono")

class ModelCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., description="Tipo de modelo (sklearn, tensorflow, etc.)")
    version: str = Field(default="1.0.0")
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None

class ModelUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[ModelStatus] = None
    accuracy: Optional[float] = Field(None, ge=0, le=1)
    precision: Optional[float] = Field(None, ge=0, le=1)
    recall: Optional[float] = Field(None, ge=0, le=1)
    f1_score: Optional[float] = Field(None, ge=0, le=1)

# Esquemas de Response
class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    prediction_id: str
    status: PredictionStatus
    result: Optional[Dict[str, Any]] = None
    cached: bool = False
    message: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class ModelMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None

class ModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    type: str
    version: str
    description: Optional[str] = None
    status: ModelStatus
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    metrics: Optional[ModelMetrics] = None
    created_at: datetime
    updated_at: datetime

class FileUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    filename: str
    original_filename: str
    size: int
    upload_id: str
    url: str
    type: FileType
    uploaded_at: datetime

class HealthCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    status: str
    timestamp: datetime
    service: str
    version: str
    uptime: Optional[float] = None

class DetailedHealthCheck(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    status: str
    timestamp: datetime
    service: str
    version: str
    uptime: Optional[float] = None
    checks: Dict[str, Dict[str, Any]]

class PaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class ErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    error: str
    detail: str
    timestamp: datetime
    request_id: Optional[str] = None

# Esquemas WebSocket
class WSMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WSPredictionUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    prediction_id: str
    status: PredictionStatus
    progress: Optional[float] = None  # 0-100
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None 