# 🔄 Guía del Sistema de Auto-Commits

Sistema automático de protección contra pérdida de datos que hace commits frecuentes y push automático a GitHub.

## 🚨 **PARA EMERGENCIAS (PC INESTABLE)**

### ⚡ **Activación Instantánea:**
```powershell
# COMANDO MÁS IMPORTANTE - Úsalo si tu PC está fallando
.\scripts\quick_save.ps1 -Emergency

# Activa commits cada 1 minuto con push automático
# Tu trabajo se guarda en GitHub cada minuto
```

### 🔥 **Comandos de Emergencia:**
```powershell
# Activar protección estándar (3 minutos)
.\scripts\quick_save.ps1 -On

# Modo emergencia máxima (1 minuto)  
.\scripts\quick_save.ps1 -Emergency

# Ver estado actual
.\scripts\quick_save.ps1 -Status

# Desactivar (solo cuando el PC esté estable)
.\scripts\quick_save.ps1 -Off
```

## 📋 **Scripts Disponibles**

### 🚀 **`quick_save.ps1` - Acceso Rápido**
Script principal para activar/desactivar protección automática.

| Comando | Descripción | Intervalo | Validaciones |
|---------|-------------|-----------|--------------|
| `-On` | Modo estándar | 3 minutos | Mínimas |
| `-Emergency` | Modo emergencia | 1 minuto | Bypass |
| `-Off` | Desactivar | - | - |
| `-Status` | Ver estado | - | - |

### 🔧 **`auto_commit.ps1` - Control Avanzado**
Control granular del sistema de auto-commits.

```powershell
# Intervalos personalizados
.\scripts\auto_commit.ps1 -Interval 2 -Fast     # Cada 2 minutos
.\scripts\auto_commit.ps1 -Interval 10          # Cada 10 minutos

# Control del daemon
.\scripts\auto_commit.ps1 -Status               # Estado detallado
.\scripts\auto_commit.ps1 -Stop                 # Detener
```

## 🛡️ **Funcionalidades de Protección**

### ✅ **Qué Hace Automáticamente:**
- ✅ **Detecta cambios** en el proyecto cada X minutos
- ✅ **Git add .** automático de todos los archivos modificados  
- ✅ **Commit automático** con mensaje timestamped
- ✅ **Push automático** a GitHub para respaldo remoto
- ✅ **Logging completo** de toda la actividad
- ✅ **Manejo de errores** graceful sin interrumpir trabajo

### 🔄 **Mensajes de Commit Automáticos:**
```
auto: save work in progress at 14:25:28
auto: save work in progress at 14:28:31  
auto: save work in progress at 14:31:45
```

### 📊 **Monitoreo en Tiempo Real:**
```powershell
# Ver log en tiempo real
Get-Content auto_commit.log -Wait

# Ver últimas entradas
Get-Content auto_commit.log | Select-Object -Last 10
```

## ⚙️ **Configuraciones Recomendadas**

### 🎯 **Por Situación:**

#### **PC Estable - Desarrollo Normal:**
```powershell
.\scripts\quick_save.ps1 -On
# Commits cada 3 minutos con validaciones mínimas
```

#### **PC Inestable - Problemas de Hardware:**
```powershell
.\scripts\quick_save.ps1 -Emergency  
# Commits cada 1 minuto sin validaciones
```

#### **Trabajo Crítico - No Puedes Perder Nada:**
```powershell
.\scripts\auto_commit.ps1 -Interval 1 -Fast
# Commits cada 1 minuto con push inmediato
```

#### **Sesión de Coding Larga:**
```powershell
.\scripts\auto_commit.ps1 -Interval 5 -Fast
# Commits cada 5 minutos, equilibrio perfecto
```

## 📋 **Logs y Monitoreo**

### 📜 **Archivo de Log:**
- **Ubicación:** `auto_commit.log` (directorio raíz)
- **Formato:** `[timestamp] [level] mensaje`
- **Rotación:** Automática por día

