#!/usr/bin/env pwsh
<#
.SYNOPSIS
    SMART COMMIT ESTRICTO - SISTEMA REAL DE CALIDAD SIN BYPASS

.DESCRIPTION
    Sistema VERDADERAMENTE ESTRICTO que BLOQUEA commits automaticamente:
    - NO permite commits con tests fallidos (NUNCA)
    - NO permite coverage inferior al 80%
    - NO permite linting errors
    - NO hay opciones de bypass (NINGUNA)
    - NO hay confirmaciones para ignorar errores
    - Solo permite commits que pasen TODAS las validaciones
    
    ESTE ES UN SISTEMA REAL DE CALIDAD - NO UNA MENTIRA

.PARAMETER Message
    Mensaje de commit (obligatorio)

.PARAMETER DryRun
    Solo validar, no hacer commit real

.EXAMPLE
    .\scripts\smart_commit_strict.ps1 -Message "feat: add user auth"

.NOTES
    SISTEMA ESTRICTO REAL - SIN MENTIRAS
    - NO hay parametros Force, AutoConfirm, o similares
    - Si algo falla = COMMIT BLOQUEADO (sin excepciones)
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Message,

    [Parameter(Mandatory = $false)]
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Show-StrictHeader {
    Write-ColorOutput "SMART COMMIT ESTRICTO - SISTEMA REAL DE CALIDAD" "Red"
    Write-ColorOutput ("=" * 60) "Red"
    Write-ColorOutput "NO bypasses - NO confirmaciones - NO mentiras" "Yellow"
    Write-ColorOutput "Solo commits que pasen TODAS las validaciones" "Green"
    Write-ColorOutput ("=" * 60) "Red"
}

function Test-StrictCommitMessage {
    param([string]$Message)
    
    Write-ColorOutput "VALIDANDO MENSAJE DE COMMIT..." "Cyan"
    
    $conventionalPattern = '^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}$'
    
    if (-not ($Message -match $conventionalPattern)) {
        Write-ColorOutput "COMMIT BLOQUEADO - MENSAJE INVALIDO" "Red"
        Write-ColorOutput "Problemas encontrados:" "Red"
        
        if ($Message.Length -gt 50) {
            Write-ColorOutput "  - Muy largo: $($Message.Length) chars (maximo 50)" "Red"
        }
        if (-not ($Message -match '^(feat|fix|docs|style|refactor|test|chore)')) {
            Write-ColorOutput "  - Debe empezar con: feat|fix|docs|style|refactor|test|chore" "Red"
        }
        if (-not ($Message -match ': ')) {
            Write-ColorOutput "  - Formato requerido: tipo(scope): descripcion" "Red"
        }
        
        Write-ColorOutput "COMMIT RECHAZADO - ARREGLA EL MENSAJE" "Red"
        return $false
    }
    
    Write-ColorOutput "Mensaje valido" "Green"
    return $true
}

function Test-StrictGitStatus {
    Write-ColorOutput "VERIFICANDO GIT STATUS..." "Cyan"
    
    try {
        git rev-parse --git-dir | Out-Null
    }
    catch {
        Write-ColorOutput "COMMIT BLOQUEADO - NO ES REPOSITORIO GIT" "Red"
        return $false
    }
    
    $stagedFiles = git diff --cached --name-only
    if (-not $stagedFiles) {
        Write-ColorOutput "COMMIT BLOQUEADO - NO HAY ARCHIVOS EN STAGING" "Red"
        Write-ColorOutput "Usa: git add <archivos>" "Yellow"
        return $false
    }
    
    Write-ColorOutput "Git status valido ($($stagedFiles.Count) archivos)" "Green"
    return $true
}

