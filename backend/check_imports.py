# -*- coding: utf-8 -*-
"""
Script para verificar que todas las importaciones del proyecto funcionen correctamente
"""
import importlib
import sys
from pathlib import Path
from typing import List, Tuple


def get_critical_modules() -> List[str]:
    """Retorna la lista de módulos críticos a verificar"""
    return [
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


def get_project_modules() -> List[str]:
    """Retorna la lista de módulos del proyecto a verificar"""
    return [
        "app.config.settings",
        "app.core.database",
        "app.core.security",
        "app.models.api_models",
        "app.services.prediction_service",
        "app.utils.data_validators",
    ]


def print_environment_info():
    """Imprime información del entorno de ejecución"""
    print("🔍 Verificando importaciones del proyecto...")
    print(f"📁 Directorio actual: {Path.cwd()}")
    print(f"🐍 Python path: {sys.executable}")
    print(f"📦 Python version: {sys.version}")
    print()


def test_single_import(module: str) -> Tuple[bool, str]:
    """Prueba la importación de un módulo específico"""
    try:
        importlib.import_module(module)
        return True, ""
    except ImportError as e:
        return False, str(e)


def check_module_list(modules: List[str], module_type: str) -> Tuple[List[str], List[str]]:
    """Verifica una lista de módulos y retorna éxitos y fallos"""
    failed_imports = []
    successful_imports = []

    for module in modules:
        success, error = test_single_import(module)
        if success:
            print(f"✅ {module}")
            successful_imports.append(module)
        else:
            print(f"❌ {module}: {error}")
            failed_imports.append(module)

    return successful_imports, failed_imports


def print_summary(successful: List[str], failed: List[str], module_type: str):
    """Imprime el resumen de las verificaciones"""
    print()
    print("📊 Resumen:")
    print(f"✅ Importaciones exitosas: {len(successful)}")
    print(f"❌ Importaciones fallidas: {len(failed)}")

    if failed:
        print(f"\n❌ Módulos que fallaron: {', '.join(failed)}")
        return False
    else:
        print(f"\n🎉 ¡Todas las importaciones {module_type} funcionan correctamente!")
        return True


def check_imports() -> bool:
    """Verificar todas las importaciones críticas del proyecto"""
    critical_modules = get_critical_modules()
    print_environment_info()
    
    successful_imports, failed_imports = check_module_list(critical_modules, "críticas")
    return print_summary(successful_imports, failed_imports, "críticas")


def check_project_imports() -> bool:
    """Verificar importaciones específicas del proyecto"""
    print("\n🔍 Verificando importaciones del proyecto...")
    
    project_modules = get_project_modules()
    successful_imports, failed_imports = check_module_list(project_modules, "del proyecto")
    return print_summary(successful_imports, failed_imports, "del proyecto")


def main():
    """Función principal que ejecuta todas las verificaciones"""
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


if __name__ == "__main__":
    main()
