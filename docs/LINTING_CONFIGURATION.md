# Configuración de Linting - ML API FastAPI v2

## Resumen

Este documento explica las decisiones de configuración de `flake8` y otros linters en el proyecto.

## Configuración de `.flake8`

### Exclusiones de Directorios

```ini
exclude =
    .git,
    __pycache__,
    .pytest_cache,
    .venv,
    venv,
    backend/venv,
    frontend/web-app/node_modules,
    htmlcov,
    reports,
    build,
    dist,
    *.egg-info
```

**¿Por qué excluimos estos directorios?**

- **Entornos virtuales** (`.venv`, `venv`, `backend/venv`): Contienen dependencias de terceros que no son responsabilidad de nuestro código
- **`node_modules`**: Dependencias del frontend JavaScript/TypeScript
- **`reports`**, **`htmlcov`**: Artefactos generados automáticamente
- **`build`**, **`dist`**: Archivos compilados/generados

### Errores Ignorados Globalmente

```ini
extend-ignore = E203, W503, E501
```

**E203 (whitespace before ':')**: Conflicto con `black` formatter
**W503 (line break before binary operator)**: Conflicto con `black` formatter  
**E501 (line too long)**: Ignorado temporalmente para enfocarse en errores críticos

### Complejidad Ciclomática

```ini
max-complexity = 18
```

**¿Por qué 18?**
- Valor estándar que permite funciones moderadamente complejas
- Funciones más complejas requieren refactorización
- Se puede ajustar según las necesidades del proyecto

### Configuración por Archivo

```ini
per-file-ignores =
    __init__.py:F401
    tests/*: D100, D101, D102, D103, D104
```

**`__init__.py:F401`**: Los archivos `__init__.py` pueden tener imports no utilizados intencionalmente
**`tests/*: D100-D104`**: Los tests no requieren docstrings completos

## Deuda Técnica Aceptada

### Funciones con Complejidad C901

Las siguientes funciones tienen complejidad ciclomática alta y están marcadas con `# noqa: C901`:

1. **`tech_debt_analyzer.py`**:
   - `_analyze_docstrings_quality()` - Complejidad: 18
   - `_analyze_tdd_practices()` - Complejidad: 25  
   - `_analyze_dependencies()` - Complejidad: 13

2. **`quick_quality_check.py`**:
   - `_check_file_basics()` - Complejidad: 13

**Plan de Refactorización**:
- [ ] Dividir funciones complejas en métodos más pequeños
- [ ] Extraer lógica común a funciones helper
- [ ] Implementar patrones de diseño apropiados
- [ ] Prioridad: Baja (funciones de análisis, no críticas para el negocio)

## Recomendaciones

### Para Nuevos Códigos

1. **Mantener complejidad < 10** para funciones críticas
2. **Documentar decisiones** cuando se ignore un error
3. **Usar `# noqa`** con comentario explicativo
4. **Crear issues** para deuda técnica aceptada

### Para Refactorización

1. **Priorizar por impacto**: Funciones críticas primero
2. **Mantener tests**: Asegurar que la refactorización no rompa funcionalidad
3. **Documentar cambios**: Explicar por qué se refactoriza
4. **Revisar métricas**: Verificar que la complejidad se reduce

## Comandos Útiles

```bash
# Verificar configuración
flake8 --show-config

# Analizar archivo específico
flake8 path/to/file.py

# Ignorar errores específicos temporalmente
flake8 --extend-ignore=E501,W503 .

# Generar reporte detallado
flake8 --statistics --count .
```

## Referencias

- [Flake8 Documentation](https://flake8.pycqa.org/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Cyclomatic Complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity) 