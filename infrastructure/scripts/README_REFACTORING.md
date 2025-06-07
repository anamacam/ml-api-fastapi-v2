# 🔧 Scripts de Refactoring Automático

Esta documentación explica cómo usar los scripts de análisis y refactoring para evitar y reducir la deuda técnica.

## 🎯 Objetivos

- **Detectar automáticamente** patrones de deuda técnica
- **Sugerir refactorings** específicos y accionables
- **Aplicar fixes automáticos** seguros
- **Generar reportes** detallados para priorizar tareas
- **Prevenir nueva deuda técnica** mediante análisis continuo

## 📄 Scripts Disponibles

### 1. `tech_debt_analyzer.py` - Analizador de Deuda Técnica

Detecta y reporta issues de deuda técnica existente.

**Características:**

- ✅ Análisis AST de código Python
- ✅ Detección de complejidad ciclomática
- ✅ Identificación de funciones largas
- ✅ Verificación de docstrings faltantes
- ✅ Detección de duplicación de código
- ✅ Análisis de patrones problemáticos
- ✅ Reportes en múltiples formatos

### 2. `auto_refactor.py` - Refactorizador Automático

Aplica refactorings automáticos y genera planes de acción.

**Características:**

- ✅ Extracción de constantes (números mágicos)
- ✅ Agrupación de parámetros en dataclasses
- ✅ Detección de strings duplicados
- ✅ Identificación de anidamiento excesivo
- ✅ Detección de variables no utilizadas
- ✅ Backup automático antes de cambios

## 🚀 Uso Básico

### Analizar Deuda Técnica

```bash
# Análisis básico con reporte en consola
python infrastructure/scripts/tech_debt_analyzer.py

# Análizar directorios específicos
python infrastructure/scripts/tech_debt_analyzer.py --dirs backend/app frontend/web-app/src

# Generar reporte JSON
python infrastructure/scripts/tech_debt_analyzer.py --format json

# Ver issues auto-reparables
python infrastructure/scripts/tech_debt_analyzer.py --auto-fix --dry-run
```

### Refactorizar Automáticamente

```bash
# Vista previa de refactorings (modo seguro)
python infrastructure/scripts/auto_refactor.py --dry-run

# Generar plan detallado de refactoring
python infrastructure/scripts/auto_refactor.py --plan

# Aplicar refactorings automáticos (¡crea backup!)
python infrastructure/scripts/auto_refactor.py --apply

# Analizar directorios específicos
python infrastructure/scripts/auto_refactor.py --dirs backend/app --plan
```

## 📊 Tipos de Issues Detectados

### 🔴 Críticos

- **Errores de parsing**: Código que no puede ser analizado
- **Funciones ultra-complejas**: Complejidad > 15
- **Clases "God"**: Más de 20 métodos

### 🟠 Altos

- **Complejidad alta**: Complejidad ciclomática 10-15
- **Archivos grandes**: Más de 500 líneas
- **Anidamiento excesivo**: Más de 3 niveles

### 🟡 Medios

- **Funciones largas**: Más de 50 líneas
- **Docstrings faltantes**: Funciones/clases públicas sin documentar
- **Demasiados parámetros**: Más de 7 parámetros
- **Print statements**: En código de producción

### 🔵 Bajos

- **TODOs/FIXMEs**: Comentarios pendientes
- **Líneas largas**: Más de 120 caracteres
- **Strings mágicos**: Strings hardcodeados repetidos

## 🔧 Refactorings Automáticos

### ✅ Seguros (Se aplican automáticamente)

- **Extracción de constantes**: Números mágicos → constantes
- **Extracción de strings**: Strings duplicados → constantes
- **Reemplazo de prints**: `print()` → `logger.info()`

### ⚠️ Requieren Revisión Manual

- **Extract Parameter Object**: Muchos parámetros → dataclass
- **Extract Method**: Funciones grandes → métodos pequeños
- **Reduce Nesting**: Condiciones anidadas → early returns
- **Remove Unused Variables**: Variables no utilizadas

## 📈 Workflow Recomendado

### 1. Análisis Inicial

```bash
# Obtener estado actual
python infrastructure/scripts/tech_debt_analyzer.py --format json

# Generar plan de refactoring
python infrastructure/scripts/auto_refactor.py --plan
```

