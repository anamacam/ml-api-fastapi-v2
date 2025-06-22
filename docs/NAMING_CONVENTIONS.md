# 📋 Convenciones de Nomenclatura - ML API FastAPI v2

Esta guía establece las convenciones estándar para nombrar archivos, directorios, variables, funciones y clases en nuestro proyecto.

## 📁 Archivos y Directorios

### 🗂️ **Directorios**

| Tipo | Convención | Ejemplo | Descripción |
|------|------------|---------|-------------|
| **Principales** | `kebab-case` | `web-app/`, `admin-panel/` | Directorios raíz del proyecto |
| **Python packages** | `snake_case` | `prediction_service/`, `ml_models/` | Paquetes Python |
| **Frontend** | `kebab-case` | `src/components/`, `public/assets/` | Directorios frontend |
| **Config** | `lowercase` | `config/`, `docs/`, `scripts/` | Configuración y utilitarios |

### 📄 **Archivos por Tecnología**

#### **Python (.py)**

| Tipo | Convención | Ejemplo | Descripción |
|------|------------|---------|-------------|
| **Módulos** | `snake_case` | `prediction_service.py`, `user_model.py` | Archivos Python |
| **Tests** | `test_` prefix | `test_user_model.py`, `test_tdd_health.py` | Tests con prefijo |
| **Clases** | **PascalCase** en archivo `snake_case` | `UserModel` en `user_model.py` | Clase en archivo descriptivo |
| **Utilities** | `snake_case` | `file_handler.py`, `validators.py` | Funciones utilitarias |
| **Scripts** | `snake_case` | `git_best_practices.py`, `tech_debt_analyzer.py` | Scripts de automatización |

✅ **Ejemplos CORRECTOS:**
```
backend/app/models/user.py               # ✅ Modelo usuario
backend/app/services/prediction_service.py # ✅ Servicio predicción
backend/tests/unit/test_user_model.py    # ✅ Test unitario
infrastructure/scripts/git_best_practices.py # ✅ Script análisis
```

❌ **Ejemplos INCORRECTOS:**
```
backend/app/models/User.py               # ❌ PascalCase archivo
backend/app/services/predictionService.py # ❌ camelCase
backend/tests/unit/UserModelTest.py      # ❌ Sin prefijo test_
infrastructure/scripts/gitBestPractices.py # ❌ camelCase script
```

#### **TypeScript/JavaScript (.ts/.js)**

| Tipo | Convención | Ejemplo | Descripción |
|------|------------|---------|-------------|
| **Componentes React** | **PascalCase** | `UserProfile.tsx`, `PredictionForm.tsx` | Componentes UI |
| **Servicios** | `camelCase` | `api.ts`, `websocket.ts` | Servicios y utilidades |
| **Pages** | **PascalCase** | `Home.tsx`, `Dashboard.tsx` | Páginas principales |
| **Types/Interfaces** | `camelCase` | `types.ts`, `interfaces.ts` | Definiciones de tipos |
| **Tests** | `.test.` o `.spec.` | `UserProfile.test.tsx`, `api.spec.ts` | Tests frontend |

✅ **Ejemplos CORRECTOS:**
```
frontend/web-app/src/components/UserProfile.tsx  # ✅ Componente React
frontend/web-app/src/services/api.ts            # ✅ Servicio API
frontend/web-app/src/pages/Dashboard.tsx        # ✅ Página principal
frontend/web-app/src/types/interfaces.ts        # ✅ Definiciones tipos
```

#### **Configuración y Scripts**

| Tipo | Convención | Ejemplo | Descripción |
|------|------------|---------|-------------|
| **Config** | `lowercase` + extensión | `nginx.conf`, `pytest.ini` | Archivos configuración |
| **Docker** | **PascalCase** prefix | `Dockerfile.backend`, `Dockerfile.frontend` | Dockerfiles específicos |
| **Scripts PowerShell** | `snake_case` | `smart_commit_clean.ps1`, `smart_commit_fast.ps1` | Scripts automatización |
| **Batch** | `snake_case` | `setup_tdd.bat`, `analyze_tech_debt.bat` | Scripts Windows |
| **Environment** | `.env` pattern | `.env.example`, `local.env` | Variables entorno |

#### **Documentación**

| Tipo | Convención | Ejemplo | Descripción |
|------|------------|---------|-------------|
| **Markdown** | **UPPERCASE** principales | `README.md`, `CHANGELOG.md` | Docs principales |
| **Guías** | **SCREAMING_SNAKE_CASE** | `GIT_BEST_PRACTICES.md`, `NAMING_CONVENTIONS.md` | Guías técnicas |
| **Docs específicas** | `lowercase` | `deployment.md`, `development.md` | Documentación específica |

