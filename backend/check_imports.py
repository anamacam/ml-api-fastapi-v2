# -*- coding: utf-8 -*-
"""
Script para verificar que todas las importaciones del proyecto funcionen correctamente
"""
import importlib
import sys
from pathlib import Path


def check_imports():
    """Verificar todas las importaciones críticas del proyecto"""

    # Lista de módulos críticos a verificar
    critical_modules = [
        "numpy",
        "pandas",
        "pydantic",
        "pydantic_settings",
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "psycopg2",
        "redis",
        "scikit-learn",
        "joblib",
        "structlog",
        "prometheus_client",
        "cryptography",
        "bcrypt",
        "httpx",
        "aiofiles",
        "pyyaml",
        "toml",
    ]

    print("🔍 Verificando importaciones del proyecto...")
    print(f"📁 Directorio actual: {Path.cwd()}")
    print(f"🐍 Python path: {sys.executable}")
    print(f"📦 Python version: {sys.version}")
    print()

    failed_imports = []
    successful_imports = []

    for module in critical_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            successful_imports.append(module)
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)

    print()
    print("📊 Resumen:")
    print(f"✅ Importaciones exitosas: {len(successful_imports)}")
    print(f"❌ Importaciones fallidas: {len(failed_imports)}")

    if failed_imports:
        print(f"\n❌ Módulos que fallaron: {', '.join(failed_imports)}")
        return False
    else:
        print("\n🎉 ¡Todas las importaciones funcionan correctamente!")
        return True


def check_project_imports():
    """Verificar importaciones específicas del proyecto"""

    print("\n🔍 Verificando importaciones del proyecto...")

    project_modules = [
        "app.config.settings",
        "app.core.database",
        "app.core.security",
        "app.models.api_models",
        "app.services.prediction_service",
        "app.utils.data_validators",
    ]

    failed_project_imports = []

    for module in project_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_project_imports.append(module)

    if failed_project_imports:
        print(
            "\\n❌ Módulos del proyecto que fallaron: "
            f"{', '.join(failed_project_imports)}"
        )
        return False
    else:
        print("\n🎉 ¡Todas las importaciones del proyecto funcionan!")
        return True


if __name__ == "__main__":
    print("🚀 Iniciando verificación de importaciones...")
    print("=" * 50)

    # Verificar dependencias externas
    external_ok = check_imports()

    # Verificar módulos del proyecto
    project_ok = check_project_imports()

    print("=" * 50)
    if external_ok and project_ok:
        print("🎉 ¡Todas las verificaciones pasaron exitosamente!")
        sys.exit(0)
    else:
        print("❌ Algunas verificaciones fallaron")
        sys.exit(1)
