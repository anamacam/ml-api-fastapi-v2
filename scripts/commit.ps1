#!/usr/bin/env pwsh
<#
.SYNOPSIS
    🚀 Alias para Smart Commit - Acceso rápido al sistema de validaciones

.DESCRIPTION
    Alias que ejecuta el script principal smart_commit_clean.ps1
    con todas las validaciones de calidad completas.

.PARAMETER Message
    Mensaje de commit

.PARAMETER Interactive
    Modo interactivo

.PARAMETER Fast
    Usar versión rápida (smart_commit_fast.ps1)

.EXAMPLE
    .\scripts\commit.ps1 -Interactive

.EXAMPLE
    .\scripts\commit.ps1 -Message "feat: add feature"

.EXAMPLE
    .\scripts\commit.ps1 -Fast -Message "fix: typo"
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$Message,

    [Parameter(Mandatory = $false)]
    [switch]$Interactive,

    [Parameter(Mandatory = $false)]
    [switch]$Fast
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Mostrar header
Write-Host "🚀 Smart Commit System" -ForegroundColor Cyan
Write-Host ("=" * 25) -ForegroundColor Cyan

if ($Fast) {
    Write-Host "⚡ Usando versión RÁPIDA (validaciones selectivas)" -ForegroundColor Yellow
    
    if ([string]::IsNullOrWhiteSpace($Message)) {
        Write-Host "❌ Versión rápida requiere mensaje" -ForegroundColor Red
        Write-Host "Uso: .\scripts\commit.ps1 -Fast -Message 'feat: description'" -ForegroundColor Gray
        exit 1
    }
    
    & "$ScriptDir\smart_commit_fast.ps1" -Message $Message
} else {
    Write-Host "🔒 Usando versión COMPLETA (todas las validaciones)" -ForegroundColor Green
    
    if ($Interactive) {
        & "$ScriptDir\smart_commit_clean.ps1" -Interactive
    } elseif (-not [string]::IsNullOrWhiteSpace($Message)) {
        & "$ScriptDir\smart_commit_clean.ps1" -Message $Message
    } else {
        # Modo interactivo por defecto si no se proporciona mensaje
        & "$ScriptDir\smart_commit_clean.ps1" -Interactive
    }
} 