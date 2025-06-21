"""
Implementación concreta de BaseService para tests TDD CYCLE 7.

Esta clase permite instanciar BaseService en tests sin errores de clase abstracta.
"""

from .base_service import BaseService


class ConcreteBaseService(BaseService):
    """
    Implementación concreta de BaseService para tests.

    TDD CYCLE 7 - GREEN PHASE: Permite instanciar BaseService en tests.
    """

    def __init__(self, service_name: str = "test_service"):
        """Inicializar servicio concreto para tests."""
        super().__init__(service_name)

    def initialize(self) -> None:
        """Implementación concreta de initialize."""
        self.logger.info(f"Initializing {self.service_name}")
        # Inicialización específica del servicio
        self._setup_test_data()

    def cleanup(self) -> None:
        """Implementación concreta de cleanup."""
        self.logger.info(f"Cleaning up {self.service_name}")
        # Limpieza específica del servicio
        self._cleanup_test_data()

    def _setup_test_data(self) -> None:
        """Setup de datos de prueba."""
        self.test_data = {"initialized": True, "setup_time": "2024-01-01T00:00:00Z"}

    def _cleanup_test_data(self) -> None:
        """Limpieza de datos de prueba."""
        if hasattr(self, "test_data"):
            del self.test_data