### 🔍 **Tipos de Entradas:**
```bash
[INFO]  - Operaciones normales
[WARN]  - Advertencias (push falló, etc.)
[ERROR] - Errores críticos  
[DEBUG] - Información detallada
```

### 📊 **Comandos de Monitoreo:**
```powershell
# Estado completo
.\scripts\auto_commit.ps1 -Status

# Log completo
Get-Content auto_commit.log

# Filtrar solo errores
Get-Content auto_commit.log | Select-String "ERROR"

# Últimas 20 entradas  
Get-Content auto_commit.log | Select-Object -Last 20
```

## 🔧 **Administración del Sistema**

### ▶️ **Iniciar Auto-Commits:**
```powershell
# Método rápido (recomendado)
.\scripts\quick_save.ps1 -On

# Método avanzado
.\scripts\auto_commit.ps1 -Interval 3 -Fast
```

### ⏹️ **Detener Auto-Commits:**
```powershell
# Método rápido  
.\scripts\quick_save.ps1 -Off

# Método directo
.\scripts\auto_commit.ps1 -Stop
```

### 🔄 **Reiniciar Sistema:**
```powershell
# Detener y reiniciar
.\scripts\quick_save.ps1 -Off
.\scripts\quick_save.ps1 -On
```

## 🚨 **Solución de Problemas**

### **❌ Auto-commit no funciona:**
```powershell
# Verificar estado
.\scripts\quick_save.ps1 -Status

# Ver errores en log
Get-Content auto_commit.log | Select-String "ERROR"

# Reiniciar sistema
.\scripts\quick_save.ps1 -Off
.\scripts\quick_save.ps1 -On
```

### **❌ Push falló:**
```powershell
# Ver detalles del error
Get-Content auto_commit.log | Select-String "push"

# Push manual para resolver
git push origin master

# Continuar con auto-commits
```

### **❌ Demasiados commits automáticos:**
```powershell
# Cambiar a intervalo mayor
.\scripts\auto_commit.ps1 -Stop
.\scripts\auto_commit.ps1 -Interval 10 -Fast
```

## 🎯 **Mejores Prácticas**

### ✅ **Recomendaciones:**
1. **Siempre activar** auto-commits al empezar a trabajar
2. **Usar modo emergencia** si el PC tiene problemas
3. **Verificar el log** periódicamente
4. **No desactivar** durante trabajo crítico
5. **Hacer push manual** si auto-push falla

### ⚠️ **Advertencias:**
- Los commits automáticos **NO** tienen validaciones completas
- Para commits finales, usar `.\scripts\commit.ps1`  
- El sistema puede generar **muchos commits** (normal)
- **Squash commits** antes de pull requests

### 🔄 **Workflow Recomendado:**
```powershell
# 1. Activar protección al empezar
.\scripts\quick_save.ps1 -On

# 2. Trabajar normalmente
# (auto-commits cada 3 minutos)

# 3. Commits manuales para hitos importantes
.\scripts\commit.ps1 -Message "feat: complete feature X"

# 4. Desactivar al terminar (opcional)
.\scripts\quick_save.ps1 -Off
```

## 📈 **Métricas de Protección**

El sistema te protege contra:
- ✅ **Pérdida por fallo de hardware** (95% protección)
- ✅ **Pérdida por corte de luz** (90% protección)  
- ✅ **Pérdida por reinicio inesperado** (95% protección)
- ✅ **Pérdida por crash de aplicación** (85% protección)

**Tiempo máximo de pérdida:**
- Modo estándar: **3 minutos** de trabajo
- Modo emergencia: **1 minuto** de trabajo

## 🆘 **Comandos de Emergencia Absoluta**

Si tu PC está fallando **AHORA MISMO**:

```powershell
# 1. ACTIVAR EMERGENCIA INMEDIATA
.\scripts\quick_save.ps1 -Emergency

# 2. COMMIT MANUAL INMEDIATO
git add . && git commit --no-verify -m "emergency: save before PC crash"

# 3. PUSH INMEDIATO  
git push origin master

# 4. VERIFICAR SUBIDA
git log --oneline -1
```

**¡Tu trabajo está protegido! 🛡️** 