# 🔧 Deuda Técnica - ML API FastAPI v2

Este documento rastrea la deuda técnica del proyecto, priorizando tareas de mejora, refactoring y completitud.

## 📊 Resumen Ejecutivo

| Categoría            | Items | Prioridad Alta | Prioridad Media | Prioridad Baja |
| -------------------- | ----- | -------------- | --------------- | -------------- |
| **🚨 Crítico**       | 8     | 5              | 2               | 1              |
| **⚙️ Backend**       | 12    | 4              | 6               | 2              |
| **🎨 Frontend**      | 15    | 3              | 8               | 4              |
| **🔒 Seguridad**     | 6     | 4              | 2               | 0              |
| **📊 Monitoreo**     | 9     | 2              | 5               | 2              |
| **🧪 Testing**       | 11    | 6              | 4               | 1              |
| **📚 Documentación** | 7     | 2              | 3               | 2              |
| **🚀 DevOps**        | 10    | 3              | 4               | 3              |

**Total: 78 items** | **29 Alta** | **34 Media** | **15 Baja**

---

## 🚨 CRÍTICO - Resolver Inmediatamente

### 🔴 Prioridad ALTA

#### TD-001: Servicios Faltantes Críticos

- **Descripción**: Servicios referenciados pero no implementados
- **Impacto**: Aplicación no funcional
- **Esfuerzo**: 3-5 días
- **Archivos**:
  - `backend/app/services/prediction.py`
  - `backend/app/services/cache.py`
  - `backend/app/services/monitoring.py`
  - `backend/app/services/model_manager.py`
- **Bloqueante**: SÍ

#### TD-002: Endpoints Faltantes

- **Descripción**: Endpoints referenciados en API router sin implementar
- **Impacto**: API incompleta
- **Esfuerzo**: 2-3 días
- **Archivos**:
  - `backend/app/api/v1/endpoints/models.py`
  - `backend/app/api/v1/endpoints/upload.py`
  - `backend/app/api/v1/endpoints/websocket.py`
- **Bloqueante**: SÍ

#### TD-003: Base de Datos sin Migrar

- **Descripción**: Tablas no creadas, sin migraciones Alembic
- **Impacto**: Aplicación no inicia
- **Esfuerzo**: 1 día
- **Archivos**: `backend/alembic/` (crear migraciones)
- **Bloqueante**: SÍ

#### TD-004: Frontend Sin Implementar

- **Descripción**: Componentes React referenciados pero no existen
- **Impacto**: UI no funcional
- **Esfuerzo**: 1-2 semanas
- **Archivos**: Todo `frontend/web-app/src/`
- **Bloqueante**: SÍ

#### TD-005: Dockerfiles Faltantes

- **Descripción**: Docker compose referencia Dockerfiles inexistentes
- **Impacto**: No se puede ejecutar con Docker
- **Esfuerzo**: 1 día
- **Archivos**:
  - `infrastructure/docker/Dockerfile.backend`
  - `infrastructure/docker/Dockerfile.frontend`
  - `infrastructure/docker/Dockerfile.websocket`
- **Bloqueante**: SÍ

### 🟡 Prioridad MEDIA

#### TD-006: Configuración Nginx Faltante

- **Descripción**: Nginx config referenciado pero no existe
- **Impacto**: Proxy reverso no funciona
- **Esfuerzo**: 2-3 horas
- **Archivos**: `infrastructure/nginx/nginx.conf`
- **Bloqueante**: NO

#### TD-007: Configuraciones de Monitoreo

- **Descripción**: Prometheus y Grafana configs faltantes
- **Impacto**: Sin monitoreo
- **Esfuerzo**: 4-6 horas
- **Archivos**: `infrastructure/monitoring/`
- **Bloqueante**: NO

### 🟢 Prioridad BAJA

#### TD-008: Scripts de Inicialización DB

- **Descripción**: Script SQL de inicialización referenciado
- **Impacto**: Configuración manual requerida
- **Esfuerzo**: 1 hora
- **Archivos**: `infrastructure/scripts/init-db.sql`
- **Bloqueante**: NO

---

## ⚙️ BACKEND

### 🔴 Prioridad ALTA

#### TD-009: Validación de Input Insuficiente

