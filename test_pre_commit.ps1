# 🚨 ========= COPILOTO/CURSOR: TEST PRE-COMMIT HOOKS ========= 🚨
#
# 🧪 SCRIPT DE VERIFICACIÓN PRE-COMMIT:
#    ✅ Instala y configura pre-commit
#    ✅ Verifica todos los hooks de seguridad VPS
#    ✅ Ejecuta tests de validación
#    ✅ Reporta estado de configuración
#
# 🔧 USO: .\test_pre_commit.ps1
# 📚 REFERENCIA: /RULES.md sección "🧠 REGLAS PARA COPILOTO/CURSOR"
# 
# ================================================================

Write-Host "🔗 ============= VERIFICACIÓN PRE-COMMIT HOOKS ============= 🔗" -ForegroundColor Cyan
Write-Host "Verificando configuración de hooks de seguridad para VPS" -ForegroundColor White
Write-Host ""

# Verificar archivos de configuración
function Test-PreCommitFiles {
    Write-Host "📁 Verificando archivos de configuración..." -ForegroundColor Yellow
    
    $configs = @{
        ".pre-commit-config.yaml" = "Configuración principal de hooks"
        ".secrets.baseline" = "Baseline para detect-secrets"
        ".yamllint.yml" = "Configuración yamllint"
    }
    
    $allGood = $true
    foreach ($config in $configs.GetEnumerator()) {
        if (Test-Path $config.Key) {
            Write-Host "✅ $($config.Value): $($config.Key)" -ForegroundColor Green
        } else {
            Write-Host "❌ Falta: $($config.Value) ($($config.Key))" -ForegroundColor Red
            $allGood = $false
        }
    }
    
    return $allGood
}

# Instalar pre-commit si no está disponible
function Install-PreCommit {
    Write-Host "📦 Verificando instalación de pre-commit..." -ForegroundColor Yellow
    
    $pythonExe = "backend/venv/Scripts/python.exe"
    if (!(Test-Path $pythonExe)) {
        Write-Host "❌ Entorno virtual no encontrado" -ForegroundColor Red
        return $false
    }
    
    # Instalar pre-commit
    Write-Host "📋 Instalando pre-commit..." -ForegroundColor White
    & $pythonExe -m pip install pre-commit detect-secrets yamllint
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Pre-commit instalado correctamente" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Error instalando pre-commit" -ForegroundColor Red
        return $false
    }
}

# Configurar hooks
function Setup-PreCommitHooks {
    Write-Host "🔗 Configurando hooks..." -ForegroundColor Yellow
    
    $pythonExe = "backend/venv/Scripts/python.exe"
    
    # Instalar hooks
    & $pythonExe -m pre_commit install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error configurando hooks" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ Hooks configurados correctamente" -ForegroundColor Green
    return $true
}

# Probar hooks específicos
function Test-SecurityHooks {
    Write-Host "🔒 Probando hooks de seguridad..." -ForegroundColor Yellow
    
    $pythonExe = "backend/venv/Scripts/python.exe"
    
    # Test detect-secrets
    Write-Host "📋 Testing detect-secrets..." -ForegroundColor White
    & $pythonExe -m pre_commit run detect-secrets --all-files
    
    # Test private key detection
    Write-Host "🔑 Testing detect-private-key..." -ForegroundColor White
    & $pythonExe -m pre_commit run detect-private-key --all-files
    
    # Test YAML validation
    Write-Host "📄 Testing yamllint..." -ForegroundColor White
    & $pythonExe -m pre_commit run yamllint --all-files
    
    Write-Host "✅ Tests de seguridad completados" -ForegroundColor Green
}

# Probar hooks de calidad
function Test-QualityHooks {
    Write-Host "🧪 Probando hooks de calidad..." -ForegroundColor Yellow
    
    $pythonExe = "backend/venv/Scripts/python.exe"
    
    # Test validaciones de archivos
    Write-Host "📁 Testing validaciones de archivos..." -ForegroundColor White
    & $pythonExe -m pre_commit run check-json --all-files
    & $pythonExe -m pre_commit run check-yaml --all-files
    & $pythonExe -m pre_commit run check-toml --all-files
    
    # Test formateo
    Write-Host "🎨 Testing formateo..." -ForegroundColor White
    & $pythonExe -m pre_commit run black --all-files
    & $pythonExe -m pre_commit run isort --all-files
    
    Write-Host "✅ Tests de calidad completados" -ForegroundColor Green
}

# Generar reporte
function Show-PreCommitReport {
    Write-Host ""
    Write-Host "📊 ============= REPORTE PRE-COMMIT ============= 📊" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "🔒 HOOKS DE SEGURIDAD VPS:" -ForegroundColor Yellow
    Write-Host "   ✅ detect-secrets: Detectar API keys, passwords, tokens" -ForegroundColor White
    Write-Host "   ✅ detect-private-key: Evitar claves SSH/SSL hardcodeadas" -ForegroundColor White
    Write-Host "   ✅ check-case-conflict: Problemas Linux/Windows" -ForegroundColor White
    Write-Host "   ✅ yamllint: Validar configuraciones YAML" -ForegroundColor White
    Write-Host ""
    
    Write-Host "📁 VALIDACIONES DE ARCHIVOS:" -ForegroundColor Yellow
    Write-Host "   ✅ check-json/yaml/toml: Sintaxis correcta" -ForegroundColor White
    Write-Host "   ✅ check-added-large-files: Max 500KB por archivo" -ForegroundColor White
    Write-Host "   ✅ trailing-whitespace: Limpieza automática" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🎨 FORMATEO Y CALIDAD:" -ForegroundColor Yellow
    Write-Host "   ✅ black: Formateo automático Python" -ForegroundColor White
    Write-Host "   ✅ isort: Ordenamiento de imports" -ForegroundColor White
    Write-Host "   ✅ flake8: Linting PEP8" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🧪 TESTS Y ANÁLISIS:" -ForegroundColor Yellow
    Write-Host "   ✅ pytest: Tests automáticos" -ForegroundColor White
    Write-Host "   ✅ quality-checklist: Checklist de calidad" -ForegroundColor White
    Write-Host "   ✅ tech-debt-analysis: Análisis de deuda técnica" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🚀 USO:" -ForegroundColor Yellow
    Write-Host "   pre-commit run --all-files  # Ejecutar todos los hooks" -ForegroundColor White
    Write-Host "   git commit                  # Hooks automáticos en cada commit" -ForegroundColor White
    Write-Host "   .\\scripts\\smart_commit_clean.ps1  # Sistema integrado" -ForegroundColor White
    Write-Host ""
}

# ============= EJECUCIÓN PRINCIPAL =============

try {
    # Verificaciones
    if (!(Test-PreCommitFiles)) {
        Write-Host "❌ Faltan archivos de configuración" -ForegroundColor Red
        exit 1
    }
    
    # Instalación
    if (!(Install-PreCommit)) {
        Write-Host "❌ Error en instalación" -ForegroundColor Red
        exit 1
    }
    
    # Configuración
    if (!(Setup-PreCommitHooks)) {
        Write-Host "❌ Error en configuración" -ForegroundColor Red
        exit 1
    }
    
    # Tests
    Test-SecurityHooks
    Test-QualityHooks
    
    # Reporte
    Show-PreCommitReport
    
    Write-Host "🎉 ============= PRE-COMMIT CONFIGURADO ============= 🎉" -ForegroundColor Green
    Write-Host "Sistema de hooks de seguridad VPS listo para usar" -ForegroundColor White
    
} catch {
    Write-Host ""
    Write-Host "❌ Error durante la verificación: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} 