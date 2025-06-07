@echo off
echo 🔄 Auto-Refactor - ML API FastAPI v2
echo ====================================

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Ejecutar el refactorizador
echo 🔄 Iniciando refactoring...
python infrastructure\scripts\auto_refactor.py %*

echo.
echo ✅ Refactoring completado
echo 💡 Usa: refactor.bat --plan para generar plan detallado
echo 💡 Usa: refactor.bat --apply para aplicar cambios (¡crea backup!)
echo ⚠️  Siempre revisa los cambios con: git diff
pause 