# 📋 Plan de Mejoras Progresivas del Proyecto

Este documento es una hoja de ruta para mejorar la calidad, mantenibilidad y robustez del proyecto. Está basado en un análisis de deuda técnica realizado el 22 de Junio de 2024 (Score inicial: 42/100).

## ✅ Fase 1: Estabilización y Limpieza (Base)

*   [ ] **Tarea 1: Finalizar Limpieza Actual**: Hacer `git add .` y un `smart_commit` con todos los cambios de limpieza de scripts y documentación que ya realizamos. Esto nos dará una base limpia para empezar.
*   [ ] **Tarea 2: Centralizar Configuración**: Mover los archivos de configuración restantes (`.flake8`, `.pre-commit-config.yaml`, `pytest.ini`) a la carpeta `backend` para consolidar toda la configuración de Python en un solo lugar.
*   [ ] **Tarea 3: Resolver Complejidad Ciclomática (Crítico)**: Refactorizar los 5 archivos con mayor complejidad para bajar el score. Empezar con `backend/check_imports.py` y `backend/app/main.py`.
*   [ ] **Tarea 4: Eliminar Duplicación de Código (Alto)**: Identificar 3 patrones de código duplicado en `backend/tests/test_database_module.py` y refactorizarlos en funciones reutilizables o fixtures de pytest.

## 🧪 Fase 2: Calidad de Código y TDD

*   [ ] **Tarea 5: Resolver Comentarios de Deuda (Alto)**: Abordar y eliminar al menos 20 comentarios `TODO` y `HACK` del código.
*   [ ] **Tarea 6: Mejorar Calidad de Docstrings**: Añadir docstrings faltantes en todos los módulos de `backend/app/services/` para cumplir con el estándar PEP 257.
*   [ ] **Tarea 7: Incrementar Cobertura de Tests**: La "cobertura" actual parece ser un cálculo erróneo del script. El objetivo real es configurar `pytest-cov` correctamente y alcanzar al menos un **80% de cobertura** real en los módulos de `services`.
*   [ ] **Tarea 8: Actualizar Dependencias (Medio)**: Actualizar las dependencias marcadas como obsoletas (`fastapi`, `uvicorn`, etc.) a sus últimas versiones estables, validando que no haya *breaking changes*.

## 🚀 Fase 3: Optimización y CI/CD

*   [ ] **Tarea 9: Optimizar Pipeline de CI/CD**: Revisar el workflow de GitHub Actions (si existe) para añadir caching de dependencias y paralelizar los jobs de tests. Si no existe, crear uno básico.
*   [ ] **Tarea 10: Refactorizar Archivos Grandes (Alto)**: Dividir los 3 archivos más grandes (e.g., `test_database_module.py`) en módulos más pequeños y cohesivos.
*   [ ] **Tarea 11: Plan de Desarrollo Frontend**: Crear un `README.md` dentro de la carpeta `frontend` con un plan básico para desarrollar la UI, incluyendo librerías, componentes y estructura. 