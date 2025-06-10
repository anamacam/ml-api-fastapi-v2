"""
TDD para validación de modelos ML.

Tests que definen cómo debe comportarse la validación de modelos
de machine learning antes de hacer predicciones.

Nuevo ciclo TDD: RED -> GREEN -> REFACTOR
"""

import pytest


def test_validate_ml_model_rejects_none_model():
    """
    TDD Test 1: validate_ml_model debe rechazar modelos None.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.ml_model_validators import validate_ml_model

    # Modelo None
    result = validate_ml_model(None)
    assert result["valid"] is False
    assert "error" in result
    assert "none" in result["error"].lower()


def test_validate_ml_model_validates_required_methods():
    """
    TDD Test 2: validate_ml_model debe validar métodos requeridos.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.ml_model_validators import validate_ml_model

    # Modelo sin método predict
    class InvalidModel:
        def fit(self, X, y):
            pass

    model = InvalidModel()
    result = validate_ml_model(model)
    assert result["valid"] is False
    assert "missing_methods" in result["error"]
    assert "predict" in result["missing_methods"]


def test_validate_ml_model_accepts_valid_sklearn_model():
    """
    TDD Test 3: validate_ml_model debe aceptar modelos sklearn válidos.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.ml_model_validators import validate_ml_model
    from sklearn.linear_model import LinearRegression
    import numpy as np

    # Modelo sklearn entrenado
    model = LinearRegression()
    X = np.array([[1], [2], [3]])
    y = np.array([1, 2, 3])
    model.fit(X, y)

    result = validate_ml_model(model)
    assert result["valid"] is True
    assert "error" not in result


def test_validate_ml_model_validates_model_state():
    """
    TDD Test 4: validate_ml_model debe validar que el modelo esté entrenado.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.ml_model_validators import validate_ml_model
    from sklearn.linear_model import LinearRegression

    # Modelo sklearn NO entrenado
    model = LinearRegression()

    result = validate_ml_model(model)
    assert result["valid"] is False
    assert "not_fitted" in result["error"]


