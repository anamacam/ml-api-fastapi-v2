#!/usr/bin/env pwsh
<#
.SYNOPSIS
    🚀 Quick Save - Activación rápida de auto-commits

.DESCRIPTION
    Script de acceso rápido para activar protección automática
    contra pérdida de datos con configuraciones optimizadas.

.PARAMETER On
    Activar auto-commits (modo rápido, cada 3 minutos)

.PARAMETER Off  
    Desactivar auto-commits

.PARAMETER Status
    Ver estado actual

.PARAMETER Emergency
    Modo emergencia: cada 1 minuto

.EXAMPLE
    .\scripts\quick_save.ps1 -On
    Activa auto-commits rápidos cada 3 minutos

.EXAMPLE
    .\scripts\quick_save.ps1 -Emergency
    Modo emergencia cada 1 minuto

.EXAMPLE
    .\scripts\quick_save.ps1 -Off
    Desactiva auto-commits
#>

param(
    [Parameter(Mandatory = $false)]
    [switch]$On,

    [Parameter(Mandatory = $false)]
    [switch]$Off,

    [Parameter(Mandatory = $false)]
    [switch]$Status,

    [Parameter(Mandatory = $false)]
    [switch]$Emergency
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "🚀 QUICK SAVE - Protección automática" -ForegroundColor Green
Write-Host ("=" * 40) -ForegroundColor Green

if ($On) {
    Write-Host "`n⚡ Activando auto-commits RÁPIDOS..." -ForegroundColor Yellow
    Write-Host "📝 Intervalo: 3 minutos" -ForegroundColor White
    Write-Host "🔄 Auto-push: Habilitado" -ForegroundColor White
    Write-Host "⚡ Validaciones: Mínimas (modo rápido)" -ForegroundColor White
    
    & "$ScriptDir\auto_commit.ps1" -Interval 3 -Fast
    
    Write-Host "`n✅ ¡Auto-commits activados!" -ForegroundColor Green
    Write-Host "💡 Tu trabajo se guarda automáticamente cada 3 minutos" -ForegroundColor Cyan
    
} elseif ($Emergency) {
    Write-Host "`n🚨 Activando modo EMERGENCIA..." -ForegroundColor Red
    Write-Host "📝 Intervalo: 1 minuto" -ForegroundColor White
    Write-Host "🔄 Auto-push: Habilitado" -ForegroundColor White
    Write-Host "⚡ Validaciones: Bypass completo" -ForegroundColor White
    
    & "$ScriptDir\auto_commit.ps1" -Interval 1 -Fast
    
    Write-Host "`n🆘 ¡Modo emergencia activado!" -ForegroundColor Red
    Write-Host "💡 Máxima protección: guardado cada 1 minuto" -ForegroundColor Yellow
    
} elseif ($Off) {
    Write-Host "`n⏹️  Desactivando auto-commits..." -ForegroundColor Yellow
    
    & "$ScriptDir\auto_commit.ps1" -Stop
    
    Write-Host "`n⚠️  Auto-commits desactivados" -ForegroundColor Yellow
    Write-Host "💡 Recuerda hacer commits manuales frecuentes" -ForegroundColor Cyan
    
} elseif ($Status) {
    & "$ScriptDir\auto_commit.ps1" -Status
    
} else {
    Write-Host "`n🎯 OPCIONES RÁPIDAS:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚡ .\scripts\quick_save.ps1 -On        " -ForegroundColor White -NoNewline
    Write-Host "Auto-commits cada 3 min" -ForegroundColor Gray
    
    Write-Host "🚨 .\scripts\quick_save.ps1 -Emergency " -ForegroundColor White -NoNewline  
    Write-Host "Modo emergencia (1 min)" -ForegroundColor Gray
    
    Write-Host "⏹️  .\scripts\quick_save.ps1 -Off       " -ForegroundColor White -NoNewline
    Write-Host "Desactivar auto-commits" -ForegroundColor Gray
    
    Write-Host "📊 .\scripts\quick_save.ps1 -Status    " -ForegroundColor White -NoNewline
    Write-Host "Ver estado actual" -ForegroundColor Gray
    
    Write-Host "`n💡 RECOMENDACIÓN:" -ForegroundColor Yellow
    Write-Host "Para máxima protección contra fallos del PC:" -ForegroundColor White
    Write-Host ".\scripts\quick_save.ps1 -On" -ForegroundColor Green
}

Write-Host "`n🔧 CONTROLES AVANZADOS:" -ForegroundColor Blue
Write-Host "📋 .\scripts\auto_commit.ps1 -Status           - Estado detallado" -ForegroundColor Gray
Write-Host "⚙️  .\scripts\auto_commit.ps1 -Interval 5      - Intervalo personalizado" -ForegroundColor Gray
Write-Host "📜 Get-Content auto_commit.log                 - Ver log completo" -ForegroundColor Gray 