- **Descripción**: Falta validación robusta en endpoints
- **Impacto**: Vulnerabilidades de seguridad
- **Esfuerzo**: 2-3 días
- **Archivos**: Todos los endpoints
- **Riesgo**: Alto

#### TD-010: Manejo de Errores Inconsistente

- **Descripción**: No hay manejo centralizado de errores
- **Impacto**: UX pobre, debugging difícil
- **Esfuerzo**: 1-2 días
- **Archivos**: `backend/app/api/exceptions.py` (crear)

#### TD-011: Logging Estructurado Incompleto

- **Descripción**: Logs no estructurados, sin correlación IDs
- **Impacto**: Debugging complejo en producción
- **Esfuerzo**: 1 día
- **Archivos**: `backend/app/core/logging.py`

#### TD-012: Rate Limiting Faltante

- **Descripción**: Sin protección contra abuso de API
- **Impacto**: Vulnerabilidad DoS
- **Esfuerzo**: 1 día
- **Archivos**: `backend/app/api/middleware.py`

### 🟡 Prioridad MEDIA

#### TD-013: Cache Strategy Inmadura

- **Descripción**: Cache básico, sin invalidación inteligente
- **Impacto**: Performance subóptima
- **Esfuerzo**: 2-3 días
- **Archivos**: `backend/app/services/cache.py`

#### TD-014: Background Tasks Sin Monitoreo

- **Descripción**: Tareas async sin seguimiento de estado
- **Impacto**: Tareas fallidas pasan desapercibidas
- **Esfuerzo**: 1-2 días
- **Archivos**: `backend/app/services/tasks.py` (crear)

#### TD-015: Configuración de CORS Laxa

- **Descripción**: CORS permite todos los orígenes en config actual
- **Impacal:** Riesgo de seguridad
- **Esfuerzo**: 1 hora
- **Archivos**: `backend/app/core/config.py`

#### TD-016: Paginación Inconsistente

- **Descripción**: No todos los endpoints list tienen paginación
- **Impacto**: Performance issues con datasets grandes
- **Esfuerzo**: 1 día
- **Archivos**: Endpoints de listado

#### TD-017: Métricas de Negocio Faltantes

- **Descripción**: Solo métricas técnicas, sin métricas de ML
- **Impacto**: Insight limitado del modelo performance
- **Esfuerzo**: 2 días
- **Archivos**: `backend/app/services/monitoring.py`

#### TD-018: Retry Logic Faltante

- **Descripción**: Sin reintentos para operaciones que pueden fallar
- **Impacto**: Fallas transitorias no manejadas
- **Esfuerzo**: 1 día
- **Archivos**: Servicios externos

### 🟢 Prioridad BAJA

#### TD-019: Optimización de Queries DB

- **Descripción**: Queries N+1, sin índices optimizados
- **Impacto**: Performance DB
- **Esfuerzo**: 1-2 días
- **Archivos**: `backend/app/models/database.py`

#### TD-020: Health Checks Más Granulares

- **Descripción**: Health checks básicos, pocos detalles
- **Impacto**: Debugging limitado
- **Esfuerzo**: 4 horas
- **Archivos**: `backend/app/api/v1/endpoints/health.py`

---

## 🎨 FRONTEND

### 🔴 Prioridad ALTA

#### TD-021: Componentes Base Faltantes

- **Descripción**: Componentes UI fundamentales sin implementar
- **Impacto**: Desarrollo bloqueado
- **Esfuerzo**: 1 semana
- **Archivos**: `frontend/web-app/src/components/`
- **Bloqueante**: SÍ

#### TD-022: Estado Global Sin Implementar

- **Descripción**: Zustand store configurado pero vacío
- **Impacto**: No se puede manejar estado de app
- **Esfuerzo**: 2-3 días
- **Archivos**: `frontend/web-app/src/store/` (crear)

#### TD-023: Routing Sin Configurar

- **Descripción**: React Router sin rutas definidas
- **Impacto**: Navegación no funcional
- **Esfuerzo**: 1 día
- **Archivos**: `frontend/web-app/src/App.tsx`

### 🟡 Prioridad MEDIA

#### TD-024: Error Boundaries Faltantes

- **Descripción**: Sin manejo de errores React
- **Impacto**: Crashes de UI sin recovery
- **Esfuerzo**: 4 horas
- **Archivos**: `frontend/web-app/src/components/ErrorBoundary.tsx`

