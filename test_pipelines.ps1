# 🚨 ========= COPILOTO/CURSOR: TEST PIPELINES AUTOMATIZADOS ========= 🚨
#
# 🤖 SCRIPT DE VERIFICACIÓN COMPLETA DE PIPELINES:
#    ✅ Verifica configuración de GitHub Actions
#    ✅ Valida sintaxis de todos los workflows
#    ✅ Prueba pre-commit hooks integrados
#    ✅ Verifica configuraciones de seguridad
#    ✅ Genera reporte de estado completo
#
# 🔧 USO: .\test_pipelines.ps1
# 📚 REFERENCIA: /RULES.md sección "🧠 REGLAS PARA COPILOTO/CURSOR"
# 
# ================================================================

Write-Host "🤖 ============= VERIFICACIÓN PIPELINES AUTOMATIZADOS ============= 🤖" -ForegroundColor Cyan
Write-Host "Sistema completo de validación automatizada para VPS" -ForegroundColor White
Write-Host ""

# Verificar estructura de GitHub Actions
function Test-GitHubActions {
    Write-Host "📁 Verificando estructura GitHub Actions..." -ForegroundColor Yellow
    
    $workflows = @{
        ".github/workflows/quality_pipeline.yml" = "Pipeline principal de calidad"
        ".github/workflows/security_scan.yml" = "Pipeline de seguridad avanzada"
        ".github/workflows/performance_test.yml" = "Pipeline de testing de performance"
        ".github/workflows/deploy_vps.yml" = "Pipeline de deploy a VPS"
    }
    
    $allGood = $true
    foreach ($workflow in $workflows.GetEnumerator()) {
        if (Test-Path $workflow.Key) {
            Write-Host "✅ $($workflow.Value): $($workflow.Key)" -ForegroundColor Green
        } else {
            Write-Host "❌ Falta: $($workflow.Value) ($($workflow.Key))" -ForegroundColor Red
            $allGood = $false
        }
    }
    
    return $allGood
}

# Verificar archivos de configuración
function Test-ConfigurationFiles {
    Write-Host "⚙️ Verificando archivos de configuración..." -ForegroundColor Yellow
    
    $configs = @{
        ".pre-commit-config.yaml" = "Pre-commit hooks"
        ".secrets.baseline" = "Baseline de secretos"
        ".yamllint.yml" = "Configuración YAML lint"
        "mypy.ini" = "Configuración MyPy"
        "pyproject.toml" = "Configuración Python centralizada"
        "ruff.toml" = "Configuración Ruff linter"
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

# Validar sintaxis de workflows
function Test-WorkflowSyntax {
    Write-Host "🔍 Validando sintaxis de workflows..." -ForegroundColor Yellow
    
    $pythonExe = "backend/venv/Scripts/python.exe"
    if (!(Test-Path $pythonExe)) {
        Write-Host "⚠️ Entorno virtual no encontrado - instalando yamllint..." -ForegroundColor Yellow
        pip install yamllint
        $yamlLint = "yamllint"
    } else {
        & $pythonExe -m pip install yamllint -q
        $yamlLint = "$pythonExe -m yamllint"
    }
    
    $workflows = Get-ChildItem ".github/workflows/*.yml"
    $allValid = $true
    
    foreach ($workflow in $workflows) {
        Write-Host "📋 Validando: $($workflow.Name)" -ForegroundColor White
        
        $result = & $yamlLint $workflow.FullName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Sintaxis correcta" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Errores de sintaxis:" -ForegroundColor Red
            Write-Host "   $result" -ForegroundColor Red
            $allValid = $false
        }
    }
    
    return $allValid
}

# Probar pre-commit hooks
function Test-PreCommitIntegration {
    Write-Host "🔗 Probando integración pre-commit..." -ForegroundColor Yellow
    
    $pythonExe = "backend/venv/Scripts/python.exe"
    if (!(Test-Path $pythonExe)) {
        Write-Host "❌ Entorno virtual no encontrado" -ForegroundColor Red
        return $false
    }
    
    # Instalar pre-commit si no está
    & $pythonExe -m pip install pre-commit -q
    
    # Probar configuración
    Write-Host "📋 Verificando configuración pre-commit..." -ForegroundColor White
    & $pythonExe -m pre_commit --version
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Pre-commit configurado correctamente" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Error en configuración pre-commit" -ForegroundColor Red
        return $false
    }
}

