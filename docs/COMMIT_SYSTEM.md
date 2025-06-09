# 🚀 Sistema de Commits Inteligentes

Sistema completo de validaciones automatizadas que garantiza la calidad del código antes de cada commit.

## 📋 **Scripts Disponibles**

### 🔒 **Script Principal: `commit.ps1`** (RECOMENDADO)
```powershell
# Modo interactivo (predeterminado)
.\scripts\commit.ps1

# Con mensaje directo
.\scripts\commit.ps1 -Message "feat: add user authentication"

# Modo rápido para cambios pequeños
.\scripts\commit.ps1 -Fast -Message "fix: typo in readme"
```

### 🎯 **Scripts Específicos**

#### `smart_commit_clean.ps1` - Validaciones Completas
- ✅ **Sistema OFICIAL** de validaciones
- ✅ Quality Score: **82.2/100** (Grado A)
- ✅ Tests automatizados
- ✅ Análisis de deuda técnica
- ✅ Git best practices
- ✅ Modo interactivo guiado
- 🔒 **NO permite bypasses**

```powershell
.\scripts\smart_commit_clean.ps1 -Interactive
.\scripts\smart_commit_clean.ps1 -Message "feat: add feature"
```

#### `smart_commit_fast.ps1` - Validaciones Rápidas
- ⚡ **10x más rápido** que la versión completa
- ✅ Validaciones **selectivas** (solo archivos del commit)
- ✅ Tests relacionados únicamente
- ⚠️ Menor cobertura (solo para cambios pequeños)

```powershell
.\scripts\smart_commit_fast.ps1 -Message "fix: small typo"
```

## 🔍 **Validaciones Ejecutadas**

### 1. **Mensaje de Commit** (Conventional Commits)
- ✅ Formato: `tipo(ámbito): descripción`
- ✅ Tipos válidos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- ✅ Longitud máxima: 50 caracteres
- ✅ Formato consistente

**Ejemplos válidos:**
```
feat: add user authentication system
fix(auth): resolve token validation issue
docs: update API documentation
refactor(db): optimize query performance
test: add unit tests for user service
```

### 2. **Tests Automatizados**
- ✅ Ejecución de tests unitarios
- ✅ Verificación de cobertura
- ✅ Tests relacionados con archivos modificados

### 3. **Análisis de Calidad**
- ✅ Deuda técnica
- ✅ Complejidad de código
- ✅ Estándares de codificación
- ✅ Documentación
- ✅ Score mínimo: **70/100**

### 4. **Git Best Practices**
- ✅ Tamaño de commits (atomic commits)
- ✅ Estructura de branches
- ✅ Historial limpio
- ✅ Archivos necesarios (.gitignore, README)

## 🚫 **Qué NO Está Permitido**

### ❌ **Bypasses de Validaciones**
```powershell
# ❌ NO DISPONIBLE
git commit -m "quick fix" --no-verify

# ❌ NO DISPONIBLE  
git commit -m "wip" --skip-ci
```

### ❌ **Mensajes Inválidos**
```powershell
# ❌ Muy largo
"feat: this is a very long commit message that exceeds the 50 character limit"

# ❌ Formato incorrecto
"add new feature"
"fixed bug"
"WIP"
"quick fix"

# ❌ Tipos inválidos
"added: new feature"
"bug: fix issue"
```

### ❌ **Commits Sin Validar**
- El sistema **SIEMPRE** ejecuta validaciones
- **NO** se pueden omitir checks de calidad
- **NO** se pueden hacer commits con tests fallando

## 📊 **Flujo de Trabajo**

### 1. **Desarrollo Normal**
```powershell
# 1. Hacer cambios en código
git add .

# 2. Usar sistema inteligente
.\scripts\commit.ps1 -Interactive

# 3. Seguir guía interactiva
# 4. Commit automático si todas las validaciones pasan
```

### 2. **Cambios Pequeños/Rápidos**
```powershell
# 1. Hacer cambios menores
git add file.py

# 2. Commit rápido
.\scripts\commit.ps1 -Fast -Message "fix: typo in docstring"
```

### 3. **Desarrollo con Modo Interactivo**
```powershell
# 1. Ejecutar modo interactivo
.\scripts\commit.ps1

# 2. El sistema guía paso a paso:
#    - Selección de tipo de commit
#    - Definición de ámbito
#    - Redacción de descripción
#    - Validación automática
#    - Commit final
```

## 🎯 **Beneficios del Sistema**

### ✅ **Calidad Garantizada**
- Quality Score mantenido en **82.2/100** (Grado A)
- Deuda técnica bajo control
- Tests siempre funcionando

### ✅ **Historial Git Limpio**
- Mensajes consistentes y claros
- Commits atómicos y focalizados
- Fácil navegación y reversión

### ✅ **Automatización Completa**
- Sin intervención manual en validaciones
- Detección temprana de problemas
- Feedback inmediato

### ✅ **Estándares Empresariales**
- Conventional Commits estándar
- Best practices integradas
- Auditoría completa

## 🚨 **Solución de Problemas**

### **Tests Fallan**
```powershell
# Ver detalles del error
.\scripts\test.ps1

# Ejecutar tests específicos
cd backend
python -m pytest tests/unit/test_specific.py -v
```

### **Quality Score Bajo**
```powershell
# Analizar deuda técnica
.\analyze_tech_debt.bat

# Ver reporte detallado
# Archivo generado: reports/tech_debt_report_YYYYMMDD_HHMMSS.json
```

### **Mensaje Rechazado**
```powershell
# Usar modo interactivo para guía
.\scripts\commit.ps1 -Interactive

# Verificar formato:
# tipo(ámbito): descripción ≤ 50 chars
```

## 📈 **Métricas del Sistema**

- **Quality Score Actual:** 82.2/100 (Grado A)
- **Git Practices Score:** Variable (mejorando)
- **Commits Rechazados:** ~15% (mantiene calidad)
- **Time to Commit:** 
  - Completo: ~30-60 segundos
  - Rápido: ~5-10 segundos

## 🔧 **Configuración Avanzada**

### **Variables de Entorno**
```powershell
# Opcional: Configurar timeouts
$env:COMMIT_TIMEOUT = "120"  # segundos

# Opcional: Nivel de verbosidad
$env:COMMIT_VERBOSE = "true"
```

### **Personalización**
Los scripts pueden personalizarse modificando:
- `scripts/smart_commit_clean.ps1` - Sistema completo
- `scripts/smart_commit_fast.ps1` - Sistema rápido
- `infrastructure/scripts/git_best_practices.py` - Validaciones Git

## 📚 **Referencias**

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Best Practices](docs/GIT_BEST_PRACTICES.md)
- [Quality Standards](TECHNICAL_DEBT.md)
- [Testing Guidelines](backend/tests/README.md) 