## 🔤 Variables y Funciones

### **Python**

| Elemento | Convención | Ejemplo | Descripción |
|----------|------------|---------|-------------|
| **Variables** | `snake_case` | `user_name`, `prediction_result` | Variables locales |
| **Constantes** | `SCREAMING_SNAKE_CASE` | `API_BASE_URL`, `MAX_FILE_SIZE` | Constantes globales |
| **Funciones** | `snake_case` | `get_user_data()`, `validate_input()` | Funciones |
| **Clases** | **PascalCase** | `UserModel`, `PredictionService` | Clases |
| **Métodos privados** | `_snake_case` | `_validate_data()`, `_process_result()` | Métodos privados |
| **Métodos especiales** | `__snake_case__` | `__init__()`, `__str__()` | Métodos mágicos |

✅ **Ejemplos Python CORRECTOS:**
```python
# Variables y constantes
user_name = "john_doe"
API_BASE_URL = "https://api.example.com"
MAX_RETRY_ATTEMPTS = 3

# Funciones
def get_user_predictions(user_id: int) -> List[Prediction]:
    """Obtiene predicciones del usuario."""
    return prediction_service.get_by_user_id(user_id)

def validate_prediction_input(data: dict) -> bool:
    """Valida datos de entrada para predicción."""
    return _check_required_fields(data)

# Clases
class PredictionService:
    """Servicio para manejar predicciones ML."""

    def __init__(self):
        self._model_cache = {}

    def _load_model(self, model_id: str):
        """Carga modelo en cache privadamente."""
        pass
```

### **TypeScript/JavaScript**

| Elemento | Convención | Ejemplo | Descripción |
|----------|------------|---------|-------------|
| **Variables** | `camelCase` | `userName`, `predictionResult` | Variables locales |
| **Constantes** | `SCREAMING_SNAKE_CASE` | `API_BASE_URL`, `DEFAULT_TIMEOUT` | Constantes globales |
| **Funciones** | `camelCase` | `getUserData()`, `validateInput()` | Funciones |
| **Clases** | **PascalCase** | `UserModel`, `ApiService` | Clases |
| **Interfaces** | **PascalCase** con `I` | `IUser`, `IPrediction` | Interfaces |
| **Types** | **PascalCase** | `UserType`, `PredictionData` | Tipos personalizados |
| **Componentes** | **PascalCase** | `UserProfile`, `PredictionForm` | Componentes React |

✅ **Ejemplos TypeScript CORRECTOS:**
```typescript
// Variables y constantes
const userName = "johnDoe";
const API_BASE_URL = "https://api.example.com";
const DEFAULT_TIMEOUT = 5000;

// Interfaces y tipos
interface IUser {
  id: number;
  name: string;
  email: string;
}

type PredictionData = {
  modelId: string;
  inputData: Record<string, any>;
};

// Funciones
const getUserPredictions = async (userId: number): Promise<IPrediction[]> => {
  return await apiService.get(`/users/${userId}/predictions`);
};

// Componentes React
const UserProfile: React.FC<{ user: IUser }> = ({ user }) => {
  return <div>{user.name}</div>;
};

// Clases
class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async get(endpoint: string): Promise<any> {
    // implementación
  }
}
```

## 🗄️ Base de Datos

### **Tablas y Columnas (SQL)**

| Elemento | Convención | Ejemplo | Descripción |
|----------|------------|---------|-------------|
| **Tablas** | `snake_case` plural | `users`, `ml_predictions` | Nombres descriptivos plurales |
| **Columnas** | `snake_case` | `user_id`, `created_at` | Descriptivas y específicas |
| **Claves primarias** | `id` | `id` | Siempre `id` simple |
| **Claves foráneas** | `table_id` | `user_id`, `model_id` | Referencia clara a tabla |
| **Índices** | `idx_table_column` | `idx_users_email`, `idx_predictions_date` | Prefijo descriptivo |
| **Constraints** | `type_table_column` | `fk_predictions_user_id`, `uk_users_email` | Tipo y descripción |

✅ **Ejemplos SQL CORRECTOS:**
```sql
-- Tablas
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ml_predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    model_id VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    prediction_result JSONB NOT NULL,
    confidence_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_predictions_user_id
        FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Índices
CREATE INDEX idx_predictions_user_id ON ml_predictions(user_id);
CREATE INDEX idx_predictions_created_at ON ml_predictions(created_at);
CREATE UNIQUE INDEX uk_users_email ON users(email);
```

## 🌐 URLs y APIs

### **Endpoints REST**

