# 🚨 ========= COPILOTO/CURSOR: CONFIGURACIÓN LINTING ========= 🚨
#
# 📋 SCRIPT DE CONFIGURACIÓN COMPLETA DE LINTING
#    ✅ Instala todas las herramientas de linting
#    ✅ Verifica configuraciones
#    ✅ Ejecuta tests de configuración
#    ✅ Configura pre-commit hooks
#
# 🔧 USO: .\configure_linting.ps1
# 📚 REFERENCIA: /RULES.md sección "🧠 REGLAS PARA COPILOTO/CURSOR"
# 
# ================================================================

param(
    [switch]$InstallRuff = $false,
    [switch]$SkipTests = $false,
    [switch]$Verbose = $false
)

Write-Host "🔧 ============= CONFIGURACIÓN DE LINTING ============= 🔧" -ForegroundColor Cyan
Write-Host "Configurando herramientas de linting para el proyecto ml-api-fastapi-v2" -ForegroundColor White
Write-Host ""

# Función para verificar si estamos en el directorio correcto
function Test-ProjectRoot {
    if (!(Test-Path "backend/app") -or !(Test-Path "pyproject.toml")) {
        Write-Host "❌ Error: Ejecutar desde la raíz del proyecto ml-api-fastapi-v2" -ForegroundColor Red
        exit 1
    }
}

# Función para verificar Python y venv
function Test-PythonEnvironment {
    Write-Host "🐍 Verificando entorno Python..." -ForegroundColor Yellow
    
    if (!(Test-Path "backend/venv")) {
        Write-Host "❌ Entorno virtual no encontrado en backend/venv" -ForegroundColor Red
        Write-Host "💡 Ejecutar primero: python -m venv backend/venv" -ForegroundColor Cyan
        exit 1
    }
    
    $pythonExe = "backend/venv/Scripts/python.exe"
    if (!(Test-Path $pythonExe)) {
        Write-Host "❌ Python no encontrado en entorno virtual" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Entorno Python verificado" -ForegroundColor Green
    return $pythonExe
}

# Función para instalar herramientas de linting
function Install-LintingTools {
    param([string]$PythonExe)
    
    Write-Host "📦 Instalando herramientas de linting..." -ForegroundColor Yellow
    
    $tools = @(
        "flake8==7.3.0",
        "black==25.1.0", 
        "isort==6.0.1",
        "mypy==1.16.1",
        "pre-commit==4.0.1"
    )
    
    if ($InstallRuff) {
        $tools += "ruff==0.8.5"
        Write-Host "⚡ Incluyendo Ruff (linter súper rápido)" -ForegroundColor Magenta
    }
    
    foreach ($tool in $tools) {
        Write-Host "📋 Instalando $tool..." -ForegroundColor White
        & $PythonExe -m pip install $tool
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Error instalando $tool" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "✅ Herramientas de linting instaladas" -ForegroundColor Green
}

# Función para verificar configuraciones
function Test-LintingConfigurations {
    Write-Host "🔍 Verificando archivos de configuración..." -ForegroundColor Yellow
    
    $configs = @{
        ".flake8" = "Configuración de Flake8"
        "pyproject.toml" = "Configuración centralizada"
        "mypy.ini" = "Configuración de MyPy"
        ".pre-commit-config.yaml" = "Pre-commit hooks"
    }
    
    if ($InstallRuff) {
        $configs["ruff.toml"] = "Configuración de Ruff"
    }
    
    foreach ($config in $configs.GetEnumerator()) {
        if (Test-Path $config.Key) {
            Write-Host "✅ $($config.Value): $($config.Key)" -ForegroundColor Green
        } else {
            Write-Host "❌ Falta: $($config.Value) ($($config.Key))" -ForegroundColor Red
        }
    }
}

# Función para ejecutar tests de linting
function Test-LintingTools {
    param([string]$PythonExe)
    
    if ($SkipTests) {
        Write-Host "⏭️  Saltando tests de herramientas" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🧪 Ejecutando tests de herramientas de linting..." -ForegroundColor Yellow
    
    # Test Flake8
    Write-Host "📋 Testing Flake8..." -ForegroundColor White
    & $PythonExe -m flake8 --version
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Flake8 funcionando" -ForegroundColor Green
    } else {
        Write-Host "❌ Flake8 con problemas" -ForegroundColor Red
    }
    
    # Test Black
    Write-Host "🎨 Testing Black..." -ForegroundColor White
    & $PythonExe -m black --version
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Black funcionando" -ForegroundColor Green
    } else {
        Write-Host "❌ Black con problemas" -ForegroundColor Red
    }
    
    # Test isort
    Write-Host "📋 Testing isort..." -ForegroundColor White
    & $PythonExe -m isort --version
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ isort funcionando" -ForegroundColor Green
    } else {
        Write-Host "❌ isort con problemas" -ForegroundColor Red
    }
    
    # Test MyPy
    Write-Host "🔍 Testing MyPy..." -ForegroundColor White
    & $PythonExe -m mypy --version
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MyPy funcionando" -ForegroundColor Green
    } else {
        Write-Host "❌ MyPy con problemas" -ForegroundColor Red
    }
    
    # Test Ruff (si está instalado)
    if ($InstallRuff) {
        Write-Host "⚡ Testing Ruff..." -ForegroundColor White
        & $PythonExe -m ruff --version
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Ruff funcionando" -ForegroundColor Green
        } else {
            Write-Host "❌ Ruff con problemas" -ForegroundColor Red
        }
    }
}

