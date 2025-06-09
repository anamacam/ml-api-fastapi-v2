#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Smart Commit TDD - Versión temporal para desarrollo TDD

.DESCRIPTION
    Versión optimizada temporalmente para commits de desarrollo TDD:
    - Valida mensajes Conventional Commits (mantiene calidad)
    - Ejecuta tests relevantes (mantiene calidad)
    - SKIP análisis completo de proyecto (acelera proceso)
    - Usar solo durante desarrollo TDD, después volver a smart_commit_clean.ps1

.PARAMETER Message
    Mensaje de commit a validar y usar

.EXAMPLE
    .\scripts\smart_commit_tdd.ps1 -Message "feat(tdd): implement function"
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
    
    Write-ColorOutput "Validando mensaje de commit..." "Yellow"
    $conventionalPattern = '^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}$'
    
    if ($Message -match $conventionalPattern) {
        Write-ColorOutput "Mensaje válido (Score: 100/100)" "Green"
        return $true
    }
    else {
        Write-ColorOutput "Mensaje inválido (Score: 0/100)" "Red"
        Write-ColorOutput "Issues encontrados:" "Red"
        
        if ($Message.Length -gt 50) {
            Write-ColorOutput "  - Muy largo ($($Message.Length) chars, max 50)" "Red"
        }
        if (-not ($Message -match '^(feat|fix|docs|style|refactor|test|chore)')) {
            Write-ColorOutput "  - Debe empezar con: feat, fix, docs, style, refactor, test, chore" "Red"
        }
        if (-not ($Message -match ': ')) {
            Write-ColorOutput "  - Debe tener formato: tipo(scope): descripcion" "Red"
        }
        
        return $false
    }
}

function Invoke-TDDChecks {
    Write-ColorOutput "Ejecutando checks TDD (optimizados)..." "Yellow"
    $allPassed = $true

    # Test unitarios (mantener calidad)
    Write-ColorOutput "  - Ejecutando tests..." "Gray"
    try {
        Push-Location "$ProjectRoot\backend"
        python -m pytest tests/unit/test_tdd_health.py -v --tb=short 2>&1 | Out-Null
        $testResult = $LASTEXITCODE
        Pop-Location

        if ($testResult -eq 0) {
            Write-ColorOutput "  - Tests: PASSED" "Green"
        }
        else {
            Write-ColorOutput "  - Tests: FAILED" "Red"
            $allPassed = $false
        }
    }
    catch {
        Pop-Location -ErrorAction SilentlyContinue
        Write-ColorOutput "  - Tests: ERROR - $($_.Exception.Message)" "Red"
        $allPassed = $false
    }

    # SKIP análisis completo de calidad (temporal para TDD)
    Write-ColorOutput "  - Quality: SKIP (modo TDD - análisis al final)" "Yellow"
    Write-ColorOutput "    ⚠️ TEMPORAL: Usar smart_commit_clean.ps1 para commits finales" "Gray"

    # Git best practices básicas (mantener calidad)
    Write-ColorOutput "  - Verificando git practices..." "Gray"
    try {
        $hasGitignore = Test-Path "$ProjectRoot\.gitignore"
        $hasReadme = Test-Path "$ProjectRoot\README.md"
        
        if ($hasGitignore -and $hasReadme) {
            Write-ColorOutput "  - Git Practices: GOOD" "Green"
        }
        else {
            Write-ColorOutput "  - Git Practices: BASIC FILES MISSING" "Yellow"
        }
    }
    catch {
        Write-ColorOutput "  - Git Practices: ERROR - $($_.Exception.Message)" "Red"
        $allPassed = $false
    }

    return $allPassed
}

function Get-GitStatus {
    $status = @{
        StagedFiles  = @()
        TotalChanges = 0
    }

    $gitStatus = git status --porcelain
    foreach ($line in $gitStatus) {
        if ($line.Length -ge 3) {
            $statusCode = $line.Substring(0, 2)
            $fileName = $line.Substring(3)

            if ($statusCode[0] -match '[MADRCU]') {
                $status.StagedFiles += $fileName
            }
        }
    }

    $status.TotalChanges = $status.StagedFiles.Count
    return $status
}

function Show-CommitPreview {
    param([string]$Message, [array]$StagedFiles)

    Write-ColorOutput "PREVIEW DEL COMMIT TDD" "Magenta"
    Write-ColorOutput ("-" * 35) "Magenta"
    Write-ColorOutput "Mensaje: $Message" "White"
    Write-ColorOutput "Archivos ($($StagedFiles.Count)):" "White"

    foreach ($file in $StagedFiles | Select-Object -First 10) {
        Write-ColorOutput "  - $file" "Gray"
    }

    if ($StagedFiles.Count -gt 10) {
        Write-ColorOutput "  ... y $($StagedFiles.Count - 10) archivos más" "Gray"
    }
}

function Main {
    Write-ColorOutput "Smart Commit TDD - Desarrollo Rápido" "Cyan"
    Write-ColorOutput ("=" * 45) "Cyan"
    Write-ColorOutput "⚠️ MODO TEMPORAL: Calidad esencial + velocidad" "Yellow"
    Write-ColorOutput ("=" * 45) "Cyan"
    
    Set-Location $ProjectRoot
    
    $status = Get-GitStatus

    if ($status.StagedFiles.Count -eq 0) {
        Write-ColorOutput "No hay archivos en staging area. Usa 'git add' primero." "Red"
        exit 1
    }

    Show-CommitPreview -Message $Message -StagedFiles $status.StagedFiles

    # Validar mensaje (mantener calidad)
    if (-not (Test-CommitMessage -Message $Message)) {
        Write-ColorOutput "Validación de mensaje falló." "Red"
        exit 1
    }

    # Ejecutar checks TDD optimizados
    if (-not (Invoke-TDDChecks)) {
        Write-ColorOutput "Algunos checks fallaron. ¿Continuar? (y/N)" "Yellow"
        $continue = Read-Host
        if ($continue -ne 'y' -and $continue -ne 'Y') {
            Write-ColorOutput "Commit cancelado." "Red"
            exit 1
        }
    }

    # Confirmar commit
    Write-ColorOutput "¿Proceder con el commit TDD? (Y/n)" "Green"
    $confirm = Read-Host
    if ($confirm -eq 'n' -or $confirm -eq 'N') {
        Write-ColorOutput "Commit cancelado." "Yellow"
        exit 0
    }

    try {
        git commit -m "$Message"
        Write-ColorOutput "¡Commit TDD realizado exitosamente!" "Green"

        $commitHash = git rev-parse --short HEAD
        Write-ColorOutput "Hash: $commitHash" "Gray"
        
        Write-ColorOutput "" "White"
        Write-ColorOutput "📋 SIGUIENTE PASO:" "Cyan"
        Write-ColorOutput "  Cuando termines el desarrollo TDD, usa:" "White"
        Write-ColorOutput "  .\scripts\smart_commit_clean.ps1 para commits finales" "Green"
        exit 0
    }
    catch {
        Write-ColorOutput "Error realizando commit: $($_.Exception.Message)" "Red"
        exit 1
    }
}

Main 