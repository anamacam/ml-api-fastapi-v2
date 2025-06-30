"""
Validador de seguridad - Extraído de settings.py

REFACTORED: Separando validaciones de seguridad en módulo independiente
- Validación de paths seguros
- Parseo seguro de booleanos
- Patrones peligrosos centralizados
"""

from pathlib import Path
from typing import Any


class SecurityValidator:
    """Validador centralizado para seguridad"""

    DANGEROUS_PATH_PATTERNS = [
        "..",
        "/etc/",
        "/var/",
        "/root/",
        "System32",
        "Windows\\System32",
        "passwd",
        "shadow",
        "secrets",
    ]

    BOOLEAN_TRUE_VALUES = ["true", "1", "yes", "on"]
    BOOLEAN_FALSE_VALUES = ["false", "0", "no", "off"]

    @classmethod
    def validate_safe_path(cls, path: Path) -> Path:
        """Validar que un path sea seguro"""
        path_str = str(path)
        for pattern in cls.DANGEROUS_PATH_PATTERNS:
            if pattern in path_str:
                raise ValueError(f"Dangerous path detected: {path_str}")
        return path

    @classmethod
    def parse_boolean_with_fallback(
        cls, value: Any, environment: str = "development"
    ) -> bool:
        """Parse booleano con fallback seguro"""
        if isinstance(value, str):
            if value.lower() in cls.BOOLEAN_TRUE_VALUES:
                return True
            elif value.lower() in cls.BOOLEAN_FALSE_VALUES:
                return False
            else:
                # Fallback seguro basado en entorno
                return environment == "production"
        return bool(value) 