# Script para configurar el IDE correctamente
# configure_ide.ps1

Write-Host "🔧 Configurando IDE para proyecto ML-API-FastAPI-v2..." -ForegroundColor Green

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend\venv\Scripts\python.exe")) {
    Write-Host "❌ Error: No se encuentra el entorno virtual en backend\venv\" -ForegroundColor Red
    Write-Host "   Ejecuta primero: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Verificar versión de Python
Write-Host "🐍 Verificando versión de Python..."
$pythonVersion = & "backend\venv\Scripts\python.exe" --version
Write-Host "   Versión encontrada: $pythonVersion" -ForegroundColor Cyan

# Verificar que mypy esté instalado
Write-Host "🔍 Verificando mypy..."
try {
    & "backend\venv\Scripts\python.exe" -m mypy --version
    Write-Host "   ✅ mypy está instalado" -ForegroundColor Green
} catch {
    Write-Host "   ❌ mypy no está instalado. Instalando..." -ForegroundColor Yellow
    & "backend\venv\Scripts\python.exe" -m pip install mypy
}

# Verificar que flake8 esté instalado
Write-Host "🔍 Verificando flake8..."
try {
    & "backend\venv\Scripts\python.exe" -m flake8 --version
    Write-Host "   ✅ flake8 está instalado" -ForegroundColor Green
} catch {
    Write-Host "   ❌ flake8 no está instalado. Instalando..." -ForegroundColor Yellow
    & "backend\venv\Scripts\python.exe" -m pip install flake8
}

# Verificar que black esté instalado
Write-Host "🔍 Verificando black..."
try {
    & "backend\venv\Scripts\python.exe" -m black --version
    Write-Host "   ✅ black está instalado" -ForegroundColor Green
} catch {
    Write-Host "   ❌ black no está instalado. Instalando..." -ForegroundColor Yellow
    & "backend\venv\Scripts\python.exe" -m pip install black
}

# Limpiar cache de mypy
Write-Host "🧹 Limpiando cache de mypy..."
if (Test-Path ".mypy_cache") {
    Remove-Item -Recurse -Force ".mypy_cache"
    Write-Host "   ✅ Cache de mypy limpiado" -ForegroundColor Green
}

# Limpiar cache de Python
Write-Host "🧹 Limpiando cache de Python..."
Get-ChildItem -Path "backend" -Recurse -Name "__pycache__" | ForEach-Object {
    Remove-Item -Recurse -Force "backend\$_"
}
Write-Host "   ✅ Cache de Python limpiado" -ForegroundColor Green

# Ejecutar test de configuración
Write-Host "🧪 Ejecutando test de configuración..."
Write-Host "   Probando mypy en database.py..."
$mypyResult = & "backend\venv\Scripts\python.exe" -m mypy "backend\app\core\database.py" --config-file="mypy.ini" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ mypy funciona correctamente en database.py" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  mypy reporta algunos warnings (esto es normal):" -ForegroundColor Yellow
    Write-Host $mypyResult
}

Write-Host ""
Write-Host "🎉 Configuración del IDE completada!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Pasos siguientes:" -ForegroundColor Cyan
Write-Host "   1. Reinicia tu IDE (VS Code/Cursor)" -ForegroundColor White
Write-Host "   2. Presiona Ctrl+Shift+P y busca 'Python: Select Interpreter'" -ForegroundColor White
Write-Host "   3. Selecciona: .\backend\venv\Scripts\python.exe" -ForegroundColor White
Write-Host "   4. El IDE debería reconocer automáticamente la configuración" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   - Ctrl+Shift+P -> 'Tasks: Run Task' -> 'Run MyPy on Database Module'" -ForegroundColor White
Write-Host "   - Ctrl+Shift+P -> 'Tasks: Run Task' -> 'Full Code Quality Check'" -ForegroundColor White 