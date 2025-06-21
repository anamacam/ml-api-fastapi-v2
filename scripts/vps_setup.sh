#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Iniciando configuración del VPS...${NC}"

# Actualizar sistema
echo -e "${YELLOW}Actualizando sistema...${NC}"
apt update && apt upgrade -y

# Instalar herramientas básicas
echo -e "${YELLOW}Instalando herramientas básicas...${NC}"
apt install -y git curl wget vim htop python3 python3-pip python3-venv

# Instalar PostgreSQL
echo -e "${YELLOW}Instalando PostgreSQL...${NC}"
apt install -y postgresql postgresql-contrib

# Instalar Redis
echo -e "${YELLOW}Instalando Redis...${NC}"
apt install -y redis-server

# Configurar PostgreSQL
echo -e "${YELLOW}Configurando PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE DATABASE ml_api_db;"
sudo -u postgres psql -c "CREATE USER ml_api_user WITH ENCRYPTED PASSWORD 'ml_api_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ml_api_db TO ml_api_user;"

# Configurar Redis
echo -e "${YELLOW}Configurando Redis...${NC}"
sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
systemctl restart redis

# Crear directorio del proyecto
echo -e "${YELLOW}Creando estructura de directorios...${NC}"
mkdir -p /opt/ml-api
chown -R root:root /opt/ml-api

# Configurar firewall
echo -e "${YELLOW}Configurando firewall...${NC}"
apt install -y ufw
ufw allow ssh
ufw allow 8000
ufw --force enable

echo -e "${GREEN}Configuración completada!${NC}"
echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Clonar el repositorio en /opt/ml-api"
echo "2. Configurar el entorno virtual"
echo "3. Instalar dependencias del proyecto"
