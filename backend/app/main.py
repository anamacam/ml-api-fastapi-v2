"""
FastAPI Application - REFACTORIZADA con servicios separados.

REFACTOR PHASE: Código elegante, mantenible y escalable.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

# Importar servicios refactorizados
from app.services.hybrid_prediction_service import HybridPredictionService
from app.services.model_management_service import ModelManagementService

# Importar modelos refactorizados
from app.models.api_models import (
    PredictionRequest, ModelUploadRequest,
    PredictionResponse, ModelUploadResponse, 
    HealthResponse, ErrorResponse,
    ValidationDetails, ModelInfo
)

# Configurar logging mejorado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Instancias globales de servicios (en producción usar Dependency Injection)
prediction_service = None
model_management_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación."""
    # Startup
    global prediction_service, model_management_service
    
    # Usar modelos reales en producción, mocks en testing
    import os
    use_real_models = os.getenv("TESTING", "false").lower() != "true"
    
    prediction_service = HybridPredictionService(use_real_models=use_real_models)
    model_management_service = ModelManagementService()
    
    logger.info("🚀 Servicios híbridos inicializados correctamente")
    logger.info(f"📊 Modo: {'Modelos Reales' if use_real_models else 'Modelos Mock (Testing)'}")
    
    yield
    
    # Shutdown
    logger.info("👋 Aplicación cerrando...")

# Crear aplicación FastAPI refactorizada
app = FastAPI(
    title="ML API FastAPI v2 - Refactorizada",
    description="API de Machine Learning con arquitectura TDD y servicios separados",
    version="2.1.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection functions
def get_prediction_service() -> HybridPredictionService:
    """Obtener servicio de predicción híbrido."""
    global prediction_service
    if prediction_service is None:
        # Inicialización para tests o uso directo
        import os
        use_real_models = os.getenv("TESTING", "false").lower() != "true"
        prediction_service = HybridPredictionService(use_real_models=use_real_models)
    return prediction_service

def get_model_service() -> ModelManagementService:
    """Obtener servicio de gestión de modelos."""
    global model_management_service
    if model_management_service is None:
        # Inicialización para tests o uso directo
        model_management_service = ModelManagementService()
    return model_management_service

# ===== ENDPOINTS REFACTORIZADOS =====

@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    service: HybridPredictionService = Depends(get_prediction_service)
):
    """
    Endpoint de predicción refactorizado con servicios separados.
    
    Arquitectura limpia:
    - Validación en servicio
    - Manejo de errores centralizado  
    - Respuesta tipada con Pydantic
    """
    try:
        success, result = service.validate_and_predict(
            request.features, 
            request.model_id
        )
        
        if not success:
            error = result
            
            # Manejo específico por tipo de error
            if error["error_type"] == "input_validation":
                validation_result = error["validation_result"]
                
                if "missing_fields" in validation_result:
                    raise HTTPException(
                        status_code=422,
                        detail={
                            "validation_error": "Missing required fields",
                            "missing_fields": validation_result["missing_fields"]
                        }
                    )
                else:
                    raise HTTPException(
                        status_code=422,
                        detail={
                            "validation_error": validation_result["error"],
                            "invalid_types": True
                        }
                    )
            
            elif error["error_type"] == "model_not_found":
                raise HTTPException(
                    status_code=400,
                    detail={"model_validation_error": f"Model '{error['model_id']}' not found"}
                )
            
            elif error["error_type"] == "prediction_failed":
                raise HTTPException(
                    status_code=500,
                    detail={"prediction_failed": error["error_message"]}
                )
        
        # Respuesta exitosa usando modelo Pydantic
        return PredictionResponse(
            prediction=result["prediction"],
            validation_details=ValidationDetails(
                input_valid=result["validation_details"]["input_valid"],
                model_valid=result["validation_details"]["model_valid"]
            ) if request.include_validation_details else None,
            model_info=ModelInfo(
                model_id=result["model_info"]["model_id"],
                status=result["model_info"]["status"],
                type=result["model_info"].get("type")
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en predicción: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error"}
        )

@app.post("/api/v1/models", response_model=ModelUploadResponse)
async def upload_model(
    request: ModelUploadRequest,
    service: ModelManagementService = Depends(get_model_service)
):
    """
    Endpoint para subir modelos refactorizado.
    
    Usa servicio separado para validación y registro.
    """
    try:
        success, result = service.validate_and_register_model(
            request.model_name,
            request.model_type,
            request.model_data
        )
        
        if not success:
            error = result
            raise HTTPException(
                status_code=422,
                detail={"model_validation_error": error.get("message", "Invalid model")}
            )
        
        # Respuesta exitosa usando modelo Pydantic
        return ModelUploadResponse(
            message=result["message"],
            model_name=result["model_name"],
            status=result["status"],
            model_type=result.get("model_type")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo modelo: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Error processing model upload"}
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check mejorado con información de servicios."""
    return HealthResponse(
        status="healthy",
        version="2.1.0",
        services={
            "prediction_service": "running" if prediction_service else "not_initialized",
            "model_management": "running" if model_management_service else "not_initialized"
        }
    )

@app.get("/api/v1/models")
async def list_models(
    service: HybridPredictionService = Depends(get_prediction_service)
):
    """Listar modelos disponibles (reales + mocks)."""
    try:
        available_models = service.list_available_models()
        model_details = []
        
        for model_id in available_models:
            model_info = service.get_model_info(model_id)
            if model_info:
                model_details.append(model_info)
        
        return {
            "models": available_models,
            "model_details": model_details,
            "total_count": len(available_models),
            "status": "success",
            "real_models_enabled": service.use_real_models
        }
    except Exception as e:
        logger.error(f"Error listando modelos: {e}")
        raise HTTPException(status_code=500, detail={"error": str(e)})

# Endpoint de documentación adicional
@app.get("/")
async def root():
    """Root endpoint con información de la API."""
    return {
        "message": "🚀 ML API FastAPI v2 - Arquitectura TDD Refactorizada",
        "version": "2.1.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "predict": "/api/v1/predict",
            "upload_model": "/api/v1/models",
            "list_models": "/api/v1/models"
        }
    }
