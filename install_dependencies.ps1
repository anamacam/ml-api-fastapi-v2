#!/usr/bin/env pwsh
<#
.SYNOPSIS
    🐍 Instalador de Python y Dependencias - ML API FastAPI v2

.DESCRIPTION
    Script completo para instalar Python y configurar el entorno de desarrollo:
    1. Verificar/Instalar Python
    2. Crear entorno virtual
    3. Instalar dependencias
    4. Configurar pre-commit hooks

.EXAMPLE
    .\install_dependencies.ps1
#>

Write-Host "🐍 ML API FastAPI v2 - Instalador de Dependencias" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Green

# Función para verificar si Python está instalado
function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # Intentar con py launcher
        try {
            $pythonVersion = py --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Python encontrado (py launcher): $pythonVersion" -ForegroundColor Green
                return $true
            }
        }
        catch {
            return $false
        }
    }
    return $false
}

# Función para instalar Python usando winget
function Install-PythonWithWinget {
    Write-Host "`n📦 Instalando Python usando winget..." -ForegroundColor Yellow
    try {
        winget install Python.Python.3.12
        Write-Host "✅ Python instalado exitosamente" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Error instalando Python con winget: $_" -ForegroundColor Red
        return $false
    }
}

# Función para descargar Python manualmente
function Install-PythonManual {
    Write-Host "`n📥 Descargando Python manualmente..." -ForegroundColor Yellow
    $pythonUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
    $installerPath = "$env:TEMP\python-3.12.0-amd64.exe"
    
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
        Write-Host "✅ Python descargado" -ForegroundColor Green
        
        Write-Host "🔧 Instalando Python (se abrirá el instalador)..." -ForegroundColor Yellow
        Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
        Write-Host "✅ Python instalado" -ForegroundColor Green
        
        # Limpiar archivo temporal
        Remove-Item $installerPath -Force
        return $true
    }
    catch {
        Write-Host "❌ Error descargando/instalando Python: $_" -ForegroundColor Red
        return $false
    }
}

# Verificar si estamos en el directorio correcto
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Ejecuta este script desde el directorio raíz del proyecto" -ForegroundColor Red
    exit 1
}

# Paso 1: Verificar/Instalar Python
Write-Host "`n🔍 Verificando Python..." -ForegroundColor Cyan
if (-not (Test-PythonInstalled)) {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    Write-Host "`n📋 Opciones de instalación:" -ForegroundColor Yellow
    Write-Host "1. Instalar con winget (recomendado)" -ForegroundColor White
    Write-Host "2. Descargar manualmente" -ForegroundColor White
    Write-Host "3. Instalar desde python.org" -ForegroundColor White
    
    $choice = Read-Host "`nSelecciona una opción (1-3)"
    
    switch ($choice) {
        "1" {
            if (-not (Install-PythonWithWinget)) {
                Write-Host "⚠️ Falló winget, intentando descarga manual..." -ForegroundColor Yellow
                Install-PythonManual
            }
        }
        "2" { Install-PythonManual }
        "3" {
            Write-Host "`n🌐 Abriendo python.org..." -ForegroundColor Yellow
            Start-Process "https://www.python.org/downloads/"
            Write-Host "📋 Instala Python 3.12+ y asegúrate de marcar 'Add to PATH'" -ForegroundColor Cyan
            Read-Host "Presiona Enter cuando hayas instalado Python"
        }
        default {
            Write-Host "❌ Opción inválida" -ForegroundColor Red
            exit 1
        }
    }
    
    # Verificar nuevamente después de la instalación
    if (-not (Test-PythonInstalled)) {
        Write-Host "❌ Python aún no está disponible. Reinicia PowerShell y ejecuta nuevamente." -ForegroundColor Red
        exit 1
    }
}

# Paso 2: Crear entorno virtual
Write-Host "`n🔧 Configurando entorno virtual..." -ForegroundColor Cyan
Set-Location "backend"

if (Test-Path "venv") {
    Write-Host "⚠️ Entorno virtual ya existe. ¿Recrearlo? (y/N)" -ForegroundColor Yellow
    $recreate = Read-Host
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Remove-Item "venv" -Recurse -Force
        Write-Host "🗑️ Entorno virtual eliminado" -ForegroundColor Gray
    } else {
        Write-Host "✅ Usando entorno virtual existente" -ForegroundColor Green
    }
}

if (-not (Test-Path "venv")) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Yellow
    try {
        python -m venv venv
        Write-Host "✅ Entorno virtual creado" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Error creando entorno virtual: $_" -ForegroundColor Red
        Set-Location ".."
        exit 1
    }
}

# Paso 3: Activar entorno virtual
Write-Host "🔄 Activando entorno virtual..." -ForegroundColor Yellow
try {
    .\venv\Scripts\Activate.ps1
    Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error activando entorno virtual: $_" -ForegroundColor Red
    Write-Host "💡 Intenta ejecutar: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    Set-Location ".."
    exit 1
}

# Paso 4: Actualizar pip
Write-Host "`n📦 Actualizando pip..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip
    Write-Host "✅ pip actualizado" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Error actualizando pip: $_" -ForegroundColor Yellow
}

# Paso 5: Instalar dependencias
Write-Host "`n📚 Instalando dependencias..." -ForegroundColor Yellow
try {
    pip install -r requirements/dev.txt
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error instalando dependencias: $_" -ForegroundColor Red
    Write-Host "💡 Intenta instalar manualmente: pip install -r requirements/dev.txt" -ForegroundColor Cyan
}

# Paso 6: Configurar pre-commit hooks
Write-Host "`n🔧 Configurando pre-commit hooks..." -ForegroundColor Yellow
try {
    pre-commit install
    Write-Host "✅ Pre-commit hooks instalados" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Error instalando pre-commit hooks: $_" -ForegroundColor Yellow
}

# Volver al directorio raíz
Set-Location ".."

# Paso 7: Verificar instalación
Write-Host "`n🔍 Verificando instalación..." -ForegroundColor Cyan
try {
    $testResult = python -c "import fastapi, pytest, sqlalchemy; print('✅ Todas las dependencias instaladas correctamente')"
    Write-Host $testResult -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Algunas dependencias pueden no estar instaladas correctamente" -ForegroundColor Yellow
}

Write-Host "`n🎉 ¡Instalación completada!" -ForegroundColor Green
Write-Host "`n📋 COMANDOS DISPONIBLES:" -ForegroundColor Cyan
Write-Host "🚀 cd backend && .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "🧪 python -m pytest tests/ -v" -ForegroundColor White
Write-Host "⚡ python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "🔍 python -m flake8 app/" -ForegroundColor White
Write-Host "🎨 python -m black app/" -ForegroundColor White

Write-Host "`n🔄 PARA ACTIVAR EL ENTORNO VIRTUAL:" -ForegroundColor Cyan
Write-Host "cd backend" -ForegroundColor Gray
Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor Gray

Write-Host "`n✅ El proyecto está listo para desarrollo!" -ForegroundColor Green 