#!/bin/bash

# 🔧 Script para instalar y configurar pre-commit hooks
# ML API FastAPI v2

set -e

echo "🔧 Configurando pre-commit hooks..."

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Verificar que estamos en el directorio correcto
if [[ ! -f ".pre-commit-config.yaml" ]]; then
    log_error "Archivo .pre-commit-config.yaml no encontrado"
    log_error "Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

# 2. Activar ambiente virtual de Python si existe
if [[ -d "backend/venv" ]]; then
    log_info "Activando ambiente virtual..."
    
    # Detectar sistema operativo para activar correctamente
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows
        source backend/venv/Scripts/activate
    else
        # Linux/Mac
        source backend/venv/bin/activate
    fi
    
    log_success "Ambiente virtual activado"
else
    log_warning "Ambiente virtual no encontrado en backend/venv"
    log_info "Usando Python del sistema..."
fi

# 3. Instalar pre-commit
log_info "Instalando pre-commit..."
pip install pre-commit

# 4. Instalar hooks
log_info "Instalando hooks de pre-commit..."
pre-commit install

# 5. Instalar hooks adicionales
log_info "Instalando hooks adicionales..."
pre-commit install --hook-type commit-msg
pre-commit install --hook-type pre-push

# 6. Hacer permisos ejecutables a los scripts
log_info "Configurando permisos de scripts..."
chmod +x infrastructure/scripts/check_docstrings.py
chmod +x infrastructure/scripts/check_env_vars.py  
chmod +x infrastructure/scripts/check_package_versions.py

# 7. Instalar dependencias adicionales para linting
log_info "Instalando dependencias de linting..."

# Python linting tools
pip install black isort flake8 mypy bandit
pip install flake8-docstrings flake8-import-order flake8-bugbear
pip install types-requests types-redis

# 8. Crear archivos de configuración adicionales si no existen

# Configuración de isort
if [[ ! -f "backend/.isort.cfg" ]]; then
    log_info "Creando configuración de isort..."
    cat > backend/.isort.cfg << EOF
[settings]
profile = black
line_length = 88
multi_line_output = 3
include_trailing_comma = True
force_grid_wrap = 0
use_parentheses = True
ensure_newline_before_comments = True
EOF
fi

# Configuración de flake8
if [[ ! -f "backend/.flake8" ]]; then
    log_info "Creando configuración de flake8..."
    cat > backend/.flake8 << EOF
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
max-complexity = 10
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    .env,
    dist,
    build,
    migrations
EOF
fi

# Configuración de mypy
if [[ ! -f "backend/mypy.ini" ]]; then
    log_info "Creando configuración de mypy..."
    cat > backend/mypy.ini << EOF
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-tests.*]
disallow_untyped_defs = False

[mypy-migrations.*]
ignore_errors = True
EOF
fi

# 9. Ejecutar pre-commit en todos los archivos para verificar
log_info "Ejecutando pre-commit en todos los archivos..."
if pre-commit run --all-files; then
    log_success "✅ Pre-commit configurado exitosamente"
else
    log_warning "⚠️ Algunos hooks fallaron, pero pre-commit está configurado"
    log_info "Los errores se corregirán automáticamente en futuros commits"
fi

echo ""
log_success "🎉 Pre-commit hooks configurados correctamente!"
echo ""
echo "📋 Qué pasa ahora:"
echo "• Los hooks se ejecutarán automáticamente antes de cada commit"
echo "• Para ejecutar manualmente: pre-commit run --all-files"
echo "• Para saltarse hooks temporalmente: git commit --no-verify"
echo "• Para actualizar hooks: pre-commit autoupdate"
echo ""
echo "🔧 Hooks configurados:"
echo "• ✅ Formateo de código (Black, Prettier)"
echo "• ✅ Linting (Flake8, ESLint)"  
echo "• ✅ Type checking (MyPy)"
echo "• ✅ Seguridad (Bandit)"
echo "• ✅ Tests rápidos (Pytest)"
echo "• ✅ Verificaciones personalizadas" 