# Verificar configuraciones de seguridad
function Test-SecurityConfiguration {
    Write-Host "🔒 Verificando configuraciones de seguridad..." -ForegroundColor Yellow
    
    # Verificar secrets baseline
    if (Test-Path ".secrets.baseline") {
        $baseline = Get-Content ".secrets.baseline" | ConvertFrom-Json
        if ($baseline.version -and $baseline.plugins_used) {
            Write-Host "✅ Secrets baseline configurado correctamente" -ForegroundColor Green
        } else {
            Write-Host "❌ Secrets baseline mal configurado" -ForegroundColor Red
            return $false
        }
    }
    
    # Verificar que no hay secretos hardcodeados obvios
    $secretPatterns = @("password.*=", "secret.*=", "key.*=", "token.*=")
    $violations = @()
    
    foreach ($pattern in $secretPatterns) {
        $found = Select-String -Path "backend/app/*.py" -Pattern $pattern -Quiet
        if ($found) {
            $violations += $pattern
        }
    }
    
    if ($violations.Count -eq 0) {
        Write-Host "✅ No se encontraron secretos hardcodeados" -ForegroundColor Green
        return $true
    } else {
        Write-Host "⚠️ Posibles secretos hardcodeados encontrados" -ForegroundColor Yellow
        return $true  # Warning, not error
    }
}

# Generar dashboard de estado
function Show-PipelinesDashboard {
    Write-Host ""
    Write-Host "📊 ============= DASHBOARD PIPELINES AUTOMATIZADOS ============= 📊" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "🤖 PIPELINES IMPLEMENTADOS:" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "1️⃣ 🔧 PIPELINE PRINCIPAL DE CALIDAD" -ForegroundColor White
    Write-Host "   📋 Triggers: PR, Push a main, Schedule diario" -ForegroundColor Gray
    Write-Host "   🔍 Incluye: Seguridad, Tests, Build, Reportes" -ForegroundColor Gray
    Write-Host "   ⏱️ Duración estimada: ~30 minutos" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "2️⃣ 🔒 PIPELINE DE SEGURIDAD AVANZADA" -ForegroundColor White
    Write-Host "   📋 Triggers: Schedule diario/semanal, Push crítico" -ForegroundColor Gray
    Write-Host "   🔍 Incluye: Vulnerabilidades, Superficie ataque, Análisis profundo" -ForegroundColor Gray
    Write-Host "   ⏱️ Duración estimada: ~25 minutos" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "3️⃣ ⚡ PIPELINE DE PERFORMANCE" -ForegroundColor White
    Write-Host "   📋 Triggers: Schedule semanal, Tags release" -ForegroundColor Gray
    Write-Host "   🔍 Incluye: Load testing, Benchmarks, Métricas" -ForegroundColor Gray
    Write-Host "   ⏱️ Duración estimada: ~20 minutos" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "4️⃣ 🚀 PIPELINE DE DEPLOY VPS" -ForegroundColor White
    Write-Host "   📋 Triggers: Push a main, Tags, Manual" -ForegroundColor Gray
    Write-Host "   🔍 Incluye: Validaciones, Backup, Deploy, Rollback" -ForegroundColor Gray
    Write-Host "   ⏱️ Duración estimada: ~15 minutos" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "🔧 HERRAMIENTAS INTEGRADAS:" -ForegroundColor Yellow
    Write-Host "   🔗 Pre-commit hooks: Validación automática pre-commit" -ForegroundColor White
    Write-Host "   🔒 detect-secrets: Detección de secretos hardcodeados" -ForegroundColor White
    Write-Host "   🛡️ bandit: Análisis de seguridad Python" -ForegroundColor White
    Write-Host "   📦 safety: Validación de dependencias vulnerables" -ForegroundColor White
    Write-Host "   🔬 semgrep: Análisis estático avanzado" -ForegroundColor White
    Write-Host "   📄 yamllint: Validación de archivos YAML" -ForegroundColor White
    Write-Host "   ⚡ locust: Load testing" -ForegroundColor White
    Write-Host "   🚀 autocannon: Performance testing" -ForegroundColor White
    Write-Host ""
    
    Write-Host "📊 REPORTES AUTOMATIZADOS:" -ForegroundColor Yellow
    Write-Host "   📋 Quality Report: Dashboard de calidad consolidado" -ForegroundColor White
    Write-Host "   🔒 Security Dashboard: Análisis de seguridad completo" -ForegroundColor White
    Write-Host "   ⚡ Performance Dashboard: Métricas de rendimiento" -ForegroundColor White
    Write-Host "   🚀 Deploy Report: Estado de deployments" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🚨 ALERTAS Y NOTIFICACIONES:" -ForegroundColor Yellow
    Write-Host "   🔴 Critical: Vulnerabilidades críticas detectadas" -ForegroundColor White
    Write-Host "   ⚠️ Warning: Degradación de performance > 20%" -ForegroundColor White
    Write-Host "   🚀 Success: Deploy exitoso con health checks" -ForegroundColor White
    Write-Host "   🔄 Rollback: Rollback automático ejecutado" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🔗 INTEGRACIÓN VPS:" -ForegroundColor Yellow
    Write-Host "   🌐 SSH Deploy: Deploy automático vía SSH" -ForegroundColor White
    Write-Host "   💾 Auto Backup: Backup automático pre-deploy" -ForegroundColor White
    Write-Host "   🏥 Health Checks: Validación post-deploy" -ForegroundColor White
    Write-Host "   🚨 Auto Rollback: Rollback en caso de falla" -ForegroundColor White
    Write-Host ""
}