| Convención | Ejemplo | Descripción |
|------------|---------|-------------|
| **Recursos** en plural | `/api/v1/users` | Colecciones de recursos |
| **kebab-case** para palabras múltiples | `/api/v1/ml-predictions` | Separado por guiones |
| **Verbos HTTP** explícitos | `GET /users`, `POST /users` | Sin verbos en URL |
| **IDs** como path params | `/users/{user_id}` | Identificadores en ruta |
| **Filtros** como query params | `/users?status=active&page=1` | Parámetros de consulta |

✅ **Ejemplos API CORRECTOS:**
```
GET    /api/v1/users                    # ✅ Listar usuarios
POST   /api/v1/users                    # ✅ Crear usuario
GET    /api/v1/users/{user_id}          # ✅ Obtener usuario específico
PUT    /api/v1/users/{user_id}          # ✅ Actualizar usuario
DELETE /api/v1/users/{user_id}          # ✅ Eliminar usuario

GET    /api/v1/ml-predictions           # ✅ Listar predicciones
POST   /api/v1/ml-predictions           # ✅ Crear predicción
GET    /api/v1/ml-models                # ✅ Listar modelos ML
POST   /api/v1/file-uploads             # ✅ Subir archivos

# Con filtros
GET /api/v1/users?status=active&role=admin&page=1&limit=20
GET /api/v1/ml-predictions?user_id=123&model_id=rf_model&date_from=2024-01-01
```

## 📦 Paquetes y Módulos

### **Python Packages**

```
backend/
├── app/                    # ✅ Paquete principal aplicación
│   ├── __init__.py
│   ├── api/               # ✅ Paquete API
│   │   ├── __init__.py
│   │   └── v1/            # ✅ Versionado API
│   ├── core/              # ✅ Funcionalidad core
│   ├── models/            # ✅ Modelos de datos
│   ├── services/          # ✅ Lógica de negocio
│   └── utils/             # ✅ Utilidades
├── tests/                 # ✅ Tests separados
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── requirements/          # ✅ Dependencias organizadas
    ├── base.txt
    ├── dev.txt
    └── prod.txt
```

### **Frontend Modules**

```
frontend/web-app/src/
├── components/            # ✅ Componentes reutilizables
│   ├── common/           # ✅ Componentes comunes
│   ├── forms/            # ✅ Formularios
│   └── layout/           # ✅ Layout components
├── pages/                # ✅ Páginas principales
├── services/             # ✅ Servicios API
├── hooks/                # ✅ Custom hooks React
├── utils/                # ✅ Utilidades
├── types/                # ✅ Definiciones TypeScript
└── styles/               # ✅ Estilos CSS/SCSS
```

## ✅ Checklist de Verificación

### **Antes de Crear Archivo:**

- [ ] ✅ Nombre sigue convención de tecnología
- [ ] ✅ Es descriptivo y específico
- [ ] ✅ No usa abreviaciones ambiguas
- [ ] ✅ Está en directorio correcto
- [ ] ✅ Extensión es apropiada

### **Antes de Nombrar Variable/Función:**

- [ ] ✅ Usa convención del lenguaje (snake_case/camelCase)
- [ ] ✅ Es descriptiva y clara
- [ ] ✅ No usa nombres reservados
- [ ] ✅ Sigue patrones del proyecto
- [ ] ✅ Es pronunciable y buscable

### **Antes de Crear API Endpoint:**

- [ ] ✅ Usa recursos en plural
- [ ] ✅ Usa kebab-case para palabras múltiples
- [ ] ✅ No incluye verbos en URL
- [ ] ✅ Sigue estructura RESTful
- [ ] ✅ Usa versionado (`/v1/`)

## 🔧 Herramientas de Validación

El proyecto incluye herramientas automáticas para validar convenciones:

```bash
# Análisis de convenciones Python
python infrastructure/scripts/tech_debt_analyzer.py

# Validación de Git best practices
python infrastructure/scripts/git_best_practices.py

# Pre-commit hooks automáticos
git commit  # Ejecuta validaciones automáticamente
```

## 📚 Referencias

- **[PEP 8](https://pep8.org/)**: Guía de estilo Python
- **[Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)**: Convenciones TypeScript
- **[REST API Naming Conventions](https://restfulapi.net/resource-naming/)**: Convenciones APIs REST
- **[SQL Style Guide](https://www.sqlstyle.guide/)**: Convenciones SQL

---

**Nota**: Estas convenciones están integradas en nuestro sistema de calidad y se validan automáticamente en cada commit mediante pre-commit hooks. ¡Mantengamos el código limpio y consistente! 🚀