#### TD-025: Loading States Inconsistentes

- **Descripción**: UX pobre durante loading
- **Impacto**: Percepción de lentitud
- **Esfuerzo**: 1 día
- **Archivos**: Todos los componentes

#### TD-026: Responsive Design Faltante

- **Descripción**: Solo desktop, sin mobile
- **Impacto**: UX móvil pobre
- **Esfuerzo**: 3-4 días
- **Archivos**: CSS/Tailwind configs

#### TD-027: Accessibility (A11y) Ignorada

- **Descripción**: Sin consideraciones de accesibilidad
- **Impacto**: Exclusión de usuarios
- **Esfuerzo**: 2-3 días
- **Archivos**: Todos los componentes

#### TD-028: WebSocket Client Faltante

- **Descripción**: Cliente WebSocket referenciado pero no implementado
- **Impacto**: Sin updates en tiempo real
- **Esfuerzo**: 1-2 días
- **Archivos**: `frontend/web-app/src/services/websocket.ts`

#### TD-029: Form Validation Débil

- **Descripción**: Validación básica, sin UX de errores
- **Impacto**: Frustración del usuario
- **Esfuerzo**: 1-2 días
- **Archivos**: Componentes de formularios

#### TD-030: Performance Sin Optimizar

- **Descripción**: Sin code splitting, lazy loading
- **Impacto**: Bundle size grande
- **Esfuerzo**: 1 día
- **Archivos**: Vite config, componentes

#### TD-031: Admin Panel Básico

- **Descripción**: Admin panel sin funcionalidad
- **Impacto**: No hay gestión administrativa
- **Esfuerzo**: 1-2 semanas
- **Archivos**: `frontend/admin-panel/`

### 🟢 Prioridad BAJA

#### TD-032: Tema Dark Mode

- **Descripción**: Solo light theme
- **Impacto**: Preferencias de usuario
- **Esfuerzo**: 2-3 días
- **Archivos**: CSS/Tailwind

#### TD-033: Internacionalización (i18n)

- **Descripción**: Solo español/inglés hardcoded
- **Impacto**: Mercados internacionales limitados
- **Esfuerzo**: 1 semana
- **Archivos**: Todo el frontend

#### TD-034: PWA Features

- **Descripción**: Sin Progressive Web App features
- **Impacto**: UX móvil subóptima
- **Esfuerzo**: 2-3 días
- **Archivos**: Manifest, service worker

#### TD-035: Analytics Faltante

- **Descripción**: Sin tracking de uso
- **Impacto**: No insights de producto
- **Esfuerzo**: 1 día
- **Archivos**: Analytics service

---

## 🔒 SEGURIDAD

### 🔴 Prioridad ALTA

#### TD-036: Autenticación JWT Básica

- **Descripción**: JWT sin refresh tokens, sin revocación
- **Impacto**: Riesgo de seguridad alto
- **Esfuerzo**: 2-3 días
- **Archivos**: `backend/app/core/security.py`

#### TD-037: Secretos Hardcodeados

- **Descripción**: SECRET_KEY por defecto en configs
- **Impacto**: Vulnerabilidad crítica
- **Esfuerzo**: 1 hora
- **Archivos**: `backend/app/core/config.py`

#### TD-038: Input Sanitization Faltante

- **Descripción**: Sin sanitización de inputs de usuario
- **Impacto**: XSS, injection attacks
- **Esfuerzo**: 1-2 días
- **Archivos**: Todos los endpoints

#### TD-039: HTTPS No Configurado

- **Descripción**: HTTP en todos lados, sin SSL
- **Impacto**: Data en tránsito vulnerable
- **Esfuerzo**: 1 día
- **Archivos**: Nginx config, Docker configs

### 🟡 Prioridad MEDIA

#### TD-040: Audit Logging Faltante

- **Descripción**: Sin logs de acciones críticas
- **Impacto**: No trazabilidad de cambios
- **Esfuerzo**: 1-2 días
- **Archivos**: `backend/app/services/audit.py` (crear)

#### TD-041: File Upload Sin Validar

- **Descripción**: Upload sin validación de tipo/tamaño
- **Impacto**: Upload de archivos maliciosos
- **Esfuerzo**: 1 día
- **Archivos**: `backend/app/api/v1/endpoints/upload.py`

---

## 📊 MONITOREO

