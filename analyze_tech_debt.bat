@echo off
echo 🔧 Analizador de Deuda Técnica - ML API FastAPI v2
echo =====================================================

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Ejecutar el analizador
echo 🔍 Iniciando análisis...
python infrastructure\scripts\tech_debt_analyzer.py %*

echo.
echo ✅ Análisis completado
echo 💡 Usa: analyze_tech_debt.bat --format json para generar reporte JSON
echo 💡 Usa: refactor.bat --plan para generar plan de refactoring
pause
