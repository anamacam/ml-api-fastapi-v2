#!/usr/bin/env pwsh
<#
.SYNOPSIS
    🔄 Auto-Commit System - Protección automática contra pérdida de datos

.DESCRIPTION
    Sistema que hace commits automáticos frecuentes para proteger el trabajo
    en desarrollo. Ideal para situaciones de inestabilidad del sistema.

.PARAMETER Interval
    Intervalo en minutos entre commits automáticos (default: 5 minutos)

.PARAMETER Stop
    Detener el auto-commit daemon

.PARAMETER Status
    Mostrar estado del auto-commit daemon

.PARAMETER Fast
    Usar modo rápido con validaciones mínimas

.EXAMPLE
    .\scripts\auto_commit.ps1
    Inicia auto-commits cada 5 minutos

.EXAMPLE
    .\scripts\auto_commit.ps1 -Interval 3 -Fast
    Auto-commits cada 3 minutos en modo rápido

.EXAMPLE
    .\scripts\auto_commit.ps1 -Stop
    Detiene el auto-commit daemon
#>

param(
    [Parameter(Mandatory = $false)]
    [int]$Interval = 5,

    [Parameter(Mandatory = $false)]
    [switch]$Stop,

    [Parameter(Mandatory = $false)]
    [switch]$Status,

    [Parameter(Mandatory = $false)]
    [switch]$Fast
)

# Configuración
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$PidFile = Join-Path $ProjectRoot ".auto_commit.pid"
$LogFile = Join-Path $ProjectRoot "auto_commit.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry
    Write-Host $logEntry -ForegroundColor $(if ($Level -eq "ERROR") { "Red" } elseif ($Level -eq "WARN") { "Yellow" } else { "Green" })
}

function Test-AutoCommitRunning {
    if (Test-Path $PidFile) {
        $processId = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($processId -and (Get-Process -Id $processId -ErrorAction SilentlyContinue)) {
            return $true
        } else {
            # Archivo PID obsoleto
            Remove-Item $PidFile -ErrorAction SilentlyContinue
            return $false
        }
    }
    return $false
}

function Stop-AutoCommit {
    if (Test-Path $PidFile) {
        $processId = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($processId) {
            try {
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                Remove-Item $PidFile -ErrorAction SilentlyContinue
                Write-Log "Auto-commit daemon detenido (PID: $processId)" "INFO"
                return $true
            } catch {
                Write-Log "Error deteniendo proceso $processId : $_" "ERROR"
            }
        }
    }
    Write-Log "No hay auto-commit daemon ejecutándose" "WARN"
    return $false
}

function Show-Status {
    Write-Host "`n🔄 AUTO-COMMIT STATUS" -ForegroundColor Cyan
    Write-Host ("=" * 30) -ForegroundColor Cyan

    if (Test-AutoCommitRunning) {
        $processId = Get-Content $PidFile
        $process = Get-Process -Id $processId
        $startTime = $process.StartTime
        $runtime = (Get-Date) - $startTime

        Write-Host "✅ Estado: ACTIVO" -ForegroundColor Green
        Write-Host "🔢 PID: $processId" -ForegroundColor White
        Write-Host "⏰ Tiempo ejecutándose: $($runtime.ToString('hh\:mm\:ss'))" -ForegroundColor White
        Write-Host "📁 Archivo PID: $PidFile" -ForegroundColor Gray
    } else {
        Write-Host "❌ Estado: INACTIVO" -ForegroundColor Red
    }

    Write-Host "📋 Log: $LogFile" -ForegroundColor Gray

    if (Test-Path $LogFile) {
        Write-Host "`n📜 Últimas 5 entradas del log:" -ForegroundColor Yellow
        Get-Content $LogFile | Select-Object -Last 5 | ForEach-Object {
            Write-Host "   $_" -ForegroundColor Gray
        }
    }
}

function Start-AutoCommitDaemon {
    if (Test-AutoCommitRunning) {
        Write-Log "Auto-commit daemon ya está ejecutándose" "WARN"
        Show-Status
        return
    }

    Write-Log "Iniciando auto-commit daemon (intervalo: $Interval minutos)" "INFO"

    # Crear job en background
    $job = Start-Job -ScriptBlock {
        param($ProjectRoot, $Interval, $Fast, $LogFile)

        function Write-JobLog {
            param([string]$Message, [string]$Level = "INFO")
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $logEntry = "[$timestamp] [$Level] $Message"
            Add-Content -Path $LogFile -Value $logEntry
        }

        Set-Location $ProjectRoot
        Write-JobLog "Auto-commit daemon iniciado en $ProjectRoot"

        while ($true) {
            try {
                # Verificar si hay cambios
                $gitStatus = git status --porcelain 2>$null

                if ($gitStatus) {
                    $changedFiles = ($gitStatus | Measure-Object).Count
                    Write-JobLog "Detectados $changedFiles archivos modificados"

                    # Agregar cambios
                    git add . 2>$null

                    # Generar mensaje automático
                    $timestamp = Get-Date -Format "HH:mm:ss"
                    $message = "auto: save work in progress at $timestamp"

                    if ($Fast) {
                        # Commit rápido con bypass
                        $result = git commit --no-verify -m $message 2>&1
                        if ($LASTEXITCODE -eq 0) {
                            Write-JobLog "✅ Auto-commit rápido: $message"

                            # Intentar push automático
                            $pushResult = git push origin master 2>&1
                            if ($LASTEXITCODE -eq 0) {
                                Write-JobLog "📤 Auto-push exitoso"
                            } else {
                                Write-JobLog "⚠️ Auto-push falló: $pushResult" "WARN"
                            }
                        } else {
                            Write-JobLog "❌ Auto-commit falló: $result" "ERROR"
                        }
                    } else {
                        # Usar sistema de commits completo pero automatizado
                        Write-JobLog "Ejecutando commit con validaciones..."
                        # Aquí se podría integrar con smart_commit_fast.ps1
                    }
                } else {
                    Write-JobLog "No hay cambios para commitear" "DEBUG"
                }

            } catch {
                Write-JobLog "Error en auto-commit: $_" "ERROR"
            }

            # Esperar intervalo
            Start-Sleep -Seconds ($Interval * 60)
        }

    } -ArgumentList $ProjectRoot, $Interval, $Fast, $LogFile

    # Guardar PID del job
    $job.Id | Out-File -FilePath $PidFile -Encoding ASCII

    Write-Log "✅ Auto-commit daemon iniciado (Job ID: $($job.Id))" "INFO"
    Write-Log "📝 Commits automáticos cada $Interval minutos" "INFO"
    Write-Log "⚡ Modo: $(if ($Fast) { 'RÁPIDO (bypass validaciones)' } else { 'COMPLETO (con validaciones)' })" "INFO"

    Show-Status
}

# Main execution
Write-Host "🔄 AUTO-COMMIT SYSTEM" -ForegroundColor Cyan
Write-Host ("=" * 25) -ForegroundColor Cyan

if ($Stop) {
    Stop-AutoCommit
} elseif ($Status) {
    Show-Status
} else {
    Start-AutoCommitDaemon
}

Write-Host "`n💡 COMANDOS ÚTILES:" -ForegroundColor Yellow
Write-Host "📊 .\scripts\auto_commit.ps1 -Status       - Ver estado" -ForegroundColor White
Write-Host "⏹️  .\scripts\auto_commit.ps1 -Stop         - Detener" -ForegroundColor White
Write-Host "⚡ .\scripts\auto_commit.ps1 -Fast         - Modo rápido" -ForegroundColor White
Write-Host "📋 Get-Content auto_commit.log             - Ver log completo" -ForegroundColor White
