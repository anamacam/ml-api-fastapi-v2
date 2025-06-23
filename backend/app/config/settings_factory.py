"""
Factory de configuración - Extraído de settings.py

REFACTORED: Separando factory pattern en módulo independiente
- Creación de configuraciones por entorno
- Factory methods centralizados
"""

from typing import Dict, Any

from .environment import Environment
from .settings import Settings


class SettingsFactory:
    """Factory para crear configuraciones por entorno"""

    @classmethod
    def create_development_settings(cls, **overrides) -> Settings:
        """Crear configuración para desarrollo"""
        return Settings(
            environment=Environment.DEVELOPMENT,
            debug=True,
            use_real_models=False,  # Usar mocks en desarrollo por defecto
            **overrides,
        )

    @classmethod
    def create_testing_settings(cls, **overrides) -> Settings:
        """Crear configuración para testing"""
        return Settings(
            environment=Environment.TESTING,
            debug=True,
            use_real_models=False,  # Nunca usar modelos reales en testing
            **overrides,
        )

    @classmethod
    def create_production_settings(cls, **overrides) -> Settings:
        """Crear configuración para producción"""
        return Settings(
            environment=Environment.PRODUCTION,
            debug=False,
            use_real_models=True,
            **overrides,
        ) 