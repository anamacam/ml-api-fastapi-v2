"""
Tests unitarios para el servicio de predicciones ML.

Este módulo contiene tests que verifican el funcionamiento correcto
del servicio de predicciones, incluyendo validación de datos,
procesamiento y generación de predicciones.
"""

import pytest
from app.models.api_models import ModelInfo, PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService


class TestPredictionService:
    """Tests para el servicio de predicciones."""

    @pytest.fixture
    def prediction_service(self, mock_ml_model):
        """
        Fixture que proporciona una instancia del servicio de predicciones.

        Args:
            mock_ml_model: Modelo ML mock

        Returns:
            PredictionService: Instancia del servicio de predicciones
        """
        service = PredictionService()
        # Mock el modelo en el diccionario de modelos
        service.models["default_model"] = mock_ml_model
        return service

    @pytest.fixture
    def valid_prediction_request(self, sample_prediction_data):
        """
        Fixture que proporciona una request válida de predicción.

        Args:
            sample_prediction_data: Datos de predicción de ejemplo

        Returns:
            PredictionRequest: Request de predicción válida
        """
        return PredictionRequest(
            features=sample_prediction_data["features"],
            model_id=sample_prediction_data["model_id"],
            include_validation_details=sample_prediction_data[
                "include_validation_details"
            ],
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_predict_success(self, prediction_service, valid_prediction_request):
        """
        Test que verifica una predicción exitosa.

        Args:
            prediction_service: Servicio de predicciones
            valid_prediction_request: Request válida de predicción
        """
        # Arrange
        expected_prediction = [0.8, 0.2]
        mock_model = prediction_service.models["default_model"]
        mock_model.predict.return_value = expected_prediction

        # Act
        result = await prediction_service.predict(valid_prediction_request)

        # Assert
        assert isinstance(result, PredictionResponse)
        assert result.prediction == expected_prediction
        assert result.model_info is not None
        assert result.model_info.model_id == valid_prediction_request.model_id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_predict_model_not_found(self, prediction_service):
        """
        Test que verifica el comportamiento cuando el modelo no existe.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        request = PredictionRequest(
            features={
                "age": 30.0,
                "income": 50000.0,
                "category": "premium",
                "score": 0.85,
            },
            model_id="non_existent_model",
        )

        # Act & Assert
        with pytest.raises(Exception):  # PredictionError
            await prediction_service.predict(request)

    @pytest.mark.unit
    def test_load_model_success(self, prediction_service):
        """
        Test que verifica la carga exitosa de un modelo.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Act
        result = prediction_service.load_model("test_model.joblib")

        # Assert
        assert result is True
        assert prediction_service.model_loaded is True
        assert prediction_service.current_model is not None

    @pytest.mark.unit
    def test_load_model_failure(self, prediction_service):
        """
        Test que verifica el manejo de errores al cargar un modelo.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Act
        result = prediction_service.load_model("invalid_path")

        # Assert
        assert result is False

    @pytest.mark.unit
    def test_validate_model_compatibility(self, prediction_service):
        """
        Test que verifica la validación de compatibilidad de modelos.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        valid_model_data = {"type": "sklearn", "version": "1.0.0"}
        invalid_model_data = None

        # Act & Assert
        assert prediction_service.validate_model_compatibility(valid_model_data) is True
        assert (
            prediction_service.validate_model_compatibility(invalid_model_data) is False
        )

    @pytest.mark.unit
    def test_get_model_status(self, prediction_service):
        """
        Test que verifica la obtención del estado del modelo.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Act
        status = prediction_service.get_model_status("default_model")

        # Assert
        assert isinstance(status, str)
        assert status in ["active", "inactive", "error", "loading"]

    @pytest.mark.unit
    def test_cache_prediction_result(self, prediction_service):
        """
        Test que verifica el cacheo de resultados de predicción.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        prediction_id = "test_pred_123"
        result = {"prediction": [0.8, 0.2], "confidence": 0.9}

        # Act
        success = prediction_service.cache_prediction_result(prediction_id, result)

        # Assert
        assert success is True

    @pytest.mark.unit
    def test_get_cached_prediction(self, prediction_service):
        """
        Test que verifica la obtención de predicciones cacheadas.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        prediction_id = "test_pred_456"
        expected_result = {"prediction": [0.7, 0.3], "confidence": 0.8}
        prediction_service.cache_prediction_result(prediction_id, expected_result)

        # Act
        cached_result = prediction_service.get_cached_prediction(prediction_id)

        # Assert
        assert cached_result == expected_result

    @pytest.mark.unit
    def test_get_prediction_confidence(self, prediction_service):
        """
        Test que verifica la obtención de confianza de predicción.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Act
        confidence = prediction_service.get_prediction_confidence("test_pred_789")

        # Assert
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check(self, prediction_service):
        """
        Test que verifica el health check del servicio.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Act
        health_status = await prediction_service.health_check()

        # Assert
        assert isinstance(health_status, dict)
        assert "status" in health_status
        assert "models_loaded" in health_status
        assert "preprocessors_loaded" in health_status
        assert "timestamp" in health_status
        assert "details" in health_status

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_available_models(self, prediction_service):
        """
        Test que verifica el listado de modelos disponibles.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Act
        models = await prediction_service.list_available_models()

        # Assert
        assert isinstance(models, list)
        # Puede estar vacío si no hay modelos cargados

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_model_info(self, prediction_service):
        """
        Test que verifica la obtención de información del modelo.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Act
        model_info = await prediction_service.get_model_info("default_model")

        # Assert
        assert isinstance(model_info, dict)
        # Puede estar vacío si no hay información del modelo


@pytest.mark.unit
class TestPredictionModels:
    """Tests para los modelos de datos de predicción."""

    def test_prediction_request_creation(self):
        """
        Test que verifica la creación de PredictionRequest.
        """
        # Arrange & Act
        request = PredictionRequest(
            features={
                "age": 30.0,
                "income": 50000.0,
                "category": "premium",
                "score": 0.85,
            },
            model_id="default_model",
        )

        # Assert
        assert request.features == {
            "age": 30.0,
            "income": 50000.0,
            "category": "premium",
            "score": 0.85,
        }
        assert request.model_id == "default_model"

    def test_prediction_request_validation(self):
        """
        Test que verifica la validación de PredictionRequest.
        """
        # Act & Assert
        with pytest.raises(ValueError):
            # Usar un enfoque que falle la validación sin causar errores de linter
            import json

            invalid_data = json.loads(
                '{"features": "not_a_dict", "model_id": "default_model"}'
            )
            PredictionRequest(**invalid_data)

    def test_prediction_response_creation(self):
        """
        Test que verifica la creación de PredictionResponse.
        """
        # Arrange & Act
        model_info = ModelInfo(
            model_id="default_model", status="active", type="ml_model", version="1.0.0"
        )

        response = PredictionResponse(
            prediction=[0.8, 0.2], model_info=model_info, request_id="req_123456"
        )

        # Assert
        assert response.prediction == [0.8, 0.2]
        assert response.model_info.model_id == "default_model"
        assert response.request_id == "req_123456"
        assert response.timestamp is not None