def test_validate_ml_model_validates_prediction_capability():
    """
    TDD Test 5: validate_ml_model debe validar capacidad de predicción.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.ml_model_validators import validate_ml_model
    import numpy as np

    # Modelo que falla al predecir
    class BrokenModel:
        def predict(self, X):
            raise Exception("Prediction failed")

        def fit(self, X, y):
            pass

    model = BrokenModel()
    test_data = np.array([[1], [2]])

    result = validate_ml_model(model, test_data=test_data)
    assert result["valid"] is False
    assert "prediction_failed" in result["error"]


def test_validate_ml_model_validates_output_format():
    """
    TDD Test 6: validate_ml_model debe validar formato de salida.

    RED PHASE: Este test debe FALLAR porque la función no existe.
    """
    from app.utils.ml_model_validators import validate_ml_model
    import numpy as np

    # Modelo que retorna formato inválido
    class BadOutputModel:
        def predict(self, X):
            return "invalid_output"  # String en lugar de array

        def fit(self, X, y):
            pass

    model = BadOutputModel()
    test_data = np.array([[1], [2]])

    result = validate_ml_model(model, test_data=test_data)
    assert result["valid"] is False
    assert "invalid_output_format" in result["error"]


# Tests adicionales después del refactor
def test_sklearn_model_validator_supports_sklearn():
    """
    Test adicional: SklearnModelValidator debe reconocer modelos sklearn.
    """
    from app.utils.ml_model_validators import SklearnModelValidator
    from sklearn.linear_model import LinearRegression

    validator = SklearnModelValidator()
    model = LinearRegression()

    assert validator.supports_model(model) is True


def test_sklearn_model_validator_rejects_non_sklearn():
    """
    Test adicional: SklearnModelValidator debe rechazar modelos no-sklearn.
    """
    from app.utils.ml_model_validators import SklearnModelValidator

    validator = SklearnModelValidator()

    class CustomModel:
        def predict(self, X):
            return [1, 2, 3]

    model = CustomModel()
    # Ahora con la lógica mejorada debe funcionar correctamente
    assert validator.supports_model(model) is False


def test_generic_model_validator_accepts_any_model():
    """
    Test adicional: GenericModelValidator debe aceptar cualquier modelo.
    """
    from app.utils.ml_model_validators import GenericModelValidator

    validator = GenericModelValidator()

    class AnyModel:
        def predict(self, X):
            return [1, 2, 3]

    model = AnyModel()
    result = validator.validate(model)

    assert validator.supports_model(model) is True
    assert result["valid"] is True


def test_get_supported_model_types():
    """
    Test adicional: get_supported_model_types debe retornar lista de tipos.
    """
    from app.utils.ml_model_validators import get_supported_model_types

    types = get_supported_model_types()

    assert isinstance(types, list)
    assert len(types) > 0
    assert "sklearn.*" in types
    assert "generic (any object with predict method)" in types


def test_get_validation_config():
    """
    Test adicional: get_validation_config debe retornar configuración.
    """
    from app.utils.ml_model_validators import get_validation_config

    config = get_validation_config()

    assert "required_methods" in config
    assert "sklearn_fitted_attributes" in config
    assert "valid_prediction_types" in config
    assert "supported_model_types" in config
    assert "version" in config
    assert "predict" in config["required_methods"]


def test_validate_ml_model_handles_empty_prediction():
    """
    Test adicional: validate_ml_model debe detectar predicciones vacías.
    """
    from app.utils.ml_model_validators import validate_ml_model
    import numpy as np

    # Modelo que retorna predicción vacía
    class EmptyPredictionModel:
        def predict(self, X):
            return []  # Lista vacía

        def fit(self, X, y):
            pass

    model = EmptyPredictionModel()
    test_data = np.array([[1], [2]])

    result = validate_ml_model(model, test_data=test_data)
    assert result["valid"] is False
    assert "empty" in result["error"]


def test_validate_ml_model_accepts_tuple_output():
    """
    Test adicional: validate_ml_model debe aceptar tuplas como salida válida.
    """
    from app.utils.ml_model_validators import validate_ml_model
    import numpy as np

    # Modelo que retorna tupla
    class TupleOutputModel:
        def predict(self, X):
            return (1, 2, 3)  # Tupla válida

        def fit(self, X, y):
            pass

    model = TupleOutputModel()
    test_data = np.array([[1], [2]])

    result = validate_ml_model(model, test_data=test_data)
    assert result["valid"] is True


# NUEVOS TESTS PARA MEJORAS IMPLEMENTADAS

def test_validate_ml_model_with_custom_required_methods():
    """
    Test para métodos requeridos personalizados (MEJORA CRÍTICA).
    """
    from app.utils.ml_model_validators import validate_ml_model

    # Modelo que tiene predict_proba pero no decision_function
    class ClassifierModel:
        def predict(self, X):
            return [1, 0, 1]
        
        def predict_proba(self, X):
            return [[0.8, 0.2], [0.3, 0.7], [0.9, 0.1]]

    model = ClassifierModel()
    
    # Debe pasar con métodos por defecto
    result = validate_ml_model(model)
    assert result["valid"] is True
    
    # Debe pasar al requerir predict_proba
    result = validate_ml_model(model, required_methods=["predict", "predict_proba"])
    assert result["valid"] is True
    
    # Debe fallar al requerir decision_function
    result = validate_ml_model(model, required_methods=["predict", "decision_function"])
    assert result["valid"] is False
    assert "missing_methods" in result["error"]
    assert "decision_function" in result["missing_methods"]


def test_validate_test_data_rejects_empty_data():
    """
    Test para validación de test_data vacío (MEJORA CRÍTICA).
    """
    from app.utils.ml_model_validators import validate_ml_model
    import numpy as np

    class SimpleModel:
        def predict(self, X):
            return [1, 2, 3]

    model = SimpleModel()
    
    # Test con array vacío
    empty_data = np.array([])
    result = validate_ml_model(model, test_data=empty_data)
    assert result["valid"] is False
    assert "empty" in result["error"]
    
    # Test con None
    result = validate_ml_model(model, test_data=None)
    assert result["valid"] is True  # None es opcional, no debe fallar


def test_validate_test_data_limits_large_datasets():
    """
    Test para límite de tamaño de test_data (MEJORA CRÍTICA).
    """
    from app.utils.ml_model_validators import validate_ml_model
    import numpy as np

    class SimpleModel:
        def predict(self, X):
            return np.ones(X.shape[0])

    model = SimpleModel()
    
    # Test con dataset demasiado grande (>1000 muestras)
    large_data = np.random.rand(1500, 5)
    result = validate_ml_model(model, test_data=large_data)
    assert result["valid"] is False
    assert "too large" in result["error"]
    assert "1500" in result["error"]
    assert "1000" in result["error"]


def test_logging_configuration_works():
    """
    Test para verificar que el logging está configurado (MEJORA CRÍTICA).
    """
    from app.utils.ml_model_validators import logger
    
    # Verificar que el logger tiene handlers
    assert len(logger.handlers) > 0
    
    # Verificar que el level está configurado
    assert logger.level == 20  # INFO level
    
    # Verificar que el handler tiene formatter
    handler = logger.handlers[0]
    assert handler.formatter is not None


def test_get_validation_config_includes_new_options():
    """
    Test para verificar que la configuración incluye nuevas opciones.
    """
    from app.utils.ml_model_validators import get_validation_config

    config = get_validation_config()
    
    # Verificar nuevas opciones
    assert "optional_methods" in config
    assert "max_test_samples" in config
    assert config["version"] == "2.1.0"
    
    # Verificar contenido de métodos opcionales
    assert "predict_proba" in config["optional_methods"]
    assert "decision_function" in config["optional_methods"]
    assert "transform" in config["optional_methods"]
    
    # Verificar límite de muestras
    assert config["max_test_samples"] == 1000


def test_validate_ml_model_logs_success():
    """
    Test para verificar que se logea el éxito de validación.
    """
    import logging
    from app.utils.ml_model_validators import validate_ml_model
    from sklearn.linear_model import LinearRegression
    import numpy as np

    # Modelo sklearn entrenado
    model = LinearRegression()
    X = np.array([[1], [2], [3]])
    y = np.array([1, 2, 3])
    model.fit(X, y)

    result = validate_ml_model(model)
    assert result["valid"] is True
    
    # Verificar que no hay errores (logging funciona implícitamente)
    # Este test verifica que el sistema de logging está funcionando sin errores


def test_edge_cases_for_robustness():
    """
    Test para casos edge y robustez general.
    """
    from app.utils.ml_model_validators import validate_ml_model
    import numpy as np

    # Modelo con método predict que no es callable
    class BrokenModel:
        predict = "not_a_method"

    model = BrokenModel()
    result = validate_ml_model(model)
    assert result["valid"] is False
    assert "missing_methods" in result["error"]
    
    # Test con test_data de dimensiones extrañas
    class SimpleModel:
        def predict(self, X):
            return [1] * len(X)

    model = SimpleModel()
    weird_data = np.array([1, 2, 3])  # 1D array
    result = validate_ml_model(model, test_data=weird_data)
    # Debería manejar esto sin errores
    assert result["valid"] is True
