# 📄 Modelos de Código Python

Este directorio contiene **únicamente código Python** para definir modelos de datos:

## 📋 Contenido

### `database.py`

- **SQLAlchemy Models**: Definiciones de tablas de base de datos
- **Entidades**: MLModel, Prediction, UploadedFile
- **Relaciones**: Foreign keys y constraints

### `schemas.py`

- **Pydantic Models**: Validación y serialización de datos
- **Request/Response schemas**: Para la API REST
- **Enums**: Estados y tipos de datos

## ❌ NO debe contener:

- ❌ Archivos `.joblib` o `.pkl` (modelos ML entrenados)
- ❌ Archivos `.json` de registro de modelos
- ❌ Datasets o archivos de datos

## 📂 Para archivos de modelos ML:

Los modelos entrenados van en:

```
data/models/
├── model_registry.json
├── modelo1.joblib
├── modelo2.pkl
└── ...
```

## 💡 Principio:

**Separación clara entre CÓDIGO y DATOS**

- `backend/app/models/` = 🐍 Código Python
- `data/models/` = 🤖 Modelos ML entrenados
