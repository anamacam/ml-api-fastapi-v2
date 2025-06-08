#!/bin/bash

# 🚀 ML API FastAPI v2 - Script de Configuración Inicial
# Este script configura todo el ambiente de desarrollo

set -e  # Salir si hay errores

echo "🚀 Configurando ML API FastAPI v2..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logs
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

# Verificar sistema operativo
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

log_info "Sistema detectado: $MACHINE"

# 1. Verificar Python 3.8+
log_info "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    log_success "Python $PYTHON_VERSION encontrado"
else
    log_error "Python3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

# 2. Verificar Node.js 18+
log_info "Verificando Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    log_success "Node.js $NODE_VERSION encontrado"
else
    log_error "Node.js no encontrado. Por favor instala Node.js 18+"
    exit 1
fi

# 3. Verificar Docker
log_info "Verificando Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    log_success "Docker encontrado: $DOCKER_VERSION"
else
    log_warning "Docker no encontrado. Se puede usar sin Docker."
fi

# 4. Crear ambiente virtual Python
log_info "Creando ambiente virtual Python..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_success "Ambiente virtual creado"
else
    log_warning "Ambiente virtual ya existe"
fi

# 5. Activar ambiente virtual e instalar dependencias
log_info "Instalando dependencias Python..."

# Detectar como activar el ambiente virtual
if [ "$MACHINE" = "MinGw" ] || [ "$MACHINE" = "Cygwin" ]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements/base.txt

log_success "Dependencias Python instaladas"

cd ..

# 6. Configurar Frontend Web App
log_info "Configurando Frontend Web App..."
cd frontend/web-app

if [ ! -d "node_modules" ]; then
    npm install
    log_success "Dependencias del frontend instaladas"
else
    log_warning "Dependencias del frontend ya instaladas"
fi

cd ../..

# 7. Configurar Frontend Admin Panel
log_info "Configurando Frontend Admin Panel..."
cd frontend/admin-panel

# Crear package.json básico si no existe
if [ ! -f "package.json" ]; then
    cat > package.json << EOF
{
  "name": "ml-api-admin-panel",
  "version": "2.0.0",
  "description": "Panel de administración para ML API",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^7.1.1",
    "axios": "^1.7.9"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.7"
  }
}
EOF
fi

if [ ! -d "node_modules" ]; then
    npm install
    log_success "Dependencias del admin panel instaladas"
else
    log_warning "Dependencias del admin panel ya instaladas"
fi

cd ../..

# 8. Crear archivos de configuración
log_info "Creando archivos de configuración..."

# Archivo .env
if [ ! -f "config/local.env" ]; then
    cat > config/local.env << EOF
# 🔧 Configuración Local - ML API FastAPI v2

# Base de datos
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ml_api_db
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT
SECRET_KEY=your-secret-key-change-in-production-$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_STR=/api/v1
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:80"]

# Archivos
UPLOAD_DIR=data/uploads
MODELS_DIR=data/models
MAX_FILE_SIZE=10485760

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/logs/app.log

# Desarrollo
DEBUG=true
RELOAD=true
EOF
    log_success "Archivo de configuración local creado"
fi

# 9. Crear directorios necesarios
log_info "Creando directorios..."
mkdir -p data/{uploads,models,logs,postgres,redis,grafana,prometheus,nginx/logs}
mkdir -p frontend/monitoring/grafana-dashboards
mkdir -p infrastructure/{nginx/conf.d,monitoring}

log_success "Directorios creados"

# 10. Configurar base de datos (si Docker está disponible)
if command -v docker &> /dev/null; then
    log_info "Iniciando servicios de base de datos..."
    docker-compose up -d postgres redis
    log_success "Servicios de base de datos iniciados"

    # Esperar a que la base de datos esté lista
    log_info "Esperando a que PostgreSQL esté listo..."
    sleep 10
fi

log_success "🎉 ¡Configuración completada!"

echo ""
echo "📋 Próximos pasos:"
echo "1. Copia config/local.env a .env y personaliza las variables"
echo "2. Para ejecutar el backend:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Para ejecutar el frontend:"
echo "   cd frontend/web-app && npm run dev"
echo "4. Para ejecutar con Docker:"
echo "   docker-compose up -d"
echo ""
echo "🌐 URLs de acceso:"
echo "• Frontend Web: http://localhost:3000"
echo "• Frontend Admin: http://localhost:3001"
echo "• Backend API: http://localhost:8000"
echo "• API Docs: http://localhost:8000/docs"
echo "• Grafana: http://localhost:3000 (admin/admin)"
echo "• Prometheus: http://localhost:8002"
