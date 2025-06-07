from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json
import uuid
from datetime import datetime

from app.models.database import get_db
from app.models.schemas import PredictionRequest, PredictionResponse, PredictionStatus
from app.services.prediction import PredictionService
from app.services.cache import CacheService
from app.services.monitoring import metrics

router = APIRouter()

@router.post("/", response_model=PredictionResponse)
async def create_prediction(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva predicción ML
    
    - **model_id**: ID del modelo a usar
    - **input_data**: Datos de entrada para la predicción
    - **async_mode**: Si es True, procesa en background
    """
    
    try:
        # Generar ID único para la predicción
        prediction_id = str(uuid.uuid4())
        
        # Verificar si el modelo existe
        prediction_service = PredictionService(db)
        if not await prediction_service.model_exists(request.model_id):
            raise HTTPException(status_code=404, detail="Modelo no encontrado")
        
        # Cache check
        cache_service = CacheService()
        cache_key = f"prediction:{request.model_id}:{hash(str(request.input_data))}"
        cached_result = await cache_service.get(cache_key)
        
        if cached_result:
            metrics.cache_hits.inc()
            return PredictionResponse(
                prediction_id=prediction_id,
                status=PredictionStatus.COMPLETED,
                result=json.loads(cached_result),
                cached=True,
                created_at=datetime.utcnow()
            )
        
        # Procesar predicción
        if request.async_mode:
            # Procesamiento asíncrono
            background_tasks.add_task(
                prediction_service.process_async,
                prediction_id,
                request.model_id,
                request.input_data
            )
            
            return PredictionResponse(
                prediction_id=prediction_id,
                status=PredictionStatus.PROCESSING,
                message="Predicción en proceso. Use GET /predict/{id} para verificar estado.",
                created_at=datetime.utcnow()
            )
        else:
            # Procesamiento síncrono
            result = await prediction_service.predict(
                request.model_id,
                request.input_data
            )
            
            # Cache resultado
            await cache_service.set(cache_key, json.dumps(result), expire=3600)
            
            metrics.predictions_total.inc()
            metrics.cache_misses.inc()
            
            return PredictionResponse(
                prediction_id=prediction_id,
                status=PredictionStatus.COMPLETED,
                result=result,
                cached=False,
                created_at=datetime.utcnow()
            )
            
    except Exception as e:
        metrics.prediction_errors.inc()
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: str,
    db: Session = Depends(get_db)
):
    """Obtener estado y resultado de una predicción"""
    
    try:
        prediction_service = PredictionService(db)
        prediction = await prediction_service.get_prediction(prediction_id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo predicción: {str(e)}")

@router.get("/")
async def list_predictions(
    limit: int = 10,
    offset: int = 0,
    model_id: str = None,
    status: PredictionStatus = None,
    db: Session = Depends(get_db)
):
    """Listar predicciones con filtros opcionales"""
    
    try:
        prediction_service = PredictionService(db)
        predictions = await prediction_service.list_predictions(
            limit=limit,
            offset=offset,
            model_id=model_id,
            status=status
        )
        
        return {
            "predictions": predictions,
            "total": len(predictions),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando predicciones: {str(e)}")

@router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: str,
    db: Session = Depends(get_db)
):
    """Eliminar una predicción"""
    
    try:
        prediction_service = PredictionService(db)
        deleted = await prediction_service.delete_prediction(prediction_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")
        
        return {"message": "Predicción eliminada exitosamente"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando predicción: {str(e)}")

@router.post("/batch", response_model=List[PredictionResponse])
async def batch_predict(
    requests: List[PredictionRequest],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Procesar múltiples predicciones en lote"""
    
    if len(requests) > 100:
        raise HTTPException(status_code=400, detail="Máximo 100 predicciones por lote")
    
    try:
        prediction_service = PredictionService(db)
        results = []
        
        for request in requests:
            prediction_id = str(uuid.uuid4())
            
            if request.async_mode:
                background_tasks.add_task(
                    prediction_service.process_async,
                    prediction_id,
                    request.model_id,
                    request.input_data
                )
                
                results.append(PredictionResponse(
                    prediction_id=prediction_id,
                    status=PredictionStatus.PROCESSING,
                    created_at=datetime.utcnow()
                ))
            else:
                result = await prediction_service.predict(
                    request.model_id,
                    request.input_data
                )
                
                results.append(PredictionResponse(
                    prediction_id=prediction_id,
                    status=PredictionStatus.COMPLETED,
                    result=result,
                    created_at=datetime.utcnow()
                ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción lote: {str(e)}") 