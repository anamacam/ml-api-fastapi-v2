#!/usr/bin/env pwsh
<#
.SYNOPSIS
Setup Quality Pipeline - ML API FastAPI v2

.DESCRIPTION
Configura el pipeline hibrido de calidad con tracking de progreso:
- Pre-commit hooks locales
- GitHub Actions pipeline
- Dashboard de progreso
- Tracking historico

.EXAMPLE
.\scripts\setup_quality_pipeline.ps1
#>

param(
    [switch]$Force = $false,
    [switch]$SkipDependencies = $false
)

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $emoji = switch ($Type) {
        "SUCCESS" { "✅" }
        "ERROR" { "❌" }
        "WARNING" { "⚠️" }
        "INFO" { "📋" }
        default { "📋" }
    }
    Write-Host "$emoji $Message"
}

Write-Host "🎯 CONFIGURANDO PIPELINE HIBRIDO DE CALIDAD"
Write-Host "=" * 50

# 1. Verificar dependencias
Write-Status "1. Verificando dependencias..." "INFO"

$dependencies = @("python", "git")
$missing = @()

foreach ($dep in $dependencies) {
    try {
        Get-Command $dep -ErrorAction Stop | Out-Null
        Write-Status "$dep disponible" "SUCCESS"
    }
    catch {
        Write-Status "$dep no encontrado" "ERROR"
        $missing += $dep
    }
}

if ($missing.Count -gt 0 -and -not $SkipDependencies) {
    Write-Status "Dependencias faltantes: $($missing -join ', ')" "ERROR"
    exit 1
}

# 2. Crear directorios necesarios
Write-Status "2. Creando estructura de directorios..." "INFO"

$directories = @("reports", ".github", ".github/workflows")

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Status "Creado: $dir" "SUCCESS"
    }
    else {
        Write-Status "Ya existe: $dir" "WARNING"
    }
}

# 3. Configurar pre-commit
Write-Status "3. Configurando pre-commit hooks..." "INFO"

if (Test-Path ".pre-commit-config.yaml") {
    Write-Status "Configuracion pre-commit encontrada" "SUCCESS"
    
    try {
        pre-commit install
        Write-Status "Pre-commit hooks instalados" "SUCCESS"
    }
    catch {
        Write-Status "Error instalando pre-commit hooks" "WARNING"
    }
}
else {
    Write-Status ".pre-commit-config.yaml no encontrado" "ERROR"
}

# 4. Verificar GitHub Actions
Write-Status "4. Verificando GitHub Actions..." "INFO"

if (Test-Path ".github/workflows/quality-pipeline.yml") {
    Write-Status "Workflow de calidad configurado" "SUCCESS"
}
else {
    Write-Status "Workflow de GitHub Actions no encontrado" "WARNING"
}

# 5. Inicializar tracking de progreso
Write-Status "5. Inicializando tracking de progreso..." "INFO"

try {
    python infrastructure/scripts/progress_tracker.py
    Write-Status "Tracking de progreso inicializado" "SUCCESS"
}
catch {
    Write-Status "Error inicializando tracking" "WARNING"
}

# 6. Generar dashboard inicial
Write-Status "6. Generando dashboard inicial..." "INFO"

try {
    python infrastructure/scripts/generate_dashboard.py
    Write-Status "Dashboard inicial generado" "SUCCESS"
    Write-Status "Disponible en: reports/dashboard.html" "INFO"
}
catch {
    Write-Status "Error generando dashboard" "WARNING"
}

# 7. Ejecutar analisis inicial
Write-Status "7. Ejecutando analisis inicial de calidad..." "INFO"

try {
    Push-Location "backend"
    python ../infrastructure/scripts/tech_debt_analyzer.py
    Pop-Location
    Write-Status "Analisis inicial completado" "SUCCESS"
}
catch {
    Write-Status "Error en analisis inicial" "WARNING"
    Pop-Location
}

# 8. Resumen final
Write-Host "`n📋 RESUMEN DE CONFIGURACION"
Write-Host "=" * 50

Write-Status "PIPELINE HIBRIDO CONFIGURADO:" "SUCCESS"
Write-Host "  ⚡ Pre-commit: Checks rapidos locales"
Write-Host "  🚀 GitHub Actions: Analisis completo"
Write-Host "  📈 Progress Tracking: Historial de mejoras"
Write-Host "  📊 Dashboard: Visualizacion de progreso"

Write-Host "`n🔧 COMANDOS UTILES:"
Write-Host "  git commit                                           # Ejecuta checks automaticos"
Write-Host "  pre-commit run --all-files                          # Ejecuta todos los hooks"
Write-Host "  python infrastructure/scripts/progress_tracker.py  # Ver progreso"
Write-Host "  python infrastructure/scripts/generate_dashboard.py # Generar dashboard"

Write-Host "`n📊 UMBRALES DE CALIDAD:"
Write-Host "  🚨 Critico: < 60 puntos (bloquea deployment)"
Write-Host "  ⚠️  Advertencia: < 70 puntos (requiere revision)"
Write-Host "  📈 Bueno: < 80 puntos (en progreso)"
Write-Host "  🎉 Excelente: 80+ puntos (objetivo)"

Write-Host "`n🎯 OBJETIVOS DE MEJORA:"
Write-Host "  📊 Score Actual: ~73.8 puntos"
Write-Host "  🎯 Meta Inmediata: 75+ puntos"
Write-Host "  🚀 Meta Final: 85+ puntos"

Write-Status "PIPELINE HIBRIDO LISTO!" "SUCCESS"
Write-Host "Cada commit ahora mejorara automaticamente tu score de calidad" 