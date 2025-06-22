# Fix PowerShell Configuration for ML API Project
# Ejecutar una vez para configurar el entorno correctamente

Write-Host "🔧 Configurando PowerShell para ML API Project..." -ForegroundColor Cyan

# 1. Configurar encoding UTF-8
Write-Host "📝 Configurando encoding UTF-8..." -ForegroundColor Yellow
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# 2. Configurar política de ejecución (si es necesario)
Write-Host "🔐 Verificando política de ejecución..." -ForegroundColor Yellow
$currentPolicy = Get-ExecutionPolicy
if ($currentPolicy -eq "Restricted") {
    Write-Host "⚠️ Política restrictiva detectada. Configurando RemoteSigned..." -ForegroundColor Red
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "✅ Política actualizada a RemoteSigned" -ForegroundColor Green
    } catch {
        Write-Host "❌ No se pudo cambiar la política. Ejecutar como administrador." -ForegroundColor Red
    }
} else {
    Write-Host "✅ Política de ejecución OK: $currentPolicy" -ForegroundColor Green
}

# 3. Verificar Python y venv
Write-Host "🐍 Verificando Python..." -ForegroundColor Yellow
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "✅ Virtual environment encontrado" -ForegroundColor Green

    # Activar venv
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activado" -ForegroundColor Green

    # Verificar Python
    python --version
    Write-Host "✅ Python verificado" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment no encontrado en .\venv\" -ForegroundColor Red
    Write-Host "💡 Ejecutar: python -m venv venv" -ForegroundColor Yellow
}

# 4. Configurar Git (si es necesario)
Write-Host "📦 Verificando Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git OK: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git no encontrado en PATH" -ForegroundColor Red
}

# 5. Configurar variables de entorno del proyecto
Write-Host "🌍 Configurando variables de entorno..." -ForegroundColor Yellow
$env:PROJECT_ROOT = Get-Location
$env:BACKEND_PATH = Join-Path $env:PROJECT_ROOT "backend"
$env:SCRIPTS_PATH = Join-Path $env:PROJECT_ROOT "scripts"

Write-Host "✅ PROJECT_ROOT: $env:PROJECT_ROOT" -ForegroundColor Green
Write-Host "✅ BACKEND_PATH: $env:BACKEND_PATH" -ForegroundColor Green
Write-Host "✅ SCRIPTS_PATH: $env:SCRIPTS_PATH" -ForegroundColor Green

# 6. Crear aliases útiles
Write-Host "🔗 Creando aliases útiles..." -ForegroundColor Yellow

function Invoke-QualityCheck {
    python infrastructure/scripts/quick_quality_check.py
}

function Invoke-TechDebtAnalysis {
    python infrastructure/scripts/tech_debt_analyzer.py --format console
}

function Invoke-ProgressTracker {
    python infrastructure/scripts/progress_tracker.py
}

function Invoke-SmartCommit {
    param([string]$Message)
    if ($Message) {
        & ".\scripts\smart_commit_clean.ps1" -Message $Message
    } else {
        Write-Host "❌ Uso: smart-commit 'mensaje del commit'" -ForegroundColor Red
    }
}

# Crear aliases
Set-Alias -Name "quality-check" -Value Invoke-QualityCheck
Set-Alias -Name "debt-analysis" -Value Invoke-TechDebtAnalysis
Set-Alias -Name "progress" -Value Invoke-ProgressTracker
Set-Alias -Name "smart-commit" -Value Invoke-SmartCommit

Write-Host "✅ Aliases creados:" -ForegroundColor Green
Write-Host "  - quality-check    : Verificación rápida de calidad" -ForegroundColor Cyan
Write-Host "  - debt-analysis    : Análisis de deuda técnica" -ForegroundColor Cyan
Write-Host "  - progress         : Tracking de progreso" -ForegroundColor Cyan
Write-Host "  - smart-commit     : Commit inteligente" -ForegroundColor Cyan

# 7. Verificar herramientas del proyecto
Write-Host "🛠️ Verificando herramientas del proyecto..." -ForegroundColor Yellow

$tools = @(
    @{Name="Black"; Command="python -m black --version"},
    @{Name="Pytest"; Command="python -m pytest --version"},
    @{Name="Flake8"; Command="python -m flake8 --version"}
)

foreach ($tool in $tools) {
    try {
        $version = Invoke-Expression $tool.Command 2>$null
        Write-Host "✅ $($tool.Name): OK" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ $($tool.Name): No disponible" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 CONFIGURACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 COMANDOS ÚTILES:" -ForegroundColor Yellow
Write-Host "  git status                    - Ver estado del repositorio" -ForegroundColor White
Write-Host "  git push                      - Subir cambios" -ForegroundColor White
Write-Host "  quality-check                 - Verificar calidad del código" -ForegroundColor White
Write-Host "  debt-analysis                 - Análizar deuda técnica" -ForegroundColor White
Write-Host "  smart-commit 'mensaje'        - Commit con validaciones" -ForegroundColor White
Write-Host ""
Write-Host "🚀 ¡Listo para desarrollar con calidad!" -ForegroundColor Green