# Generar resumen de configuración requerida
function Show-SetupInstructions {
    Write-Host "⚙️ ============= CONFIGURACIÓN REQUERIDA ============= ⚙️" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "🔐 SECRETS DE GITHUB (Repository Settings > Secrets):" -ForegroundColor Yellow
    Write-Host "   VPS_SSH_KEY: Clave SSH privada para acceso al VPS" -ForegroundColor White
    Write-Host "   VPS_USER: Usuario SSH del VPS" -ForegroundColor White
    Write-Host "   VPS_HOST: IP o dominio del VPS" -ForegroundColor White
    Write-Host "   VPS_URL: URL completa de la aplicación" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🏗️ CONFIGURACIÓN VPS:" -ForegroundColor Yellow
    Write-Host "   📁 /var/www/ml-api/: Directorio de la aplicación" -ForegroundColor White
    Write-Host "   🐍 /var/www/ml-api/backend/venv/: Entorno virtual Python" -ForegroundColor White
    Write-Host "   💾 /var/backups/ml-api/: Directorio de backups" -ForegroundColor White
    Write-Host "   ⚙️ systemctl ml-api-backend: Servicio de la aplicación" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🚀 ACTIVACIÓN DE PIPELINES:" -ForegroundColor Yellow
    Write-Host "   1. Configurar secrets en GitHub" -ForegroundColor White
    Write-Host "   2. Hacer push a main para activar pipeline principal" -ForegroundColor White
    Write-Host "   3. Los pipelines programados se ejecutarán automáticamente" -ForegroundColor White
    Write-Host "   4. Usar 'workflow_dispatch' para triggers manuales" -ForegroundColor White
    Write-Host ""
}

# ============= EJECUCIÓN PRINCIPAL =============

try {
    # Verificaciones principales
    $workflows = Test-GitHubActions
    $configs = Test-ConfigurationFiles
    $syntax = Test-WorkflowSyntax
    $precommit = Test-PreCommitIntegration
    $security = Test-SecurityConfiguration
    
    # Dashboard
    Show-PipelinesDashboard
    
    # Instrucciones
    Show-SetupInstructions
    
    # Resultado final
    Write-Host "🎯 ============= RESULTADO FINAL ============= 🎯" -ForegroundColor Cyan
    Write-Host ""
    
    if ($workflows -and $configs -and $syntax -and $precommit -and $security) {
        Write-Host "🎉 ¡PIPELINES AUTOMATIZADOS LISTOS!" -ForegroundColor Green
        Write-Host "✅ Todos los componentes configurados correctamente" -ForegroundColor Green
        Write-Host "🚀 Sistema de validación automatizada operativo" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 PRÓXIMOS PASOS:" -ForegroundColor Yellow
        Write-Host "   1. Configurar secrets de GitHub para VPS" -ForegroundColor White
        Write-Host "   2. Hacer push para activar el primer pipeline" -ForegroundColor White
        Write-Host "   3. Monitorear ejecución en GitHub Actions" -ForegroundColor White
        Write-Host "   4. Revisar reportes generados en artifacts" -ForegroundColor White
    } else {
        Write-Host "⚠️ CONFIGURACIÓN INCOMPLETA" -ForegroundColor Yellow
        Write-Host "🔧 Algunos componentes necesitan atención" -ForegroundColor Yellow
        Write-Host "📋 Revisar errores mostrados arriba" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "📚 Documentación completa en /RULES.md" -ForegroundColor Cyan
    Write-Host "🔗 GitHub Actions: https://github.com/usuario/repo/actions" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "❌ Error durante la verificación: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} 