### 🔴 Prioridad ALTA

#### TD-042: Métricas de Aplicación Faltantes

- **Descripción**: Solo métricas de sistema, sin app metrics
- **Impacto**: Pobre observabilidad
- **Esfuerzo**: 1-2 días
- **Archivos**: `backend/app/services/monitoring.py`

#### TD-043: Alertas No Configuradas

- **Descripción**: Sin alertas automáticas
- **Impacto**: Downtime no detectado
- **Esfuerzo**: 1 día
- **Archivos**: `infrastructure/monitoring/alerts.yml`

### 🟡 Prioridad MEDIA

#### TD-044: Dashboards Básicos

- **Descripción**: Grafana sin dashboards específicos
- **Impacto**: Visibilidad limitada
- **Esfuerzo**: 2-3 días
- **Archivos**: `frontend/monitoring/grafana-dashboards/`

#### TD-045: Distributed Tracing Faltante

- **Descripción**: Sin tracing entre servicios
- **Impacto**: Debugging de microservicios complejo
- **Esfuerzo**: 2-3 días
- **Archivos**: Instrumentación OpenTelemetry

#### TD-046: Log Aggregation Básica

- **Descripción**: Logs solo en archivos locales
- **Impacto**: Análisis de logs limitado
- **Esfuerzo**: 1-2 días
- **Archivos**: ELK stack o similar

#### TD-047: SLI/SLO No Definidos

- **Descripción**: Sin Service Level Indicators/Objectives
- **Impacto**: No hay targets de performance
- **Esfuerzo**: 1 día
- **Archivos**: Documentación de SLIs

#### TD-048: Error Tracking Faltante

- **Descripción**: Sin Sentry o similar
- **Impacto**: Errores pasan desapercibidos
- **Esfuerzo**: 4 horas
- **Archivos**: Error tracking service

### 🟢 Prioridad BAJA

#### TD-049: APM Avanzado

- **Descripción**: Sin Application Performance Monitoring
- **Impacto**: Optimización limitada
- **Esfuerzo**: 1-2 días
- **Archivos**: APM integration

#### TD-050: Business Metrics Dashboard

- **Descripción**: Solo métricas técnicas en dashboards
- **Impacto**: Poco insight de negocio
- **Esfuerzo**: 2-3 días
- **Archivos**: Dashboards de negocio

---

## 🧪 TESTING

### 🔴 Prioridad ALTA

#### TD-051: Unit Tests Faltantes

- **Descripción**: 0% cobertura de tests
- **Impacto**: Calidad de código incierta
- **Esfuerzo**: 1-2 semanas
- **Archivos**: `backend/tests/` completo
- **Bloqueante**: Para CI/CD

#### TD-052: Integration Tests Faltantes

- **Descripción**: Sin tests de API endpoints
- **Impacto**: Regresiones no detectadas
- **Esfuerzo**: 1 semana
- **Archivos**: `backend/tests/integration/`

#### TD-053: Frontend Tests Faltantes

- **Descripción**: Sin tests React/Jest
- **Impacto**: UI regressions
- **Esfuerzo**: 1 semana
- **Archivos**: `frontend/web-app/src/**/*.test.tsx`

#### TD-054: Database Tests Faltantes

- **Descripción**: Sin tests de modelos/migrations
- **Impacto**: Data corruption risk
- **Esfuerzo**: 3-4 días
- **Archivos**: `backend/tests/models/`

#### TD-055: Load Testing Faltante

- **Descripción**: Performance bajo carga desconocido
- **Impacto**: Escalabilidad incierta
- **Esfuerzo**: 2-3 días
- **Archivos**: `tests/load/` (crear)

#### TD-056: Test CI/CD Pipeline Faltante

- **Descripción**: Tests no corren automáticamente
- **Impacto**: Quality gates inexistentes
- **Esfuerzo**: 1 día
- **Archivos**: `.github/workflows/` (crear)

### 🟡 Prioridad MEDIA

#### TD-057: E2E Tests Faltantes

- **Descripción**: Sin tests end-to-end
- **Impacto**: User flows no validados
- **Esfuerzo**: 1 semana
- **Archivos**: `tests/e2e/` (crear)

#### TD-058: Test Data Management

- **Descripción**: Sin fixtures/factories organizadas
- **Impacto**: Tests difíciles de mantener
- **Esfuerzo**: 2-3 días
- **Archivos**: `backend/tests/factories/`