### 2. Priorización

- Revisar `tech_debt_report.json`
- Leer `REFACTOR_PLAN.md`
- Priorizar issues **🔴 críticos** y **🟠 altos**

### 3. Refactoring Seguro

```bash
# Aplicar fixes automáticos seguros
python infrastructure/scripts/auto_refactor.py --apply

# Verificar cambios
git diff

# Confirmar si todo está bien
git add -A && git commit -m "refactor: apply automatic tech debt fixes"
```

### 4. Refactoring Manual

- Usar `REFACTOR_PLAN.md` como guía
- Aplicar refactorings complejos manualmente
- Crear tests para código refactorizado

### 5. Verificación Final

```bash
# Re-analizar después de cambios
python infrastructure/scripts/tech_debt_analyzer.py

# Verificar que los issues disminuyeron
```

## 🔄 Integración Continua

### Pre-commit Hook

Agregar al `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: tech-debt-analyzer
      name: Tech Debt Analyzer
      entry: python infrastructure/scripts/tech_debt_analyzer.py
      language: python
      files: '\.py$'
      pass_filenames: false
```

### CI/CD Pipeline

```yaml
# En tu workflow de GitHub Actions
- name: Analyze Tech Debt
  run: |
    python infrastructure/scripts/tech_debt_analyzer.py --format json
    # Fallar si hay issues críticos
    if [ $(jq '.summary.by_severity.critical // 0' tech_debt_report.json) -gt 0 ]; then
      echo "❌ Issues críticos detectados"
      exit 1
    fi
```

## 📋 Ejemplos de Output

### Reporte de Consola

```
📊 REPORTE DE DEUDA TÉCNICA
================================================================================

📈 Estadísticas:
   Archivos analizados: 15
   Issues encontrados: 23
   Auto-reparables: 8

🚨 Por severidad:
   🔴 Critical: 2
   🟠 High: 5
   🟡 Medium: 12
   🔵 Low: 4

🔧 Por tipo:
   • Missing Docstring: 8
   • High Complexity: 3
   • Long Function: 4
   • Magic String: 2
```

### Plan de Refactoring

```markdown
## Extract Constant

**3 acciones identificadas**

### `backend/app/main.py:45`

**Descripción**: Extraer número mágico 3600 a constante
**Código actual**: `timeout = 3600`
**Refactoring sugerido**: `TIMEOUT_SECONDS = 3600`
```

## 🎯 Métricas de Éxito

### Objetivos Cuantitativos

- **Reducir complejidad promedio** < 8
- **Eliminar issues críticos** = 0
- **Documentar 100%** de funciones públicas
- **Mantener archivos** < 300 líneas

### Métricas de Seguimiento

```bash
# Generar métricas semanalmente
python infrastructure/scripts/tech_debt_analyzer.py --format json
echo "Issues críticos: $(jq '.summary.by_severity.critical // 0' tech_debt_report.json)"
echo "Funciones sin documentar: $(jq '.summary.by_type.missing_docstring // 0' tech_debt_report.json)"
```

## 🚨 Limitaciones y Precauciones

### ⚠️ Limitaciones

- **Análisis estático**: No ejecuta el código
- **Falsos positivos**: Algunos patrones pueden ser intencionales
- **Python only**: Solo analiza archivos `.py`
- **Refactorings básicos**: Los cambios complejos requieren intervención manual

### 🛡️ Precauciones

- **Siempre revisar** los cambios antes de aplicar
- **Usar git** para trackear cambios
- **Probar después** de refactorizar
- **Crear backups** automáticamente

## 🔗 Recursos Adicionales

### Lecturas Recomendadas

- [Refactoring by Martin Fowler](https://refactoring.com/)
- [Clean Code by Robert Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Python Code Quality Tools](https://realpython.com/python-code-quality/)

### Herramientas Complementarias

- **Black**: Formateo automático
- **isort**: Ordenamiento de imports
- **MyPy**: Type checking
- **Bandit**: Análisis de seguridad
- **Pylint**: Linting avanzado

---

💡 **Consejo**: Ejecuta estos scripts **regularmente** para mantener la calidad del código y evitar acumular deuda técnica.
