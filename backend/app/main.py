# -*- coding: utf-8 -*-
"""
FastAPI Application - Punto de entrada principal de la API.

Define la aplicación FastAPI, gestiona el ciclo de vida, configura middlewares,
y registra los endpoints de la API.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

# Configuración y Modelos
from app.config.settings import get_settings
from app.models.api_models import (
    HealthResponse,
    ModelInfo,
    ModelUploadRequest,
    ModelUploadResponse,
    PredictionRequest,
    PredictionResponse,
)

# Servicios
from app.services.hybrid_prediction_service import HybridPredictionService
from app.services.model_management_service import ModelManagementService
from app.utils.error_handlers import (
    build_validation_details,
    handle_prediction_error,
    handle_service_error,
)
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 1. --- Configuración e Inicialización ---

settings = get_settings()

# Configurar el logger principal
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Silenciar loggers de librerías en entornos no-debug
if settings.environment != "development":
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# Declaración de servicios globales para ser gestionados por el lifespan
prediction_service: Optional[HybridPredictionService] = None
model_management_service: Optional[ModelManagementService] = None


# 2. --- Gestión del Ciclo de Vida (Lifespan) ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona la inicialización y el apagado de los recursos de la aplicación,
    como los servicios de ML.
    """
    global prediction_service, model_management_service
    logger.info("Iniciando la aplicación y los servicios...")

    # Inicializar servicios
    prediction_service = HybridPredictionService()
    model_management_service = ModelManagementService()

    logger.info("🚀 Servicios inicializados correctamente")
    logger.info(f"🌍 Entorno de ejecución: {settings.environment.upper()}")
    logger.info(
        f"📊 Usando modelos reales: {'SÍ' if settings.should_use_real_models else 'NO'}"
    )

    yield

    # Acciones de apagado
    logger.info("👋 Apagando la aplicación...")
    # Aquí iría la lógica de limpieza si fuera necesaria (ej. cerrar conexiones)


# 3. --- Creación y Configuración de la App FastAPI ---

app = FastAPI(
    title=settings.api_title,
    description=f"API de Machine Learning (Entorno: {settings.environment})",
    version=settings.api_version,
    lifespan=lifespan,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4. --- Inyección de Dependencias ---


def get_prediction_service() -> HybridPredictionService:
    """Dependencia para obtener el servicio de predicción."""
    if prediction_service is None:
        raise HTTPException(
            status_code=503, detail="Servicio de predicción no disponible."
        )
    return prediction_service


def get_model_service() -> ModelManagementService:
    """Dependencia para obtener el servicio de gestión de modelos."""
    if model_management_service is None:
        raise HTTPException(
            status_code=503, detail="Servicio de modelos no disponible."
        )
    return model_management_service


# 5. --- Endpoints de la API ---


@app.get("/", summary="Endpoint raíz de la API", tags=["General"])
async def root():
    """Devuelve un mensaje de bienvenida y enlaces a la documentación."""
    return {
        "message": "🤖 Bienvenido a la ML API v2",
        "environment": settings.environment,
        "version": settings.api_version,
        "docs_url": "/docs",
        "health_check": "/health",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Verifica la salud de la aplicación",
    tags=["General"],
)
async def health_check():
    """
    Endpoint de health check que proporciona el estado general de la aplicación
    y sus servicios principales.
    """
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        services={
            "environment": settings.environment,
            "debug_mode": str(settings.debug),
            "real_models_enabled": str(settings.should_use_real_models),
        },
    )


@app.post(
    "/api/v1/predict",
    response_model=PredictionResponse,
    summary="Realiza una predicción",
    tags=["Predicciones"],
)
async def predict(
    request: PredictionRequest,
    service: HybridPredictionService = Depends(get_prediction_service),
):
    """
    Recibe datos de entrada y devuelve una predicción del modelo.
    """
    try:
        model_id = request.model_id or "default_model"
        success, result = service.validate_and_predict(request.features, model_id)

        if not success:
            raise handle_prediction_error(result)

        return PredictionResponse(
            prediction=result["prediction"],
            validation_details=build_validation_details(
                bool(request.include_validation_details), result
            ),
            model_info=ModelInfo(
                model_id=result["model_info"]["model_id"],
                status=result["model_info"]["status"],
                type=result["model_info"].get("type"),
            ),
        )

    except HTTPException:
        raise  # Re-lanzar HTTPErrors manejadas por handle_prediction_error
    except Exception as e:
        logger.error(
            f"Error inesperado en el endpoint de predicción: {e}", exc_info=True
        )
        raise handle_service_error("predicción", e)


@app.post(
    "/api/v1/models",
    response_model=ModelUploadResponse,
    summary="Sube y registra un nuevo modelo",
    tags=["Modelos"],
)
async def upload_model(
    request: ModelUploadRequest,
    service: ModelManagementService = Depends(get_model_service),
):
    """
    Permite subir un nuevo modelo para que esté disponible para predicciones.
    """
    try:
        success, result = service.validate_and_register_model(
            model_name=request.model_name,
            model_type=request.model_type,
            model_data=request.model_data,
        )
        if not success:
            raise HTTPException(status_code=422, detail=result)

        return ModelUploadResponse(
            message=f"Modelo '{request.model_name}' subido y registrado exitosamente.",
            model_name=request.model_name,
            status="registered",
            model_type=request.model_type,
        )
    except HTTPException:
        raise  # Re-lanzar la excepción HTTP específica sin modificar
    except Exception as e:
        logger.error(f"Error en la subida de modelo: {e}", exc_info=True)
        raise handle_service_error("subida de modelo", e)


@app.get("/api/v1/models", summary="Lista los modelos disponibles", tags=["Modelos"])
async def list_models(
    service: HybridPredictionService = Depends(get_prediction_service),
):
    """Devuelve una lista de todos los modelos de predicción disponibles."""
    try:
        models = service.list_available_models()
        return {
            "total_models": len(models),
            "available_types": ["lightgbm", "sklearn", "mock"],
            "models": models,
        }
    except Exception as e:
        logger.error(f"Error al listar modelos: {e}", exc_info=True)
        raise handle_service_error("listado de modelos", e)
