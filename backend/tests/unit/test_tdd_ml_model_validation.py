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