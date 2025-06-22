# Simple Commands - Evita problemas frecuentes de PowerShell
# Comandos robustos y directos para el proyecto

param(
    [string]$Action = "help"
)

# Configurar encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

function Show-Help {
    Write-Host "COMANDOS SIMPLES PARA ML API" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "USAR: .\scripts\simple_commands.ps1 -Action <comando>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "COMANDOS DISPONIBLES:" -ForegroundColor Green
    Write-Host "  setup      - Configurar entorno inicial" -ForegroundColor White
    Write-Host "  status     - Ver estado del repositorio" -ForegroundColor White
    Write-Host "  push       - Subir cambios al repositorio" -ForegroundColor White
    Write-Host "  quality    - Verificar calidad del código" -ForegroundColor White
    Write-Host "  test       - Ejecutar tests" -ForegroundColor White
    Write-Host "  commit     - Hacer commit con mensaje" -ForegroundColor White
    Write-Host "  clean      - Limpiar archivos temporales" -ForegroundColor White
    Write-Host ""
    Write-Host "EJEMPLOS:" -ForegroundColor Yellow
    Write-Host "  .\scripts\simple_commands.ps1 -Action setup" -ForegroundColor Cyan
    Write-Host "  .\scripts\simple_commands.ps1 -Action push" -ForegroundColor Cyan
    Write-Host "  .\scripts\simple_commands.ps1 -Action quality" -ForegroundColor Cyan
}

function Setup-Environment {
    Write-Host "🔧 Configurando entorno..." -ForegroundColor Yellow

    # Activar venv si existe
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        & ".\venv\Scripts\Activate.ps1"
        Write-Host "✅ Virtual environment activado" -ForegroundColor Green
    }

    # Verificar Python
    try {
        $pythonVersion = python --version
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python no encontrado" -ForegroundColor Red
        return
    }

    # Verificar Git
    try {
        $gitVersion = git --version
        Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Git no encontrado" -ForegroundColor Red
        return
    }

    Write-Host "🎉 Entorno configurado correctamente" -ForegroundColor Green
}

function Show-Status {
    Write-Host "📊 Estado del repositorio:" -ForegroundColor Yellow
    git status --porcelain
    Write-Host ""
    Write-Host "📝 Últimos commits:" -ForegroundColor Yellow
    git log --oneline -5
}

function Push-Changes {
    Write-Host "📤 Subiendo cambios al repositorio..." -ForegroundColor Yellow

    try {
        git push
        Write-Host "✅ Cambios subidos exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error al subir cambios" -ForegroundColor Red
        Write-Host "💡 Verificar conexión y permisos" -ForegroundColor Yellow
    }
}

function Check-Quality {
    Write-Host "🔍 Verificando calidad del código..." -ForegroundColor Yellow

    # Activar venv
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        & ".\venv\Scripts\Activate.ps1"
    }

    try {
        python infrastructure/scripts/quick_quality_check.py
    } catch {
        Write-Host "❌ Error en verificación de calidad" -ForegroundColor Red
        Write-Host "💡 Verificar que el script existe y Python está configurado" -ForegroundColor Yellow
    }
}

function Run-Tests {
    Write-Host "🧪 Ejecutando tests..." -ForegroundColor Yellow

    # Activar venv
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        & ".\venv\Scripts\Activate.ps1"
    }

    try {
        python -m pytest backend/tests/unit/test_simple_health.py -v
    } catch {
        Write-Host "❌ Error al ejecutar tests" -ForegroundColor Red
    }
}

function Make-Commit {
    $message = Read-Host "💬 Ingresa el mensaje del commit"

    if (-not $message) {
        Write-Host "ERROR: Mensaje requerido" -ForegroundColor Red
        return
    }

    Write-Host "📝 Haciendo commit: $message" -ForegroundColor Yellow

    try {
        git add .
        git commit -m $message
        Write-Host "✅ Commit realizado exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error al hacer commit" -ForegroundColor Red
    }
}

function Clean-Files {
    Write-Host "🧹 Limpiando archivos temporales..." -ForegroundColor Yellow

    # Limpiar archivos Python
    Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force
    Get-ChildItem -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force

    # Limpiar reportes antiguos
    if (Test-Path "reports\*.html") {
        Remove-Item "reports\*.html" -Force
    }

    Write-Host "✅ Limpieza completada" -ForegroundColor Green
}

# Ejecutar acción
switch ($Action.ToLower()) {
    "help" { Show-Help }
    "setup" { Setup-Environment }
    "status" { Show-Status }
    "push" { Push-Changes }
    "quality" { Check-Quality }
    "test" { Run-Tests }
    "commit" { Make-Commit }
    "clean" { Clean-Files }
    default {
        Write-Host "ERROR: Accion no reconocida: $Action" -ForegroundColor Red
        Show-Help
    }
}