#### TD-059: Mock Strategy Inmadura

- **Descripción**: Mocks inconsistentes
- **Impacto**: Tests frágiles
- **Esfuerzo**: 1-2 días
- **Archivos**: Test configuration

#### TD-060: Performance Testing

- **Descripción**: Sin benchmarks de performance
- **Impacto**: Regresiones de performance
- **Esfuerzo**: 2-3 días
- **Archivos**: Performance test suite

### 🟢 Prioridad BAJA

#### TD-061: Mutation Testing

- **Descripción**: Calidad de tests no validada
- **Impacto**: Tests pueden ser inadecuados
- **Esfuerzo**: 1 día
- **Archivos**: Mutation testing config

---

## 📚 DOCUMENTACIÓN

### 🔴 Prioridad ALTA

#### TD-062: API Documentation Incompleta

- **Descripción**: Swagger/OpenAPI sin examples/schemas completos
- **Impacto**: Adopción de API limitada
- **Esfuerzo**: 2-3 días
- **Archivos**: Docstrings de endpoints

#### TD-063: Deployment Guide Faltante

- **Descripción**: Sin guía paso a paso para producción
- **Impacto**: Deployment errors
- **Esfuerzo**: 1 día
- **Archivos**: `docs/deployment.md`

### 🟡 Prioridad MEDIA

#### TD-064: Architecture Decision Records

- **Descripción**: Sin documentación de decisiones técnicas
- **Impacto**: Context loss, decisiones repetidas
- **Esfuerzo**: 1 día
- **Archivos**: `docs/adr/` (crear)

#### TD-065: Code Documentation

- **Descripción**: Docstrings inconsistentes
- **Impacto**: Mantenimiento difícil
- **Esfuerzo**: 2-3 días
- **Archivos**: Todo el código

#### TD-066: Troubleshooting Guide

- **Descripción**: Sin guía de resolución de problemas
- **Impacto**: Support inefficient
- **Esfuerzo**: 1 día
- **Archivos**: `docs/troubleshooting.md`

### 🟢 Prioridad BAJA

#### TD-067: Contributing Guidelines

- **Descripción**: Sin guías para contribuir
- **Impacto**: Contribuciones inconsistentes
- **Esfuerzo**: 4 horas
- **Archivos**: `CONTRIBUTING.md`

#### TD-068: Changelog Automation

- **Descripción**: Changelog manual
- **Impacto**: Release notes inconsistentes
- **Esfuerzo**: 2-3 horas
- **Archivos**: Automated changelog

---

## 🚀 DEVOPS

### 🔴 Prioridad ALTA

#### TD-069: CI/CD Pipeline Faltante

- **Descripción**: Sin automatización de deploy
- **Impacto**: Deployments manuales error-prone
- **Esfuerzo**: 2-3 días
- **Archivos**: `.github/workflows/`

#### TD-070: Environment Management

- **Descripción**: Solo desarrollo, sin staging/prod configs
- **Impacto**: Deploy a prod arriesgado
- **Esfuerzo**: 1 día
- **Archivos**: Environment configs

#### TD-071: Database Migrations Strategy

- **Descripción**: Sin estrategia de migración en prod
- **Impacto**: Data loss risk
- **Esfuerzo**: 1 día
- **Archivos**: Migration scripts

### 🟡 Prioridad MEDIA

#### TD-072: Backup Strategy Faltante

- **Descripción**: Sin backups automáticos
- **Impacto**: Data loss risk
- **Esfuerzo**: 1 día
- **Archivos**: Backup scripts

#### TD-073: Health Checks en Deploy

- **Descripción**: Deploy sin verificación de salud
- **Impacto**: Broken deployments
- **Esfuerzo**: 4 horas
- **Archivos**: Deploy scripts

#### TD-074: Resource Limits No Configurados

- **Descripción**: Containers sin límites
- **Impacto**: Resource starvation
- **Esfuerzo**: 2 horas
- **Archivos**: Docker configs

#### TD-075: Blue-Green Deployment Faltante

- **Descripción**: Deployment causa downtime
- **Impacto**: Availability issues
- **Esfuerzo**: 2-3 días
- **Archivos**: Deployment strategy

### 🟢 Prioridad BAJA

