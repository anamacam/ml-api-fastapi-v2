"""
Tests unitarios para el servicio de predicciones ML.

Este módulo contiene tests que verifican el funcionamiento correcto
del servicio de predicciones, incluyendo validación de datos,
procesamiento y generación de predicciones.
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from app.services.prediction_service import (
    PredictionRequest,
    PredictionResponse,
    PredictionService,
)


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
        service.model = mock_ml_model
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
            model_version=sample_prediction_data["model_version"],
            user_id=sample_prediction_data["user_id"],
        )

    @pytest.mark.unit
    def test_make_prediction_success(
        self, prediction_service, valid_prediction_request
    ):
        """
        Test que verifica una predicción exitosa.

        Args:
            prediction_service: Servicio de predicciones
            valid_prediction_request: Request válida de predicción
        """
        # Arrange
        expected_prediction = [0.8, 0.2]
        expected_probability = [[0.2, 0.8]]

        prediction_service.model.predict.return_value = expected_prediction
        prediction_service.model.predict_proba.return_value = expected_probability

        # Act
        result = prediction_service.make_prediction(valid_prediction_request)

        # Assert
        assert isinstance(result, PredictionResponse)
        assert result.prediction == expected_prediction
        assert result.probability == expected_probability[0]
        assert result.confidence > 0
        assert result.model_version == valid_prediction_request.model_version
        assert result.prediction_id is not None

    @pytest.mark.unit
    def test_make_prediction_with_feature_validation(self, prediction_service):
        """
        Test que verifica la validación de features en la predicción.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        invalid_request = PredictionRequest(
            features=[], model_version="v1.0.0", user_id=1  # Features vacías
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Features cannot be empty"):
            prediction_service.make_prediction(invalid_request)

    @pytest.mark.unit
    def test_make_prediction_with_invalid_feature_types(self, prediction_service):
        """
        Test que verifica la validación de tipos de features.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        invalid_request = PredictionRequest(
            features=["invalid", "string", "features"],  # Tipos inválidos
            model_version="v1.0.0",
            user_id=1,
        )

        # Act & Assert
        with pytest.raises(ValueError, match="All features must be numeric"):
            prediction_service.make_prediction(invalid_request)

    @pytest.mark.unit
    def test_make_prediction_model_not_loaded(self):
        """
        Test que verifica el comportamiento cuando el modelo no está cargado.
        """
        # Arrange
        service = PredictionService()
        service.model = None

        request = PredictionRequest(
            features=[1.0, 2.0, 3.0], model_version="v1.0.0", user_id=1
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Model not loaded"):
            service.make_prediction(request)

    @pytest.mark.unit
    def test_preprocess_features_success(self, prediction_service):
        """
        Test que verifica el preprocesamiento exitoso de features.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        raw_features = [1.0, 2.0, 3.0, 4.0, 5.0]

        # Act
        processed_features = prediction_service.preprocess_features(raw_features)

        # Assert
        assert isinstance(processed_features, np.ndarray)
        assert processed_features.shape == (1, 5)  # 1 muestra, 5 features
        assert np.array_equal(processed_features[0], raw_features)

    @pytest.mark.unit
    def test_preprocess_features_normalization(self, prediction_service):
        """
        Test que verifica la normalización de features durante el preprocesamiento.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        raw_features = [100.0, 200.0, 300.0]
        prediction_service.feature_scaler = MagicMock()
        prediction_service.feature_scaler.transform.return_value = np.array(
            [[0.1, 0.2, 0.3]]
        )

        # Act
        processed_features = prediction_service.preprocess_features(raw_features)

        # Assert
        prediction_service.feature_scaler.transform.assert_called_once()
        assert processed_features.shape == (1, 3)

    @pytest.mark.unit
    def test_calculate_confidence_high_probability(self, prediction_service):
        """
        Test que verifica el cálculo de confianza con alta probabilidad.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        probabilities = [0.1, 0.9]  # Alta confianza en clase 1

        # Act
        confidence = prediction_service.calculate_confidence(probabilities)

        # Assert
        assert confidence == 0.9
        assert isinstance(confidence, float)

    @pytest.mark.unit
    def test_calculate_confidence_low_probability(self, prediction_service):
        """
        Test que verifica el cálculo de confianza con baja probabilidad.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        probabilities = [0.5, 0.5]  # Baja confianza

        # Act
        confidence = prediction_service.calculate_confidence(probabilities)

        # Assert
        assert confidence == 0.5
        assert isinstance(confidence, float)

    @pytest.mark.unit
    def test_validate_features_success(self, prediction_service):
        """
        Test que verifica la validación exitosa de features.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        valid_features = [1.0, 2.0, 3.0, 4.0, 5.0]

        # Act & Assert
        # No debería lanzar excepción
        prediction_service.validate_features(valid_features)

    @pytest.mark.unit
    def test_validate_features_empty_list(self, prediction_service):
        """
        Test que verifica la validación con lista vacía de features.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        empty_features = []

        # Act & Assert
        with pytest.raises(ValueError, match="Features cannot be empty"):
            prediction_service.validate_features(empty_features)

    @pytest.mark.unit
    def test_validate_features_non_numeric(self, prediction_service):
        """
        Test que verifica la validación con features no numéricas.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        non_numeric_features = [1.0, "string", 3.0]

        # Act & Assert
        with pytest.raises(ValueError, match="All features must be numeric"):
            prediction_service.validate_features(non_numeric_features)

    @pytest.mark.unit
    def test_validate_features_none_values(self, prediction_service):
        """
        Test que verifica la validación con valores None.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        features_with_none = [1.0, None, 3.0]

        # Act & Assert
        with pytest.raises(ValueError, match="Features cannot contain None values"):
            prediction_service.validate_features(features_with_none)

    @pytest.mark.unit
    def test_generate_prediction_id(self, prediction_service):
        """
        Test que verifica la generación de ID de predicción.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Act
        prediction_id = prediction_service.generate_prediction_id()

        # Assert
        assert isinstance(prediction_id, str)
        assert len(prediction_id) >= 8  # Al menos 8 caracteres
        assert prediction_id.startswith("pred_")

    @pytest.mark.unit
    def test_generate_prediction_id_uniqueness(self, prediction_service):
        """
        Test que verifica que los IDs de predicción son únicos.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Act
        id1 = prediction_service.generate_prediction_id()
        id2 = prediction_service.generate_prediction_id()

        # Assert
        assert id1 != id2

    @pytest.mark.unit
    @patch("app.services.prediction_service.datetime")
    def test_make_prediction_with_timestamp(
        self, mock_datetime, prediction_service, valid_prediction_request
    ):
        """
        Test que verifica que las predicciones incluyen timestamp.

        Args:
            mock_datetime: Mock del módulo datetime
            prediction_service: Servicio de predicciones
            valid_prediction_request: Request válida de predicción
        """
        # Arrange
        fixed_timestamp = "2024-12-07T10:00:00Z"
        mock_datetime.utcnow.return_value.isoformat.return_value = fixed_timestamp

        # Act
        result = prediction_service.make_prediction(valid_prediction_request)

        # Assert
        assert result.timestamp == fixed_timestamp

    @pytest.mark.unit
    def test_batch_prediction_success(self, prediction_service):
        """
        Test que verifica predicciones en lote.

        Args:
            prediction_service: Servicio de predicciones
        """
        # Arrange
        batch_requests = [
            PredictionRequest(features=[1.0, 2.0], model_version="v1.0.0", user_id=1),
            PredictionRequest(features=[3.0, 4.0], model_version="v1.0.0", user_id=2),
        ]

        prediction_service.model.predict.return_value = [0.8, 0.2]
        prediction_service.model.predict_proba.return_value = [[0.2, 0.8], [0.7, 0.3]]

        # Act
        results = prediction_service.make_batch_predictions(batch_requests)

        # Assert
        assert len(results) == 2
        assert all(isinstance(result, PredictionResponse) for result in results)


@pytest.mark.unit
class TestPredictionModels:
    """Tests para los modelos de datos de predicción."""

    def test_prediction_request_creation(self):
        """
        Test que verifica la creación de PredictionRequest.
        """
        # Arrange & Act
        request = PredictionRequest(
            features=[1.0, 2.0, 3.0], model_version="v1.0.0", user_id=123
        )

        # Assert
        assert request.features == [1.0, 2.0, 3.0]
        assert request.model_version == "v1.0.0"
        assert request.user_id == 123

    def test_prediction_request_validation(self):
        """
        Test que verifica la validación de PredictionRequest.
        """
        # Act & Assert
        with pytest.raises(ValueError):
            PredictionRequest(
                features=[], model_version="v1.0.0", user_id=123  # Features vacías
            )

    def test_prediction_response_creation(self):
        """
        Test que verifica la creación de PredictionResponse.
        """
        # Arrange & Act
        response = PredictionResponse(
            prediction=[0.8, 0.2],
            probability=[0.2, 0.8],
            confidence=0.8,
            model_version="v1.0.0",
            prediction_id="pred_123456",
            timestamp="2024-12-07T10:00:00Z",
        )

        # Assert
        assert response.prediction == [0.8, 0.2]
        assert response.probability == [0.2, 0.8]
        assert response.confidence == 0.8
        assert response.model_version == "v1.0.0"
        assert response.prediction_id == "pred_123456"
        assert response.timestamp == "2024-12-07T10:00:00Z"
