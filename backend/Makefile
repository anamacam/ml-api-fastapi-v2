# ======================================
# 🚀 ML API FastAPI v2 - Makefile
# ======================================

.PHONY: help install test tdd quality clean lint format setup check-all

# Variables
PYTHON = python
PIP = pip
PYTEST = pytest
PROJECT_ROOT = .
BACKEND_ROOT = backend

# Color codes for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

# ======================================
# 📋 HELP - Comandos disponibles
# ======================================
help:
	@echo "🚀 ML API FastAPI v2 - Comandos Disponibles"
	@echo "=========================================="
	@echo ""
	@echo "🔧 $(GREEN)Setup y Instalación:$(NC)"
	@echo "  make setup     - Configuración inicial completa"
	@echo "  make install   - Instalar dependencias"
	@echo ""
	@echo "🧪 $(GREEN)Testing y TDD:$(NC)"
	@echo "  make test      - Ejecutar todos los tests"
	@echo "  make tdd       - Ejecutar tests en modo TDD (watch)"
	@echo "  make coverage  - Generar reporte de cobertura"
	@echo ""
	@echo "🔍 $(GREEN)Calidad de Código:$(NC)"
	@echo "  make quality   - Ejecutar checklist de calidad completo"
	@echo "  make lint      - Ejecutar linters (flake8)"
	@echo "  make format    - Formatear código (black)"
	@echo "  make check-all - Ejecutar todos los checks de calidad"
	@echo ""
	@echo "🧹 $(GREEN)Limpieza:$(NC)"
	@echo "  make clean     - Limpiar archivos temporales"
	@echo ""

# ======================================
# 🔧 SETUP Y INSTALACIÓN
# ======================================
setup: clean install
	@echo "$(GREEN)✅ Setup completo realizado$(NC)"

install:
	@echo "$(YELLOW)📦 Instalando dependencias...$(NC)"
	cd $(BACKEND_ROOT) && $(PIP) install -r requirements/base.txt
	cd $(BACKEND_ROOT) && $(PIP) install -r requirements/test.txt
	@echo "$(GREEN)✅ Dependencias instaladas$(NC)"

# ======================================
# 🧪 TESTING Y TDD
# ======================================
test:
	@echo "$(YELLOW)🧪 Ejecutando tests...$(NC)"
	cd $(BACKEND_ROOT) && $(PYTEST) -v
	@echo "$(GREEN)✅ Tests completados$(NC)"

tdd:
	@echo "$(YELLOW)🔄 Modo TDD activado (Ctrl+C para salir)...$(NC)"
	cd $(BACKEND_ROOT) && $(PYTEST) -f --tb=short

coverage:
	@echo "$(YELLOW)📊 Generando reporte de cobertura...$(NC)"
	cd $(BACKEND_ROOT) && $(PYTEST) --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Reporte de cobertura generado en htmlcov/$(NC)"

# ======================================
# 🔍 CALIDAD DE CÓDIGO
# ======================================
quality:
	@echo "$(YELLOW)🔍 Ejecutando Checklist de Calidad Automatizado...$(NC)"
	cd $(BACKEND_ROOT) && $(PYTHON) infrastructure/scripts/quick_quality.py
	@echo "$(GREEN)✅ Análisis de calidad completado$(NC)"

lint:
	@echo "$(YELLOW)🔧 Ejecutando linter (flake8)...$(NC)"
	cd $(BACKEND_ROOT) && flake8 app tests --max-line-length=88 --exclude=__pycache__
	@echo "$(GREEN)✅ Linting completado$(NC)"

format:
	@echo "$(YELLOW)🎨 Formateando código (black)...$(NC)"
	cd $(BACKEND_ROOT) && black app tests --line-length=88
	@echo "$(GREEN)✅ Formateo completado$(NC)"

check-all: lint test quality
	@echo "$(GREEN)🎉 ¡Todos los checks de calidad pasaron!$(NC)"

# ======================================
# 🔄 INTEGRACIÓN TDD + CALIDAD
# ======================================
tdd-quality:
	@echo "$(YELLOW)🚀 TDD + Calidad: Ejecutando ciclo completo...$(NC)"
	@make test
	@make quality
	@echo "$(GREEN)✅ Ciclo TDD + Calidad completado$(NC)"

# ======================================
# 🧹 LIMPIEZA
# ======================================
clean:
	@echo "$(YELLOW)🧹 Limpiando archivos temporales...$(NC)"
	find $(BACKEND_ROOT) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(BACKEND_ROOT) -type f -name "*.pyc" -delete 2>/dev/null || true
	find $(BACKEND_ROOT) -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(BACKEND_ROOT)/.pytest_cache 2>/dev/null || true
	rm -rf $(BACKEND_ROOT)/htmlcov 2>/dev/null || true
	rm -rf $(BACKEND_ROOT)/.coverage 2>/dev/null || true
	rm -f quality_report.txt 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

# ======================================
# 🎯 COMANDOS ESPECÍFICOS TDD
# ======================================
red:
	@echo "$(RED)🔴 RED: Ejecutando test que debe fallar...$(NC)"
	cd $(BACKEND_ROOT) && $(PYTEST) -v --tb=short || echo "$(RED)✅ Test falló como esperado (RED phase)$(NC)"

green:
	@echo "$(GREEN)🟢 GREEN: Ejecutando tests para pasar...$(NC)"
	cd $(BACKEND_ROOT) && $(PYTEST) -v
	@echo "$(GREEN)✅ Tests pasaron (GREEN phase)$(NC)"

refactor: test quality
	@echo "$(YELLOW)🔄 REFACTOR: Tests + Calidad después de refactor...$(NC)"
	@echo "$(GREEN)✅ Refactor validado$(NC)"

# ======================================
# 📊 REPORTES Y ANÁLISIS
# ======================================
tech-debt:
	@echo "$(YELLOW)📊 Analizando deuda técnica...$(NC)"
	cd $(BACKEND_ROOT) && $(PYTHON) infrastructure/scripts/tech_debt_analyzer.py
	@echo "$(GREEN)✅ Análisis de deuda técnica completado$(NC)"

report-json:
	@echo "$(YELLOW)📋 Generando reporte JSON...$(NC)"
	cd $(BACKEND_ROOT) && $(PYTHON) infrastructure/scripts/quality_checklist.py --format json --output quality_report.json
	@echo "$(GREEN)✅ Reporte JSON generado$(NC)"

# ======================================
# 🚀 COMANDO PRINCIPAL INTEGRADO
# ======================================
dev: clean install test quality
	@echo "$(GREEN)🎉 ¡Entorno de desarrollo listo!$(NC)"
	@echo "$(YELLOW)📋 Próximos pasos:$(NC)"
	@echo "  - Ejecuta: make tdd (para desarrollo TDD)"
	@echo "  - Ejecuta: make quality (para check de calidad)"
	@echo "  - Ejecuta: make check-all (para validación completa)"
