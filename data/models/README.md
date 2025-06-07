# 🤖 Modelos ML Entrenados

Este directorio contiene **únicamente archivos de modelos ML** y metadatos relacionados:

## 📋 Contenido

### `model_registry.json`

- **Registro de modelos**: Metadatos de todos los modelos
- **Versiones**: Tracking de versiones y métricas
- **Configuración**: Parámetros y rutas de archivos

### Archivos de modelos (`.joblib`, `.pkl`)

- **Modelos entrenados**: Serialización de modelos ML
- **Formatos soportados**: joblib, pickle, ONNX, etc.
- **Organización**: Por nombre y versión

## ✅ Debe contener:

- ✅ Archivos `.joblib`, `.pkl`, `.onnx` (modelos entrenados)
- ✅ `model_registry.json` (metadatos)
- ✅ Archivos de configuración de modelos
- ✅ Archivos de métricas y evaluación

## ❌ NO debe contener:

- ❌ Código Python (`.py`)
- ❌ Definiciones de schemas o clases
- ❌ Lógica de aplicación

## 📂 Para código de modelos:

El código Python va en:

```
backend/app/models/
├── database.py
├── schemas.py
└── README.md
```

## 🔄 Flujo típico:

1. **Entrenar modelo** → Generar `.joblib`
2. **Guardar aquí** → `data/models/modelo.joblib`
3. **Actualizar registro** → `model_registry.json`
4. **Usar en API** → Cargar desde `backend/app/services/`

## 💡 Principio:

**Separación clara entre CÓDIGO y DATOS**

- `backend/app/models/` = 🐍 Código Python
- `data/models/` = 🤖 Modelos ML entrenados
