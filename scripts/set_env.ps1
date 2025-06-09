# 🌍 Script para cambiar entornos de configuración
# Uso: .\scripts\set_env.ps1 -Environment development|testing|production

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("development", "testing", "production")]
    [string]$Environment
)

Write-Host "🌍 Configurando entorno: $Environment" -ForegroundColor Cyan

# Paths
$configDir = "config"
$sourceFile = "$configDir\$Environment.env"
$targetFile = ".env"

# Verificar que existe el archivo de configuración
if (-not (Test-Path $sourceFile)) {
    Write-Host "❌ Error: No existe el archivo $sourceFile" -ForegroundColor Red
    exit 1
}

# Copiar configuración
try {
    Copy-Item $sourceFile $targetFile -Force
    Write-Host "✅ Configuración $Environment aplicada" -ForegroundColor Green
    
    # Mostrar configuración aplicada
    Write-Host "`n📋 Configuración actual:" -ForegroundColor Yellow
    Get-Content $targetFile | Where-Object { $_ -notmatch "^#" -and $_ -ne "" } | ForEach-Object {
        Write-Host "  $_" -ForegroundColor White
    }
    
    Write-Host "`n🚀 Listo para usar entorno $Environment" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error copiando configuración: $_" -ForegroundColor Red
    exit 1
}

# Información adicional según entorno
switch ($Environment) {
    "development" {
        Write-Host "`n💡 Entorno de desarrollo:" -ForegroundColor Blue
        Write-Host "  • Modelos reales activados" -ForegroundColor White
        Write-Host "  • Debug activado" -ForegroundColor White
        Write-Host "  • CORS permisivo para localhost" -ForegroundColor White
    }
    "testing" {
        Write-Host "`n🧪 Entorno de testing:" -ForegroundColor Blue
        Write-Host "  • Modelos mock (TDD rápido)" -ForegroundColor White
        Write-Host "  • Debug desactivado" -ForegroundColor White
        Write-Host "  • Base de datos SQLite" -ForegroundColor White
    }
    "production" {
        Write-Host "`n🚀 Entorno de producción:" -ForegroundColor Blue
        Write-Host "  • Modelos reales optimizados" -ForegroundColor White
        Write-Host "  • Debug desactivado" -ForegroundColor White
        Write-Host "  • CORS configurado para producción" -ForegroundColor White
        Write-Host "  • ⚠️  Asegúrate de configurar SECRET_KEY" -ForegroundColor Yellow
    }
} 