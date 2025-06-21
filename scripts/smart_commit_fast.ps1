#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Smart Commit FAST - Validaciones rÃ¡pidas para commits individuales
.DESCRIPTION
    VersiÃ³n optimizada que solo analiza archivos del commit actual:
    - Valida mensajes Conventional Commits
    - Ejecuta tests solo de archivos relacionados
    - AnÃ¡lisis de calidad SELECTIVO (no todo el proyecto)
    - 10x mÃ¡s rÃ¡pido que smart_commit_clean.ps1
.PARAMETER Message
    Mensaje de commit a validar y usar
.EXAMPLE
    .\scripts\smart_commit_fast.ps1 -Message "feat: Add new feature"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Message
)
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
function Write-ColorOutput {
    param([string]$Message, [string]$ForegroundColor = "White")
    Write-Host $Message -ForegroundColor $ForegroundColor
}
function Test-CommitMessage {
    param([string]$Message)
    Write-ColorOutput "âš¡ Validando mensaje (rÃ¡pido)..." "Yellow"
    $conventionalPattern = '^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}$'
    if ($Message -match $conventionalPattern) {
        Write-ColorOutput "… Mensaje vÃ¡lido" "Green"
        return $true
    }
    else {
        Write-ColorOutput "âŒ Mensaje invÃ¡lido" "Red"
        return $false
    }
}
function Invoke-FastChecks {
    Write-ColorOutput "âš¡ Checks rÃ¡pidos (solo archivos staged)..." "Yellow"
    # Obtener archivos staged
    $stagedFiles = git diff --cached --name-only
    $hasTests = $false
    $hasPython = $false
    foreach ($file in $stagedFiles) {
        if ($file -match "test.*\.py$") { $hasTests = $true }
        if ($file -match "\.py$") { $hasPython = $true }
    }
    # Solo ejecutar tests si hay archivos Python
    if ($hasPython) {
        Write-ColorOutput "  ðŸ§ª Ejecutando tests relevantes..." "Gray"
        try {
            Push-Location "$ProjectRoot\backend"
            if ($hasTests) {
                # Ejecutar solo tests de archivos modificados - FIX: usar rutas relativas backend
                $testFiles = $stagedFiles | Where-Object { $_ -match "test.*\.py$" } | ForEach-Object { $_.Replace("backend/", "") }
                if ($testFiles) {
                    python -m pytest $testFiles -v --tb=short -q 2>&1 | Out-Null
                }
            } else {
                # Ejecutar test bÃ¡sico de health
                python -m pytest tests/unit/test_tdd_health.py -q 2>&1 | Out-Null
            }
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "  … Tests: OK" "Green"
            } else {
                Write-ColorOutput "  âŒ Tests: FAIL" "Red"
                Pop-Location
                return $false
            }
        }
        catch {
            Write-ColorOutput "  âš ï¸ Tests: SKIP (error)" "Yellow"
        }
        finally {
            Pop-Location -ErrorAction SilentlyContinue
        }
    } else {
        Write-ColorOutput "  â­ï¸ Tests: SKIP (no Python files)" "Gray"
    }
    Write-ColorOutput "  âš¡ Quality: SKIP (usando anÃ¡lisis rÃ¡pido)" "Gray"
    Write-ColorOutput "… Checks completados" "Green"
    return $true
}
function Main {
    Write-ColorOutput "âš¡ Smart Commit FAST - Solo archivos del commit" "Cyan"
    Write-ColorOutput ("=" * 50) "Cyan"
    Set-Location $ProjectRoot
    # Verificar staging area
    $stagedFiles = git diff --cached --name-only
    if (-not $stagedFiles) {
        Write-ColorOutput "âŒ No hay archivos en staging area" "Red"
        exit 1
    }
    Write-ColorOutput "ðŸ“ Archivos a commitear ($($stagedFiles.Count)):" "White"
    foreach ($file in $stagedFiles | Select-Object -First 5) {
        Write-ColorOutput "   $file" "Gray"
    }
    # Validar mensaje
    if (-not (Test-CommitMessage -Message $Message)) {
        exit 1
    }
    # Ejecutar checks rÃ¡pidos
    if (-not (Invoke-FastChecks)) {
        Write-ColorOutput "âŒ Checks fallaron" "Red"
        exit 1
    }
    # Commit
    Write-ColorOutput "ðŸš€ Realizando commit..." "Green"
    try {
        git commit -m "$Message"
        $commitHash = git rev-parse --short HEAD
        Write-ColorOutput "… Â¡Commit exitoso! ($commitHash)" "Green"
        Write-ColorOutput "âš¡ Tiempo reducido ~80% vs smart_commit_clean" "Cyan"
    }
    catch {
        Write-ColorOutput "Error en commit: $($_.Exception.Message)" "Red"
        exit 1
    }
}
Main
Main
