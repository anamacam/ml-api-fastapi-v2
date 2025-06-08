@echo off
echo 🧪 TDD Setup - ML API FastAPI v2
echo ===============================

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Ejecutar configuración TDD
echo 🚀 Configurando Test-Driven Development...
python infrastructure\scripts\tdd_setup.py --full

echo.
echo ✅ TDD configurado exitosamente!
echo.
echo 💡 Próximos pasos:
echo    1. cd backend ^&^& pytest
echo    2. cd frontend\web-app ^&^& npm test
echo    3. Lee TDD_GUIDE.md para empezar
echo    4. Sigue el ciclo: Red → Green → Refactor
echo.
echo 🔴 RED: Escribir test que falle
echo 🟢 GREEN: Código mínimo para pasar
echo 🔵 REFACTOR: Mejorar manteniendo tests
pause
