# 🤖 GitHub Actions - Pipelines Automatizados

## 📋 Secrets Requeridos

Para que los pipelines funcionen correctamente, debes configurar los siguientes **secrets** en tu repositorio:

### 🔐 Configuración de Secrets

Ve a: **Settings > Secrets and Variables > Actions > New repository secret**

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `VPS_SSH_KEY` | Clave SSH privada para conectar al VPS | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `VPS_USER` | Usuario SSH del VPS | `ubuntu` o `root` |
| `VPS_HOST` | IP o dominio del VPS | `192.168.1.100` o `mi-vps.com` |
| `VPS_URL` | URL completa de la aplicación | `https://mi-app.com` |

### 🔧 Generación de Clave SSH

```bash
# En tu VPS, generar par de claves
ssh-keygen -t ed25519 -C "github-actions@mi-proyecto"

# Agregar clave pública al authorized_keys
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys

# Copiar clave privada para GitHub Secret
cat ~/.ssh/id_ed25519
```

## 🚀 Pipelines Implementados

### 1️⃣ Pipeline Principal de Calidad
- **Archivo**: `quality_pipeline.yml`
- **Triggers**: PR, Push a main, Schedule diario
- **Duración**: ~30 minutos
- **Incluye**: Seguridad, tests, build, reportes

### 2️⃣ Pipeline de Seguridad Avanzada
- **Archivo**: `security_scan.yml`
- **Triggers**: Schedule diario/semanal, Push crítico
- **Duración**: ~25 minutos
- **Incluye**: Vulnerabilidades, superficie de ataque

### 3️⃣ Pipeline de Performance
- **Archivo**: `performance_test.yml`
- **Triggers**: Schedule semanal, Tags release
- **Duración**: ~20 minutos
- **Incluye**: Load testing, benchmarks, métricas

### 4️⃣ Pipeline de Deploy VPS
- **Archivo**: `deploy_vps.yml`
- **Triggers**: Push a main, Tags, Manual
- **Duración**: ~15 minutos
- **Incluye**: Validaciones, backup, deploy, rollback

## 🏗️ Configuración VPS Requerida

### Estructura de Directorios
```
/var/www/ml-api/          # Aplicación principal
/var/backups/ml-api/      # Backups automáticos
/etc/ml-api/             # Configuraciones
```

### Servicios Systemd
```bash
# Crear servicio para la aplicación
sudo systemctl enable ml-api-backend
sudo systemctl start ml-api-backend
```

### Permisos SSH
```bash
# El usuario debe tener permisos sudo
sudo usermod -aG sudo $VPS_USER

# Configurar sudoers para comandos específicos
echo "$VPS_USER ALL=(ALL) NOPASSWD: /bin/systemctl" >> /etc/sudoers.d/ml-api
```

## 📊 Monitoreo y Reportes

### Artifacts Generados
- **Quality Reports**: Métricas de calidad consolidadas
- **Security Reports**: Análisis de vulnerabilidades
- **Performance Reports**: Métricas de rendimiento
- **Deploy Reports**: Estado de deployments

### Ubicación de Reportes
- Ve a: **Actions > [Workflow Run] > Artifacts**
- Los reportes se mantienen por 30-90 días según configuración

## 🚨 Troubleshooting

### Errores Comunes

**"Context access might be invalid"**
- ✅ **Normal**: Los secrets no están configurados localmente
- 🔧 **Solución**: Configurar secrets en GitHub Settings

**"SSH Connection Failed"**
- ❌ **Problema**: Clave SSH incorrecta o permisos
- 🔧 **Solución**: Verificar VPS_SSH_KEY y permisos

**"Health Check Failed"**
- ❌ **Problema**: Aplicación no responde
- 🔧 **Solución**: Verificar servicios y VPS_URL

**"Rollback Executed"**
- ⚠️ **Información**: Deploy falló, rollback automático
- 🔧 **Acción**: Revisar logs del deploy

## 🔧 Activación de Pipelines

1. **Configurar secrets** en GitHub Settings
2. **Hacer push** a main para activar primer pipeline
3. **Monitorear** ejecución en Actions tab
4. **Revisar reportes** en artifacts de cada run

## 📚 Referencias

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions) 