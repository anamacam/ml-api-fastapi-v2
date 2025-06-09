#!/usr/bin/env pwsh
<#
.SYNOPSIS
    🚀 Setup del Proyecto - Configuración inicial completa

.DESCRIPTION
    Configura el entorno de desarrollo con todas las herramientas necesarias:
    - Pre-commit hooks
    - Dependencias de Python
    - Sistema de commits inteligentes
    - Validaciones de calidad

.EXAMPLE
    .\setup.ps1
#>

Write-Host "🚀 ML API FastAPI v2 - Setup del Proyecto" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Green

# Verificar si estamos en el directorio correcto
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Ejecuta este script desde el directorio raíz del proyecto" -ForegroundColor Red
    exit 1
}

# Ir al directorio backend
Write-Host "`n📁 Configurando backend..." -ForegroundColor Yellow
Set-Location "backend"

# Verificar entorno virtual
if (-not (Test-Path "venv")) {
    Write-Host "❌ Error: No se encontró entorno virtual. Créalo primero:" -ForegroundColor Red
    Write-Host "   python -m venv venv" -ForegroundColor Gray
    Set-Location ".."
    exit 1
}

# Activar entorno virtual
Write-Host "🔄 Activando entorno virtual..." -ForegroundColor Cyan
try {
    .\venv\Scripts\Activate.ps1
    Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error activando entorno virtual: $_" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

# Instalar dependencias
Write-Host "`n📦 Instalando dependencias..." -ForegroundColor Yellow
try {
    pip install -r requirements/dev.txt
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Error instalando algunas dependencias: $_" -ForegroundColor Yellow
}

# Instalar pre-commit hooks
Write-Host "`n🔧 Configurando pre-commit hooks..." -ForegroundColor Yellow
try {
    pre-commit install
    Write-Host "✅ Pre-commit hooks instalados" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Error instalando pre-commit hooks: $_" -ForegroundColor Yellow
}

# Volver al directorio raíz
Set-Location ".."

# Verificar sistema de commits
Write-Host "`n🔍 Verificando sistema de commits..." -ForegroundColor Yellow
$commitScriptExists = Test-Path "scripts/commit.ps1"
$smartCommitExists = Test-Path "scripts/smart_commit_clean.ps1"

if ($commitScriptExists -and $smartCommitExists) {
    Write-Host "✅ Sistema de commits inteligentes configurado" -ForegroundColor Green
} else {
    Write-Host "⚠️ Sistema de commits incompleto" -ForegroundColor Yellow
}

Write-Host "`n🎉 ¡Setup completado!" -ForegroundColor Green
Write-Host "`n📋 COMANDOS DISPONIBLES:" -ForegroundColor Cyan
Write-Host "🚀 .\scripts\commit.ps1                    - Sistema de commits inteligentes" -ForegroundColor White
Write-Host "⚡ .\scripts\commit.ps1 -Fast              - Commits rápidos" -ForegroundColor White
Write-Host "🧪 .\analyze_tech_debt.bat                 - Análisis de calidad completo" -ForegroundColor White
Write-Host "🔧 .\refactor.bat                          - Herramientas de refactoring" -ForegroundColor White

Write-Host "`n🔄 FLUJO DE DESARROLLO:" -ForegroundColor Cyan
Write-Host "1. Hacer cambios en código" -ForegroundColor Gray
Write-Host "2. git add ." -ForegroundColor Gray
Write-Host "3. .\scripts\commit.ps1 -Interactive" -ForegroundColor Gray
Write-Host "4. Seguir guía interactiva" -ForegroundColor Gray

Write-Host "`n✅ El sistema validará automáticamente:" -ForegroundColor Green
Write-Host "  • Formato de mensajes de commit" -ForegroundColor Gray
Write-Host "  • Tests automatizados" -ForegroundColor Gray
Write-Host "  • Análisis de calidad de código" -ForegroundColor Gray
Write-Host "  • Git best practices" -ForegroundColor Gray
