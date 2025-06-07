#!/usr/bin/env python3
"""
Script para verificar versiones de dependencias en package.json.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parsear versión semántica a tupla de enteros."""
    # Remover prefijos como ^, ~, >=, etc.
    clean_version = version.lstrip('^~>=<')
    
    # Tomar solo la parte numérica antes de cualquier sufijo
    parts = clean_version.split('.')[0:3]
    
    try:
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except ValueError:
        return (0, 0, 0)


def check_package_json(file_path: Path) -> List[str]:
    """Verificar package.json."""
    if not file_path.exists():
        return [f"Archivo {file_path} no existe"]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
    except Exception as e:
        return [f"Error leyendo {file_path}: {e}"]
    
    errors = []
    
    # Verificar campos requeridos
    required_fields = ['name', 'version', 'scripts']
    for field in required_fields:
        if field not in package_data:
            errors.append(f"Campo requerido '{field}' faltante")
    
    # Verificar dependencias críticas y sus versiones mínimas
    min_versions = {
        'react': (18, 0, 0),
        'react-dom': (18, 0, 0),
        'typescript': (5, 0, 0),
        'vite': (5, 0, 0),
        '@vitejs/plugin-react': (4, 0, 0),
        'axios': (1, 6, 0),
        'react-router-dom': (6, 0, 0),
    }
    
    # Verificar dependencias de desarrollo críticas
    min_dev_versions = {
        'eslint': (8, 0, 0),
        '@typescript-eslint/eslint-plugin': (6, 0, 0),
        '@typescript-eslint/parser': (6, 0, 0),
    }
    
    # Combinar todas las dependencias
    all_dependencies = {}
    if 'dependencies' in package_data:
        all_dependencies.update(package_data['dependencies'])
    if 'devDependencies' in package_data:
        all_dependencies.update(package_data['devDependencies'])
    
    # Verificar versiones mínimas
    all_min_versions = {**min_versions, **min_dev_versions}
    
    for package, min_version in all_min_versions.items():
        if package in all_dependencies:
            current_version = parse_version(all_dependencies[package])
            if current_version < min_version:
                errors.append(
                    f"Versión de {package} muy antigua: "
                    f"{all_dependencies[package]} < {'.'.join(map(str, min_version))}"
                )
    
    # Verificar scripts requeridos
    required_scripts = ['dev', 'build']
    if 'scripts' in package_data:
        for script in required_scripts:
            if script not in package_data['scripts']:
                errors.append(f"Script '{script}' faltante en scripts")
    
    # Verificar compatibilidad de Node.js
    if 'engines' in package_data:
        if 'node' in package_data['engines']:
            node_version = package_data['engines']['node']
            # Verificar que requiera Node.js 18+
            if not any(v in node_version for v in ['18', '19', '20', '21', '22']):
                errors.append(f"Versión de Node.js muy antigua en engines: {node_version}")
    else:
        errors.append("Campo 'engines' recomendado para especificar versión de Node.js")
    
    # Verificar dependencias conflictivas
    conflicts = [
        ('react', 'preact'),  # React y Preact no deben estar juntos
        ('@types/react', '@types/preact'),
    ]
    
    for pkg1, pkg2 in conflicts:
        if pkg1 in all_dependencies and pkg2 in all_dependencies:
            errors.append(f"Dependencias conflictivas encontradas: {pkg1} y {pkg2}")
    
    # Verificar paquetes obsoletos
    obsolete_packages = {
        'create-react-app': 'Usar Vite en su lugar',
        '@types/node': 'No necesario en proyectos frontend simples',
        'moment': 'Usar date-fns o dayjs en su lugar',
    }
    
    for package, alternative in obsolete_packages.items():
        if package in all_dependencies:
            errors.append(f"Paquete obsoleto '{package}': {alternative}")
    
    # Verificar configuración de TypeScript
    if 'typescript' in all_dependencies:
        # Verificar que tenga los types necesarios
        required_types = ['@types/react', '@types/react-dom']
        for type_package in required_types:
            if type_package not in all_dependencies:
                errors.append(f"Dependencia de tipos faltante: {type_package}")
    
    return errors


def main():
    """Función principal."""
    # Buscar archivos package.json en frontend
    package_files = [
        Path("frontend/web-app/package.json"),
        Path("frontend/admin-panel/package.json"),
        Path("package.json"),  # Root package.json si existe
    ]
    
    # Filtrar archivos existentes
    existing_files = [f for f in package_files if f.exists()]
    
    if not existing_files:
        print("⚠️ No se encontraron archivos package.json")
        return 0
    
    total_errors = 0
    
    for package_file in existing_files:
        errors = check_package_json(package_file)
        if errors:
            print(f"\n📄 {package_file}:")
            for error in errors:
                print(f"  ❌ {error}")
                total_errors += 1
        else:
            print(f"✅ {package_file}: Configuración correcta")
    
    if total_errors == 0:
        print("\n✅ Todos los package.json están configurados correctamente")
        return 0
    else:
        print(f"\n❌ Encontrados {total_errors} problemas en package.json")
        print("\n💡 Tips:")
        print("   - Actualiza las dependencias a versiones más recientes")
        print("   - Agrega scripts 'dev' y 'build'")
        print("   - Especifica versión de Node.js en 'engines'")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 