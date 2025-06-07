#!/usr/bin/env python3
"""
Script para verificar que todas las variables de entorno requeridas estén definidas.
"""

import os
import sys
from pathlib import Path
from typing import Set, List


def get_required_env_vars() -> Set[str]:
    """Obtener lista de variables de entorno requeridas del config.py."""
    required_vars = {
        'POSTGRES_SERVER',
        'POSTGRES_USER', 
        'POSTGRES_PASSWORD',
        'POSTGRES_DB',
        'POSTGRES_PORT',
        'REDIS_HOST',
        'REDIS_PORT',
        'SECRET_KEY',
        'ALGORITHM',
        'ACCESS_TOKEN_EXPIRE_MINUTES',
    }
    
    # Leer config.py para encontrar más variables
    config_file = Path("backend/app/core/config.py")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Buscar patrones como: VARIABLE: str = "valor"
            import re
            pattern = r'(\w+):\s*(?:str|int|bool|float|List\[str\])'
            matches = re.findall(pattern, content)
            
            for match in matches:
                if match.isupper():  # Solo variables en mayúsculas
                    required_vars.add(match)
                    
        except Exception as e:
            print(f"⚠️ No se pudo leer config.py: {e}")
    
    return required_vars


def check_env_file(env_file_path: Path) -> List[str]:
    """Verificar variables en un archivo .env."""
    if not env_file_path.exists():
        return [f"Archivo {env_file_path} no existe"]
    
    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"Error leyendo {env_file_path}: {e}"]
    
    # Extraer variables definidas
    defined_vars = set()
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            var_name = line.split('=')[0].strip()
            defined_vars.add(var_name)
    
    # Verificar variables requeridas
    required_vars = get_required_env_vars()
    missing_vars = required_vars - defined_vars
    
    errors = []
    if missing_vars:
        errors.append(f"Variables faltantes en {env_file_path}: {', '.join(sorted(missing_vars))}")
    
    # Verificar valores importantes
    critical_vars = {
        'SECRET_KEY': 'your-secret-key-change-in-production',
        'POSTGRES_PASSWORD': 'postgres',
        'DEBUG': 'true'
    }
    
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            parts = line.split('=', 1)
            if len(parts) == 2:
                var_name, var_value = parts[0].strip(), parts[1].strip()
                
                # Verificar valores por defecto peligrosos en producción
                if env_file_path.name.startswith('production') or env_file_path.name.startswith('prod'):
                    if var_name in critical_vars and var_value == critical_vars[var_name]:
                        errors.append(f"❗ Variable {var_name} tiene valor por defecto en producción")
                
                # Verificar que SECRET_KEY sea lo suficientemente segura
                if var_name == 'SECRET_KEY' and len(var_value.strip('"\'')) < 32:
                    errors.append(f"❗ SECRET_KEY muy corta (mínimo 32 caracteres)")
    
    return errors


def main():
    """Función principal."""
    # Archivos de configuración a verificar
    env_files = [
        Path("config/local.env"),
        Path("config/.env.example"),
        Path(".env"),
        Path("backend/.env"),
    ]
    
    # Buscar archivos de configuración existentes
    existing_files = [f for f in env_files if f.exists()]
    
    if not existing_files:
        print("⚠️ No se encontraron archivos de configuración (.env)")
        print("💡 Crea al menos uno de estos archivos:")
        for env_file in env_files:
            print(f"   - {env_file}")
        return 1
    
    total_errors = 0
    
    for env_file in existing_files:
        errors = check_env_file(env_file)
        if errors:
            print(f"\n📄 {env_file}:")
            for error in errors:
                print(f"  ❌ {error}")
                total_errors += 1
        else:
            print(f"✅ {env_file}: Configuración correcta")
    
    # Verificar variables de entorno actuales si estamos en desarrollo
    if os.getenv('DEBUG', '').lower() == 'true':
        required_vars = get_required_env_vars()
        missing_in_env = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_in_env.append(var)
        
        if missing_in_env:
            print(f"\n⚠️ Variables faltantes en el entorno actual:")
            for var in missing_in_env:
                print(f"  - {var}")
            print("\n💡 Exporta las variables o usa un archivo .env")
    
    if total_errors == 0:
        print("\n✅ Todas las variables de entorno están configuradas correctamente")
        return 0
    else:
        print(f"\n❌ Encontrados {total_errors} problemas de configuración")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 