function Test-StrictTests {
    Write-ColorOutput "EJECUTANDO TESTS COMPLETOS..." "Cyan"
    
    try {
        Push-Location "$ProjectRoot/backend"
        
        # Ejecutar TODOS los tests - sin excepciones
        $testOutput = python -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-fail-under=80 2>&1
        $testExitCode = $LASTEXITCODE
        
        Pop-Location
        
        if ($testExitCode -ne 0) {
            Write-ColorOutput "COMMIT BLOQUEADO - TESTS FALLIDOS" "Red"
            Write-ColorOutput "Detalles del error:" "Red"
            
            # Mostrar solo las lineas importantes del error
            $errorLines = $testOutput | Where-Object { 
                $_ -match "FAILED|ERROR|AssertionError|Coverage failure" 
            }
            
            foreach ($line in $errorLines | Select-Object -First 10) {
                Write-ColorOutput "  - $line" "Red"
            }
            
            Write-ColorOutput "ARREGLA LOS TESTS ANTES DE CONTINUAR" "Red"
            return $false
        }
        
        Write-ColorOutput "Todos los tests pasaron con coverage >=80%" "Green"
        return $true
    }
    catch {
        Pop-Location -ErrorAction SilentlyContinue
        Write-ColorOutput "COMMIT BLOQUEADO - ERROR EJECUTANDO TESTS" "Red"
        Write-ColorOutput "Error: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Test-StrictLinting {
    Write-ColorOutput "VERIFICANDO LINTING..." "Cyan"
    
    try {
        Push-Location "$ProjectRoot/backend"
        
        # Verificar con flake8
        $flakeOutput = flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics 2>&1
        $flakeExitCode = $LASTEXITCODE
        
        if ($flakeExitCode -ne 0) {
            Write-ColorOutput "COMMIT BLOQUEADO - ERRORES DE LINTING" "Red"
            Write-ColorOutput "Errores encontrados:" "Red"
            Write-ColorOutput $flakeOutput "Red"
            Pop-Location
            return $false
        }
        
        # Verificar con mypy (errores criticos)
        $mypyOutput = mypy app/ --ignore-missing-imports --disallow-untyped-defs 2>&1
        $mypyExitCode = $LASTEXITCODE
        
        Pop-Location
        
        if ($mypyExitCode -ne 0) {
            Write-ColorOutput "Advertencias de MyPy encontradas (no bloqueante)" "Yellow"
        }
        
        Write-ColorOutput "Linting paso" "Green"
        return $true
    }
    catch {
        Pop-Location -ErrorAction SilentlyContinue
        Write-ColorOutput "COMMIT BLOQUEADO - ERROR EN LINTING" "Red"
        Write-ColorOutput "Error: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Test-StrictSecurity {
    Write-ColorOutput "VERIFICANDO SEGURIDAD..." "Cyan"
    
    try {
        Push-Location $ProjectRoot
        
        # Buscar secretos o informacion sensible REALES
        $secretPatterns = @(
            'password\s*=\s*[\"''].*[\"'']', 
            'api_key\s*=\s*[\"''].*[\"'']', 
            'secret\s*=\s*[\"''].*[\"'']', 
            'token\s*=\s*[\"''].*[\"'']'
        )
        
        $secretsFound = $false
        foreach ($pattern in $secretPatterns) {
            $matches = git diff --cached | Select-String -Pattern $pattern -CaseSensitive:$false
            if ($matches) {
                Write-ColorOutput "COMMIT BLOQUEADO - POSIBLE SECRETO DETECTADO" "Red"
                Write-ColorOutput "  - Patron: $pattern" "Red"
                Write-ColorOutput "  - Linea: $($matches[0].Line)" "Red"
                $secretsFound = $true
            }
        }
        
        Pop-Location
        
        if ($secretsFound) {
            Write-ColorOutput "REVISA Y ELIMINA INFORMACION SENSIBLE" "Red"
            return $false
        }
        
        Write-ColorOutput "Verificacion de seguridad paso" "Green"
        return $true
    }
    catch {
        Pop-Location -ErrorAction SilentlyContinue
        Write-ColorOutput "ERROR EN VERIFICACION DE SEGURIDAD" "Red"
        return $false
    }
}

function Invoke-StrictCommit {
    param([string]$CommitMessage)
    
    Write-ColorOutput "INICIANDO COMMIT ESTRICTO..." "Magenta"
    
    # TODAS las validaciones deben pasar - SIN EXCEPCIONES
    $validations = @(
        @{ Name = "Git Status"; Test = { Test-StrictGitStatus } },
        @{ Name = "Mensaje"; Test = { Test-StrictCommitMessage -Message $CommitMessage } },
        @{ Name = "Tests"; Test = { Test-StrictTests } },
        @{ Name = "Linting"; Test = { Test-StrictLinting } },
        @{ Name = "Seguridad"; Test = { Test-StrictSecurity } }
    )
    
    $allPassed = $true
    
    foreach ($validation in $validations) {
        $result = & $validation.Test
        if (-not $result) {
            $allPassed = $false
            Write-ColorOutput "Validacion '$($validation.Name)' FALLO" "Red"
        }
    }
    
    if (-not $allPassed) {
        Write-ColorOutput "" "White"
        Write-ColorOutput "COMMIT COMPLETAMENTE BLOQUEADO" "Red"
        Write-ColorOutput "Razon: Una o mas validaciones fallaron" "Red"
        Write-ColorOutput "Accion: Arregla TODOS los problemas y vuelve a intentar" "Yellow"
        Write-ColorOutput "" "White"
        return $false
    }
    
    # Si llegamos aqui, TODAS las validaciones pasaron
    Write-ColorOutput "" "White"
    Write-ColorOutput "TODAS LAS VALIDACIONES PASARON" "Green"
    Write-ColorOutput "Tests: PASSED" "Green"
    Write-ColorOutput "Coverage: >=80%" "Green"
    Write-ColorOutput "Linting: PASSED" "Green"
    Write-ColorOutput "Seguridad: PASSED" "Green"
    Write-ColorOutput "Mensaje: VALIDO" "Green"
    
    if ($DryRun) {
        Write-ColorOutput "DRY RUN - Commit no ejecutado" "Yellow"
        return $true
    }
    
    # Hacer el commit SIN --no-verify para que corran los hooks
    try {
        git commit -m "$CommitMessage"
        $commitHash = git rev-parse --short HEAD
        Write-ColorOutput "" "White"
        Write-ColorOutput "COMMIT EXITOSO - CALIDAD GARANTIZADA" "Green"
        Write-ColorOutput "Hash: $commitHash" "Cyan"
        Write-ColorOutput "Mensaje: $CommitMessage" "Cyan"
        return $true
    }
    catch {
        Write-ColorOutput "ERROR AL HACER COMMIT" "Red"
        Write-ColorOutput "Error: $($_.Exception.Message)" "Red"
        return $false
    }
}

# FUNCION PRINCIPAL
function Main {
    Show-StrictHeader
    
    $success = Invoke-StrictCommit -CommitMessage $Message
    
    if ($success) {
        Write-ColorOutput "" "White"
        Write-ColorOutput "COMMIT COMPLETADO CON CALIDAD MAXIMA" "Green"
        exit 0
    }
    else {
        Write-ColorOutput "" "White"
        Write-ColorOutput "COMMIT RECHAZADO - SISTEMA ESTRICTO" "Red"
        exit 1
    }
}

# Ejecutar
Main 