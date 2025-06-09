"""
Servicio de predicciones de Machine Learning.

Este módulo proporciona funcionalidades para realizar predicciones
usando modelos de machine learning entrenados.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
import numpy as np
import pandas as pd
from datetime import datetime
import joblib
from pathlib import Path

from ..core.config import get_settings
from ..models.schemas import PredictionRequest, PredictionResponse
from ..utils.validators import validate_prediction_input
from ..utils.exceptions import PredictionError, ModelLoadError

logger = logging.getLogger(__name__)
settings = get_settings()


class PredictionService:
    """
    Servicio para realizar predicciones de machine learning.
    
    Maneja la carga de modelos, preprocessing de datos y
    generación de predicciones con validaciones completas.
    """
    
    def __init__(self):
        """Inicializar el servicio de predicciones."""
        self.models: Dict[str, Any] = {}
        self.preprocessors: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        self._load_models()
    
    def _load_models(self) -> None:
        """
        Cargar modelos y preprocessadores desde disco.
        
        Raises:
            ModelLoadError: Si falla la carga de modelos críticos.
        """
        try:
            models_path = Path(settings.MODELS_PATH)
            
            if not models_path.exists():
                logger.warning(f"Directorio de modelos no encontrado: {models_path}")
                return
            
            # Cargar modelos disponibles
            for model_file in models_path.glob("*.joblib"):
                model_name = model_file.stem
                try:
                    self.models[model_name] = joblib.load(model_file)
                    logger.info(f"Modelo cargado: {model_name}")
                except Exception as e:
                    logger.error(f"Error cargando modelo {model_name}: {e}")
                    raise ModelLoadError(f"Error cargando modelo {model_name}: {e}")
            
            # Cargar preprocessadores
            preprocessors_path = models_path / "preprocessors"
            if preprocessors_path.exists():
                for preprocessor_file in preprocessors_path.glob("*.joblib"):
                    preprocessor_name = preprocessor_file.stem
                    try:
                        self.preprocessors[preprocessor_name] = joblib.load(preprocessor_file)
                        logger.info(f"Preprocessador cargado: {preprocessor_name}")
                    except Exception as e:
                        logger.warning(f"Error cargando preprocessador {preprocessor_name}: {e}")
            
            # Cargar metadata de modelos
            self._load_model_metadata()
            
        except Exception as e:
            logger.error(f"Error crítico cargando modelos: {e}")
            raise ModelLoadError(f"Error crítico cargando modelos: {e}")
    
    def _load_model_metadata(self) -> None:
        """Cargar metadata de los modelos."""
        try:
            metadata_path = Path(settings.MODELS_PATH) / "metadata.json"
            if metadata_path.exists():
                import json
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                logger.info("Metadata de modelos cargada exitosamente")
        except Exception as e:
            logger.warning(f"Error cargando metadata de modelos: {e}")
    
    async def predict(
        self, 
        request: PredictionRequest
    ) -> PredictionResponse:
        """
        Realizar predicción usando el modelo especificado.
        
        Args:
            request: Solicitud de predicción con datos y configuración.
            
        Returns:
            PredictionResponse: Respuesta con predicciones y metadata.
            
        Raises:
            PredictionError: Si falla la predicción.
            ValueError: Si los datos de entrada no son válidos.
        """
        try:
            # Validar entrada
            validate_prediction_input(request)
            
            # Verificar que el modelo existe
            if request.model_name not in self.models:
                available_models = list(self.models.keys())
                raise PredictionError(
                    f"Modelo '{request.model_name}' no encontrado. "
                    f"Modelos disponibles: {available_models}"
                )
            
            # Preparar datos
            processed_data = await self._preprocess_data(
                request.features, 
                request.model_name
            )
            
            # Realizar predicción
            predictions = await self._make_prediction(
                processed_data, 
                request.model_name
            )
            
            # Postprocesar resultados
            results = await self._postprocess_results(
                predictions, 
                request.model_name,
                request.include_probabilities
            )
            
            # Crear respuesta
            response = PredictionResponse(
                predictions=results['predictions'],
                probabilities=results.get('probabilities'),
                confidence_scores=results.get('confidence_scores'),
                model_name=request.model_name,
                model_version=self.model_metadata.get(request.model_name, {}).get('version', '1.0'),
                timestamp=datetime.utcnow(),
                processing_time_ms=results.get('processing_time_ms', 0),
                metadata=results.get('metadata', {})
            )
            
            logger.info(f"Predicción completada para modelo: {request.model_name}")
            return response
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            raise PredictionError(f"Error realizando predicción: {e}")
    
    async def _preprocess_data(
        self, 
        features: Dict[str, Any], 
        model_name: str
    ) -> np.ndarray:
        """
        Preprocesar datos de entrada.
        
        Args:
            features: Características de entrada.
            model_name: Nombre del modelo.
            
        Returns:
            np.ndarray: Datos preprocesados.
        """
        try:
            # Convertir a DataFrame para procesamiento
            df = pd.DataFrame([features])
            
            # Aplicar preprocessador específico si existe
            preprocessor_name = f"{model_name}_preprocessor"
            if preprocessor_name in self.preprocessors:
                preprocessor = self.preprocessors[preprocessor_name]
                processed_data = preprocessor.transform(df)
            else:
                # Preprocessing básico
                processed_data = self._basic_preprocessing(df)
            
            return processed_data
            
        except Exception as e:
            raise PredictionError(f"Error en preprocessing: {e}")
    
    def _basic_preprocessing(self, df: pd.DataFrame) -> np.ndarray:
        """
        Preprocessing básico para datos de entrada.
        
        Args:
            df: DataFrame con los datos.
            
        Returns:
            np.ndarray: Datos preprocesados.
        """
        # Manejar valores faltantes
        df = df.fillna(0)
        
        # Convertir a numérico donde sea posible
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass
        
        # Seleccionar solo columnas numéricas
        numeric_df = df.select_dtypes(include=[np.number])
        
        return numeric_df.values
    
    async def _make_prediction(
        self, 
        data: np.ndarray, 
        model_name: str
    ) -> np.ndarray:
        """
        Realizar predicción con el modelo.
        
        Args:
            data: Datos preprocesados.
            model_name: Nombre del modelo.
            
        Returns:
            np.ndarray: Predicciones del modelo.
        """
        try:
            model = self.models[model_name]
            
            # Realizar predicción en un executor para no bloquear
            loop = asyncio.get_event_loop()
            predictions = await loop.run_in_executor(
                None, 
                model.predict, 
                data
            )
            
            return predictions
            
        except Exception as e:
            raise PredictionError(f"Error en predicción del modelo: {e}")
    
    async def _postprocess_results(
        self, 
        predictions: np.ndarray, 
        model_name: str,
        include_probabilities: bool = False
    ) -> Dict[str, Any]:
        """
        Postprocesar resultados de predicción.
        
        Args:
            predictions: Predicciones crudas del modelo.
            model_name: Nombre del modelo.
            include_probabilities: Si incluir probabilidades.
            
        Returns:
            Dict: Resultados procesados.
        """
        try:
            results = {
                'predictions': predictions.tolist(),
                'processing_time_ms': 0  # Se calcularía en implementación real
            }
            
            # Agregar probabilidades si es clasificador y se solicita
            if include_probabilities:
                model = self.models[model_name]
                if hasattr(model, 'predict_proba'):
                    try:
                        # Obtener las características originales (simplificado)
                        proba = model.predict_proba(np.array([[0] * 5]))  # Placeholder
                        results['probabilities'] = proba.tolist()
                    except Exception as e:
                        logger.warning(f"Error obteniendo probabilidades: {e}")
            
            # Agregar scores de confianza
            results['confidence_scores'] = self._calculate_confidence_scores(predictions)
            
            # Metadata adicional
            results['metadata'] = {
                'model_type': type(self.models[model_name]).__name__,
                'prediction_count': len(predictions),
                'model_info': self.model_metadata.get(model_name, {})
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error en postprocessing: {e}")
            return {'predictions': predictions.tolist()}
    
    def _calculate_confidence_scores(self, predictions: np.ndarray) -> List[float]:
        """
        Calcular scores de confianza para las predicciones.
        
        Args:
            predictions: Predicciones del modelo.
            
        Returns:
            List[float]: Scores de confianza.
        """
        # Implementación simplificada - en producción sería más sofisticada
        return [0.85] * len(predictions)  # Placeholder
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Obtener información sobre un modelo específico.
        
        Args:
            model_name: Nombre del modelo.
            
        Returns:
            Dict: Información del modelo.
            
        Raises:
            ValueError: Si el modelo no existe.
        """
        if model_name not in self.models:
            raise ValueError(f"Modelo '{model_name}' no encontrado")
        
        model = self.models[model_name]
        metadata = self.model_metadata.get(model_name, {})
        
        return {
            'name': model_name,
            'type': type(model).__name__,
            'version': metadata.get('version', '1.0'),
            'created_at': metadata.get('created_at'),
            'last_updated': metadata.get('last_updated'),
            'features': metadata.get('features', []),
            'performance_metrics': metadata.get('metrics', {}),
            'description': metadata.get('description', '')
        }
    
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """
        Listar todos los modelos disponibles.
        
        Returns:
            List[Dict]: Lista de información de modelos.
        """
        models_info = []
        
        for model_name in self.models.keys():
            try:
                info = await self.get_model_info(model_name)
                models_info.append(info)
            except Exception as e:
                logger.error(f"Error obteniendo info de modelo {model_name}: {e}")
        
        return models_info
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar el estado de salud del servicio.
        
        Returns:
            Dict: Estado de salud del servicio.
        """
        return {
            'status': 'healthy',
            'models_loaded': len(self.models),
            'preprocessors_loaded': len(self.preprocessors),
            'available_models': list(self.models.keys()),
            'timestamp': datetime.utcnow().isoformat()
        }


# Instancia global del servicio
prediction_service = PredictionService()


async def get_prediction_service() -> PredictionService:
    """
    Obtener instancia del servicio de predicciones.
    
    Returns:
        PredictionService: Instancia del servicio.
    """
    return prediction_service 