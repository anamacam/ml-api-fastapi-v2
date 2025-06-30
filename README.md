# 🤖 ML API FastAPI v2

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-18+-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)
![TDD](https://img.shields.io/badge/TDD-Enabled-green.svg)

## Descripción

Aplicación completa de Machine Learning con FastAPI, React y arquitectura de microservicios

## 🌐 Puertos y Servicios

| Servicio       | Puerto | URL                     | Descripción                |
| -------------- | ------ | ----------------------- | -------------------------- |
| Frontend Web   | 3000   | <http://localhost:3000> | 🎨 App principal React/Vue |
| Frontend Admin | 3001   | <http://localhost:3001> | ⚙️ Panel administración    |
| Backend API    | 8000   | <http://localhost:8000> | ⚡ FastAPI REST API        |
| WebSocket      | 8001   | ws://localhost:8001     | 📡 Tiempo real             |
| Metrics        | 8002   | <http://localhost:8002> | 📊 Prometheus metrics      |
| Grafana        | 3000   | <http://localhost:3000> | 📈 Dashboards              |
| PostgreSQL     | 5432   | localhost:5432          | 🗄️ Base de datos           |
| Redis          | 6379   | localhost:6379          | 🚀 Cache                   |
| Nginx          | 80     | <http://localhost>      | 🌐 Proxy reverso           |

## 📁 Estructura del Proyecto

```text
ml-api-fastapi-v2/
├── 🎨 frontend/                     # FRONTEND COMPLETO
│   ├── web-app/                     # Aplicación web principal
│   │   ├── package.json
│   │   ├── vite.config.ts          # React/TypeScript con Vite
│   │   ├── tsconfig.json           # TypeScript strict mode
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── ModelUpload.tsx  # Subir modelos ML
│   │   │   │   ├── PredictionForm.tsx # Formulario predicciones
│   │   │   │   ├── ResultsDisplay.tsx # Mostrar resultados
│   │   │   │   └── ModelList.tsx    # Lista de modelos
│   │   │   ├── pages/
│   │   │   │   ├── Home.tsx         # Página principal
│   │   │   │   ├── Predict.tsx      # Hacer predicciones
│   │   │   │   ├── Models.tsx       # Gestionar modelos
│   │   │   │   └── Dashboard.tsx    # Métricas y stats
│   │   │   ├── services/
│   │   │   │   ├── api.ts           # Cliente HTTP para backend
│   │   │   │   └── websocket.ts     # Cliente WebSocket
│   │   │   ├── App.tsx
│   │   │   └── main.tsx
│   │   ├── public/
│   │   └── dist/                    # Build para producción
│   ├── admin-panel/                 # Panel de administración
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── ModelManager.tsx # CRUD modelos
│   │   │   │   ├── UserManager.tsx  # Gestión usuarios
│   │   │   │   └── SystemHealth.tsx # Estado del sistema
│   │   │   └── pages/
│   │   └── dist/
│   └── monitoring/                  # Dashboards personalizados
│       ├── grafana-dashboards/      # JSON configs
│       └── custom-ui/               # UI monitoring custom
│
├── ⚙️ backend/                      # BACKEND COMPLETO
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app principal
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── health.py    # ✅ GET /health
│   │   │   │   │   ├── predict.py   # 🎯 POST /predict
│   │   │   │   │   ├── models.py    # 📦 CRUD /models
│   │   │   │   │   ├── upload.py    # 📤 POST /upload
│   │   │   │   │   └── websocket.py # 📡 WebSocket /ws
│   │   │   │   └── api.py           # Router principal
│   │   │   ├── dependencies.py      # Auth, DB sessions
│   │   │   └── middleware.py        # CORS, logging, etc
│   │   ├── core/
│   │   │   ├── config.py           # Settings Pydantic
│   │   │   ├── security.py         # JWT, hashing
│   │   │   └── logging.py          # Structured logging
│   │   ├── models/
│   │   │   ├── database.py         # SQLAlchemy models
│   │   │   ├── schemas.py          # Pydantic schemas
│   │   │   └── ml_models.py        # ML model wrappers
│   │   ├── services/
│   │   │   ├── prediction.py       # Lógica ML predictions
│   │   │   ├── model_manager.py    # Cargar/guardar modelos
│   │   │   ├── cache.py           # Redis caching
│   │   │   └── monitoring.py       # Métricas Prometheus
│   │   └── utils/
│   │       ├── file_handler.py     # Upload/download files
│   │       └── validators.py       # Validaciones custom
│   ├── tests/                      # 🧪 Tests TDD completos
│   │   ├── test_api/              # Tests API endpoints
│   │   ├── test_services/         # Tests lógica de negocio
│   │   ├── test_models/           # Tests modelos de datos
│   │   └── conftest.py            # Fixtures pytest
│   ├── alembic/                    # DB migrations
│   └── requirements/               # Dependencias Python
│       ├── base.txt               # Dependencias básicas
│       ├── dev.txt                # Desarrollo
│       └── prod.txt               # Producción
│
├── 🗄️ infrastructure/              # INFRAESTRUCTURA
│   ├── docker/
│   │   ├── docker-compose.yml      # Servicios completos
│   │   ├── Dockerfile.backend      # Image del backend
│   │   ├── Dockerfile.frontend     # Image del frontend
│   │   └── Dockerfile.websocket    # WebSocket service
│   ├── nginx/
│   │   ├── nginx.conf             # Config principal
│   │   └── conf.d/                # Configuraciones sitios
│   ├── scripts/
│   │   ├── setup.sh               # Setup inicial
│   │   ├── setup-precommit.sh     # Configurar pre-commit
│   │   ├── tech_debt_analyzer.py  # Analizar deuda técnica
│   │   └── tdd_setup.py           # Setup TDD
│   └── monitoring/
│       ├── prometheus.yml          # Config Prometheus
│       ├── grafana-datasources.yml # Datasources Grafana
│       └── alerts.yml              # Alertas
│
├── 📁 data/                        # DATOS LOCALES
│   ├── models/                     # Modelos ML guardados
│   │   ├── sklearn_model.pkl
│   │   ├── tensorflow_model/
│   │   └── metadata.json
│   ├── uploads/                    # Archivos subidos por usuarios
│   ├── logs/                       # Logs de la aplicación
│   ├── postgres/                   # DB PostgreSQL
│   ├── redis/                      # Cache Redis
│   └── grafana/                    # Dashboards Grafana
│
├── 📋 config/                      # CONFIGURACIÓN
│   ├── .env.example               # Ejemplo variables
│   ├── local.env                  # Config local
│   ├── production.env             # Config producción
│   └── nginx/                     # Config web server
│
├── 📚 docs/                        # DOCUMENTACIÓN
│   ├── api/                       # Docs API
│   ├── frontend/                  # Docs frontend
│   ├── deployment.md              # Guía despliegue
│   └── development.md             # Guía desarrollo
│
├── .pre-commit-config.yaml        # ✅ Quality gates (5 hooks)
├── .gitignore                     # Git ignore rules
├── pyproject.toml                 # Config Python
├── docker-compose.yml             # Servicios principales
├── README.md                      # Este archivo
├── setup_tdd.bat                  # 🧪 Setup TDD Windows
├── analyze_tech_debt.bat          # 🔍 Análisis deuda técnica
└── refactor.bat                   # 🔧 Scripts refactoring
```

## 🧪 Calidad de Código y Testing

Este proyecto se adhiere a una estricta política de **Test-Driven Development (TDD)** y mantiene altos estándares de calidad de código.

| Principio      | Descripción              | Beneficio              |
| -------------- | ------------------------ | ---------------------- |
| **Test First** | Tests antes que código   | 🎯 Diseño claro        |
| **YAGNI**      | You Aren't Gonna Need It | 🚀 Código simple       |
| **DRY**        | Don't Repeat Yourself    | 🔧 Mantenible          |
| **SOLID**      | Principios diseño        | 📐 Arquitectura sólida |

Para una explicación detallada sobre nuestra filosofía de TDD, estructura de tests y guías de desarrollo, consulta los siguientes documentos:

- **[📄 Filosofía TDD Optimizada](TDD_STUB_PHILOSOPHY_OPTIMIZADA.md)**
- **[📄 Sistema de Commits Inteligentes](docs/COMMIT_SYSTEM.md)**
- **[📄 Buenas Prácticas de Git](docs/GIT_BEST_PRACTICES.md)**
- **[📄 Deuda Técnica y Estándares](TECHNICAL_DEBT.md)**

## 🎨 Calidad de Código

Este proyecto mantiene altos estándares de calidad mediante herramientas automatizadas y procesos de revisión:

### 🔍 **Herramientas de Linting:**

| Herramienta | Propósito | Configuración |
|-------------|-----------|---------------|
| **flake8** | Linting Python | `backend/.flake8` |
| **black** | Formateo código | `pyproject.toml` |
| **isort** | Ordenar imports | `pyproject.toml` |
| **mypy** | Type checking | `mypy.ini` |
| **pre-commit** | Hooks automáticos | `.pre-commit-config.yaml` |

### 📋 **Configuración de Linting:**

El proyecto utiliza una configuración personalizada de `flake8` que:

- **Excluye directorios irrelevantes** (entornos virtuales, `node_modules`, etc.)
- **Ignora errores no críticos** para enfocarse en problemas importantes
- **Permite complejidad moderada** en funciones de análisis
- **Documenta deuda técnica** aceptada temporalmente

📖 **Ver documentación completa:** [`docs/LINTING_CONFIGURATION.md`](docs/LINTING_CONFIGURATION.md)

### 🚀 **Comandos de Calidad:**

```bash
# Verificar calidad completa
pre-commit run --all-files

# Linting específico
flake8 .

# Formateo automático
black .
isort .

# Type checking
mypy .

# Análisis de deuda técnica
python infrastructure/scripts/tech_debt_analyzer.py
```

### 📊 **Métricas de Calidad:**

| Métrica | Objetivo | Actual | Estado |
|---------|----------|--------|--------|
| **Score Total** | >60 | **42.3/100** | 🔴 F (CRÍTICO) |
| **Flake8 Errors** | 0 | **Varios** | 🔴 Pendiente |
| **Code Complexity** | <10 | **23.1/20** | 🔴 CRÍTICO |
| **TDD Tests** | >70% | **74.1%** | 🟡 Aceptable |
| **Documentation** | >80% | **86.8%** | ✅ Bueno |
| **Architecture** | Modular | **En progreso** | 🟡 Mejorando |

## 🚀 Inicio Rápido

### 1️⃣ **Clonar y Setup:**

```bash
git clone https://github.com/anamacam/ml-api-fastapi-v2.git
cd ml-api-fastapi-v2

# Activar ambiente virtual
.\backend\venv\Scripts\Activate.ps1  # Windows
source backend/venv/bin/activate      # Linux/Mac

# Instalar dependencias backend
pip install -r backend/requirements/base.txt

# Instalar dependencias frontend
cd frontend/web-app
npm install
```

### 2️⃣ **Pre-commit Hooks (Calidad):**

```bash
# Instalar pre-commit
pre-commit install

# Ejecutar hooks manualmente
pre-commit run --all-files
```

### 3️⃣ **Levantar Servicios:**

```bash
# Desarrollo individual
uvicorn backend.app.main:app --reload --port 8000  # Backend
cd frontend/web-app && npm run dev                 # Frontend

# O con Docker (todos los servicios)
docker-compose up -d
```

### 4️⃣ **Verificar Servicios:**

- **🎨 Frontend**: <http://localhost:3000>
- **⚡ API Docs**: <http://localhost:8000/docs>
- **✅ Health Check**: <http://localhost:8000/api/v1/health>
- **📊 Metrics**: <http://localhost:8002/metrics>

## 🛠️ Tecnologías

### **Backend:**

- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos principal
- **Redis** - Cache y sesiones
- **Prometheus** - Métricas y monitoring

### **Frontend:**

- **React 18** - Librería UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool rápido
- **Axios** - Cliente HTTP
- **Tailwind CSS** - Styling

### **DevOps:**

- **Docker** - Containerización
- **Nginx** - Proxy reverso
- **Grafana** - Dashboards
- **Pre-commit** - Quality gates

## 🔧 Scripts Disponibles

```bash
# TDD y Testing
./setup_tdd.bat              # Configurar TDD
pytest backend/tests/         # Ejecutar tests

# Análisis de Código
./analyze_tech_debt.bat       # Analizar deuda técnica
./refactor.bat               # Scripts refactoring

# Frontend
cd frontend/web-app
npm run dev                   # Desarrollo
npm run build                # Build producción
npm run preview              # Preview build

# Backend
uvicorn backend.app.main:app --reload  # Desarrollo
```

## 📊 Características

### ✅ **Funcionalidades Core**
- ✅ **API REST** completa con FastAPI
- ✅ **Frontend React** con TypeScript
- ✅ **WebSockets** para tiempo real
- ✅ **Caché Redis** para performance
- ✅ **Base de datos PostgreSQL**
- ✅ **Monitoring** con Prometheus/Grafana

### 🟡 **Calidad y Testing** 
- 🟡 **1949+ Tests** implementados (74.1% TDD score)
- 🟡 **Pipeline parcial** de calidad (basic)
- ✅ **Smart commit system** con validaciones
- ✅ **Pre-commit hooks** (5 hooks funcionando)
- 🟡 **Arquitectura** en proceso de mejora

### 🟡 **DevOps y Deployment**
- ✅ **Docker** para containerización
- ✅ **Nginx** como proxy reverso
- 🟡 **Métricas básicas** disponibles
- 🟡 **Tracking manual** de progreso
- ✅ **Documentación** en proceso de mejora

### 🚨 **Estado Crítico del Proyecto**
- 🔴 **Grado F** (42.3/100) - Estado crítico
- 📊 **Complejidad crítica** (23.1/20) 
- 🧪 **TDD parcial** (74.1%) - Necesita mejoras
- 📚 **86.8% documentación** - Lo único positivo

## 🚨 Situación Actual - Análisis Real

### 📊 **Estado Crítico Identificado**

El análisis real de deuda técnica revela una situación crítica que requiere atención inmediata:

| Métrica | Actual | Estado | Acción Requerida |
|---------|--------|--------|------------------|
| **Score Total** | **42.3/100 (F)** | 🔴 CRÍTICO | Refactoring urgente |
| **Complejidad** | **23.1/20** | 🔴 CRÍTICO | Dividir funciones |
| **TODOs Pendientes** | **165** | 🟠 ALTO | Resolver deuda técnica |
| **Archivos Grandes** | **23** | 🟠 ALTO | Dividir módulos |
| **Duplicación** | **107 patrones** | 🟠 ALTO | Extraer funciones comunes |
| **Documentación** | **86.8%** | ✅ BUENO | Mantener |

### 🎯 **Plan de Recuperación (3 meses)**
- **🚑 Semanas 1-2**: Crítico → Grado D (67+ puntos)
- **📈 Semanas 3-6**: Grado D → Grado B (81+ puntos)  
- **🚀 Semanas 7-12**: Grado B → Grado A (89+ puntos)

**Ver detalles completos:** [📄 Plan de Recuperación](IMPROVEMENT_PLAN.md) | [📄 Análisis de Deuda](TECHNICAL_DEBT.md)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Hacer commit (`git commit -m 'feat: agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

---

**🚀 ¡Happy coding with TDD!** 🧪