# Función para configurar pre-commit
function Setup-PreCommit {
    param([string]$PythonExe)
    
    Write-Host "🔗 Configurando pre-commit hooks..." -ForegroundColor Yellow
    
    if (Test-Path ".pre-commit-config.yaml") {
        & $PythonExe -m pre_commit install
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Pre-commit hooks instalados" -ForegroundColor Green
        } else {
            Write-Host "❌ Error configurando pre-commit" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Archivo .pre-commit-config.yaml no encontrado" -ForegroundColor Red
    }
}

# Función para mostrar resumen de comandos
function Show-LintingCommands {
    Write-Host ""
    Write-Host "🚀 ============= COMANDOS DE LINTING ============= 🚀" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 ANÁLISIS:" -ForegroundColor Yellow
    Write-Host "   flake8 backend/app --count --statistics" -ForegroundColor White
    Write-Host "   mypy backend/app" -ForegroundColor White
    if ($InstallRuff) {
        Write-Host "   ruff check backend/app" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "🔧 CORRECCIÓN AUTOMÁTICA:" -ForegroundColor Yellow
    Write-Host "   black backend/app" -ForegroundColor White
    Write-Host "   isort backend/app" -ForegroundColor White
    if ($InstallRuff) {
        Write-Host "   ruff check --fix backend/app" -ForegroundColor White
        Write-Host "   ruff format backend/app" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "🔗 PRE-COMMIT:" -ForegroundColor Yellow
    Write-Host "   pre-commit run --all-files" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 SMART COMMIT:" -ForegroundColor Yellow
    Write-Host "   .\\scripts\\smart_commit_clean.ps1 -Message \"tu mensaje\"" -ForegroundColor White
    Write-Host ""
}

# ============= EJECUCIÓN PRINCIPAL =============

try {
    # Verificaciones iniciales
    Test-ProjectRoot
    $pythonExe = Test-PythonEnvironment
    
    # Instalación de herramientas
    Install-LintingTools -PythonExe $pythonExe
    
    # Verificación de configuraciones
    Test-LintingConfigurations
    
    # Tests de herramientas
    Test-LintingTools -PythonExe $pythonExe
    
    # Configuración de pre-commit
    Setup-PreCommit -PythonExe $pythonExe
    
    # Mostrar comandos disponibles
    Show-LintingCommands
    
    Write-Host ""
    Write-Host "🎉 ============= CONFIGURACIÓN COMPLETADA ============= 🎉" -ForegroundColor Green
    Write-Host "Todas las herramientas de linting están configuradas y listas para usar" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "   1. Ejecutar: black backend/app (corregir formato)" -ForegroundColor White
    Write-Host "   2. Ejecutar: isort backend/app (ordenar imports)" -ForegroundColor White
    Write-Host "   3. Ejecutar: flake8 backend/app (verificar errores)" -ForegroundColor White
    Write-Host "   4. Usar smart commit para commits automáticos" -ForegroundColor White
    
} catch {
    Write-Host ""
    Write-Host "❌ Error durante la configuración: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} 