#### TD-076: Infrastructure as Code

- **Descripción**: Infrastructure manual
- **Impacto**: Reproducibilidad limitada
- **Esfuerzo**: 1 semana
- **Archivos**: Terraform/CloudFormation

#### TD-077: Multi-environment Automation

- **Descripción**: Promotions manuales entre environments
- **Impacto**: Proceso lento
- **Esfuerzo**: 2-3 días
- **Archivos**: CI/CD pipeline

#### TD-078: Container Security Scanning

- **Descripción**: Sin escaneo de vulnerabilidades
- **Impacto**: Security risks
- **Esfuerzo**: 1 día
- **Archivos**: Security scanning tools

---

## 📈 Plan de Resolución

### Sprint 1 (2 semanas) - Funcionalidad Básica

**Objetivo**: Hacer que la aplicación funcione básicamente

1. **TD-001**: Implementar servicios faltantes
2. **TD-002**: Completar endpoints básicos
3. **TD-003**: Crear migraciones de DB
4. **TD-005**: Crear Dockerfiles
5. **TD-021**: Componentes React básicos

### Sprint 2 (2 semanas) - Seguridad y Estabilidad

**Objetivo**: Aplicación segura y estable

1. **TD-036**: Mejorar autenticación
2. **TD-037**: Remover secretos hardcodeados
3. **TD-038**: Sanitización de inputs
4. **TD-051**: Tests unitarios críticos
5. **TD-069**: CI/CD básico

### Sprint 3 (2 semanas) - Calidad y Monitoreo

**Objetivo**: Observabilidad y calidad

1. **TD-042**: Métricas de aplicación
2. **TD-043**: Configurar alertas
3. **TD-052**: Tests de integración
4. **TD-044**: Dashboards Grafana
5. **TD-062**: Documentación API

### Sprint 4+ - Optimización y Features

**Objetivo**: Performance y features avanzadas

1. Completar frontend (TD-022 a TD-035)
2. Testing completo (TD-053 a TD-061)
3. DevOps avanzado (TD-070 a TD-078)
4. Documentación completa (TD-063 a TD-068)

---

## 🏷️ Etiquetas y Categorización

### Por Impacto

- `impact:critical` - Aplicación no funciona
- `impact:high` - Funcionalidad limitada
- `impact:medium` - UX/Performance afectada
- `impact:low` - Nice to have

### Por Esfuerzo

- `effort:1h` - Menos de 1 hora
- `effort:1d` - 1 día
- `effort:1w` - 1 semana
- `effort:1m` - 1 mes

### Por Tipo

- `type:bug` - Algo roto que necesita arreglo
- `type:feature` - Funcionalidad nueva
- `type:refactor` - Mejora de código existente
- `type:security` - Relacionado con seguridad
- `type:performance` - Optimización de performance

---

## 📊 Métricas de Progreso

### KPIs de Deuda Técnica

- **Cobertura de Tests**: 0% → Target: 80%
- **Security Scan Score**: N/A → Target: A
- **Performance Budget**: N/A → Target: <2s load
- **Documentation Coverage**: 20% → Target: 90%
- **CI/CD Maturity**: 0/10 → Target: 8/10

### Review Quincenal

- ✅ Items completados: 0/78
- 🔄 Items en progreso: 0
- ⏸️ Items bloqueados: 5
- 📈 Velocity (items/sprint): TBD

---

## 🤝 Contribución

Para agregar nuevos items de deuda técnica:

1. **Usar formato TD-XXX**
2. **Incluir**: Descripción, Impacto, Esfuerzo, Archivos
3. **Categorizar** por prioridad e impacto
4. **Linkear** con issues de GitHub
5. **Actualizar** métricas de progreso

### Template para Nuevos Items

```markdown
#### TD-XXX: Título Descriptivo

- **Descripción**: Qué está mal y por qué es deuda técnica
- **Impacto**: Cómo afecta al proyecto/usuarios
- **Esfuerzo**: Estimación realista de tiempo
- **Archivos**: Archivos específicos afectados
- **Bloqueante**: SÍ/NO
- **Relacionado**: TD-XXX, Issue #XXX
```

---

**Última actualización**: 2024-12-28  
**Próxima revisión**: En 2 semanas  
**Owner**: Tech Lead  
**Stakeholders**: Equipo de desarrollo completo
