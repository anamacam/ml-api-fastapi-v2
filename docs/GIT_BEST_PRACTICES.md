# 🔧 Buenas Prácticas Git - Sistema Automatizado

## 📋 Resumen

Este documento describe las buenas prácticas generales de Git adoptadas en este proyecto, como la estrategia de branches, el tamaño de los commits y cómo mantener un historial limpio.

Para detalles sobre el **formato de los mensajes de commit (Conventional Commits)** y el uso de nuestro script de validación, por favor consulta nuestra guía principal:

➡️ **[📄 Sistema de Commits Inteligentes (COMMIT_SYSTEM.md)](COMMIT_SYSTEM.md)**

## 🛠️ Herramientas Disponibles

### 1. **🧠 Smart Commit** (`.\scripts\smart_commit_clean.ps1`)

Commit inteligente con validación automática:

```powershell
# Modo interactivo (RECOMENDADO)
.\scripts\smart_commit_clean.ps1 -Interactive

# Commit directo con mensaje
.\scripts\smart_commit_clean.ps1 -Message "feat: add user authentication"

# Commit con tipo y scope específicos
.\scripts\smart_commit_clean.ps1 -Type "fix" -Scope "auth" -Message "resolve login issue"

# Modo dry-run (sin commit real)
.\scripts\smart_commit_clean.ps1 -DryRun -Message "test message"

# Modo forzado (bypass validaciones)
.\scripts\smart_commit_clean.ps1 -Force -Message "emergency fix"
```

### 2. **🔍 Analizador Git** (`git_best_practices.py`)

Análisis completo de prácticas Git:

```bash
# Análisis completo
python backend/infrastructure/scripts/git_best_practices.py

# Validar mensaje específico
python backend/infrastructure/scripts/git_best_practices.py --validate-message "feat: new feature"

# Generar template
python backend/infrastructure/scripts/git_best_practices.py --template feat

# Formato JSON
python backend/infrastructure/scripts/git_best_practices.py --format json
```

## 🌿 Estrategia de Branches

### Convenciones de Naming

```
<tipo>/<descripción-corta>
```

| Tipo          | Propósito              | Ejemplo                 |
| ------------- | ---------------------- | ----------------------- |
| `feature/`    | Nuevas funcionalidades | `feature/user-profile`  |
| `fix/`        | Correcciones           | `fix/login-validation`  |
| `hotfix/`     | Correcciones urgentes  | `hotfix/security-patch` |
| `release/`    | Preparación release    | `release/v1.2.0`        |
| `experiment/` | Experimentos           | `experiment/new-ui`     |

### Flujo de Trabajo

1. **Crear branch** desde `main`/`develop`
2. **Desarrollar** con commits pequeños
3. **Push regular** para backup
4. **Pull Request** con descripción clara
5. **Code Review** obligatorio
6. **Merge** con squash si necesario
7. **Delete branch** después del merge

### Branches Especiales

- **`main`/`master`**: Código productivo estable
- **`develop`**: Integración de features
- **`staging`**: Testing pre-producción

## 📏 Tamaño de Commits

### Principios

- **Atómicos**: Un cambio lógico por commit
- **Pequeños**: Máximo 10 archivos por commit
- **Frecuentes**: Commitear temprano y seguido
- **Completos**: Cada commit debe compilar/funcionar

### Qué Incluir en Un Commit

✅ **Un solo cambio lógico:**

- Una nueva función completa
- Una corrección específica
- Refactoring de un módulo
- Actualización de documentación relacionada

❌ **Múltiples cambios:**

- Feature nueva + correcciones no relacionadas
- Cambios en múltiples módulos sin relación
- Experimentación + código productivo
- Formateo + lógica de negocio

## 🔄 Historial Limpio

### Técnicas de Limpieza

#### 1. **Interactive Rebase**

```bash
# Limpiar últimos 3 commits
git rebase -i HEAD~3

# Opciones disponibles:
# pick - mantener commit
# reword - cambiar mensaje
# squash - combinar con anterior
# drop - eliminar commit
```

#### 2. **Squash Commits**

```bash
# Combinar múltiples commits WIP
git reset --soft HEAD~3
git commit -m "feat: implement user authentication"
```

#### 3. **Amend Commits**

```bash
# Modificar último commit
git commit --amend -m "fix(auth): resolve validation logic"

# Añadir archivos al último commit
git add forgotten-file.py
git commit --amend --no-edit
```

### Evitar Merge Commits

Preferir **rebase** sobre **merge** para mantener historial lineal:

```bash
# En lugar de merge
git merge feature-branch

# Usar rebase
git rebase main
# Luego fast-forward merge
git checkout main
git merge feature-branch
```

## 🧪 Integración con Tests

### Pre-commit Hooks

Ejecutar automáticamente:

- **Linting**: flake8, black, isort
- **Tests**: pytest suite
- **Quality checks**: checklist automatizado
- **Git practices**: validación mensajes

### Comandos Integrados

```powershell
# Commit con validación completa
.\scripts\smart_commit_clean.ps1 -Interactive

# Solo ejecutar checks
.\scripts\test.ps1

# Análisis completo
.\scripts\quality.ps1
```

## 📊 Métricas y Scoring

### Sistema de Puntuación

| Categoría               | Peso | Descripción                    |
| ----------------------- | ---- | ------------------------------ |
| **Mensajes Commit**     | 40%  | Conventional Commits, longitud |
| **Estructura Branches** | 20%  | Naming, organización           |
| **Tamaño Commits**      | 20%  | Atomicidad, frecuencia         |
| **Historial Git**       | 20%  | Limpieza, merges               |

### Grados de Calidad

- **A+ (90-100%)**: 🏆 Prácticas ejemplares
- **A (80-89%)**: ✨ Muy buenas prácticas
- **B (70-79%)**: 👍 Buenas prácticas
- **C (60-69%)**: ⚠️ Necesita mejoras
- **D (50-59%)**: ❌ Requiere atención
- **F (<50%)**: 💥 Crítico

## 🚀 Comandos Rápidos

### Setup Inicial

```powershell
# Instalar sistema completo
.\setup.ps1

# Configurar Git globalmente
git config --global commit.template .gitmessage
git config --global core.editor "code --wait"
```

### Uso Diario

```powershell
# Commit inteligente
.\scripts\smart_commit_clean.ps1 -Interactive

# Verificar calidad
.\scripts\quality.ps1

# Análisis Git específico
python backend/infrastructure/scripts/git_best_practices.py
```

### Validaciones

```powershell
# Validar mensaje antes de commit
python backend/infrastructure/scripts/git_best_practices.py --validate-message "tu mensaje"

# Dry run (sin commit real)
.\scripts\smart_commit_clean.ps1 -DryRun -Message "test message"
```

## 🔧 Configuración Avanzada

### Hooks Personalizados

Editar `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: git-practices-check
        name: Git Best Practices
        entry: python backend/infrastructure/scripts/git_best_practices.py
        language: system
        pass_filenames: false
```

### Templates de Commit

Crear `.gitmessage`:

```
# <tipo>(<scope>): <descripción>
#
# Explicación más detallada del cambio (opcional)
#
# Tipos: feat, fix, docs, style, refactor, test, chore, perf, ci, build
# Scope: componente afectado (auth, api, ui, db, etc.)
# Descripción: imperativo, presente, máximo 50 chars
```

### Aliases Útiles

```bash
git config --global alias.smart-commit '!powershell -File scripts/smart_commit_clean.ps1'
git config --global alias.quality '!powershell -File scripts/quality.ps1'
git config --global alias.analyze '!python backend/infrastructure/scripts/git_best_practices.py'
```

## 📚 Recursos y Referencias

### Documentación Oficial

- **[Conventional Commits](https://www.conventionalcommits.org/)**: Especificación estándar
- **[Git Best Practices](https://git-scm.com/docs/gitworkflows)**: Flujos oficiales
- **[Semantic Versioning](https://semver.org/)**: Versionado semántico

### Herramientas Recomendadas

- **[Commitizen](https://commitizen-tools.github.io/commitizen/)**: CLI para Conventional Commits
- **[Husky](https://typicode.github.io/husky/)**: Git hooks (Node.js)
- **[Pre-commit](https://pre-commit.com/)**: Framework hooks (Python)

### Lecturas Adicionales

- **"Pro Git"** por Scott Chacon
- **"Git Internals"** documentación
- **"Clean Code"** por Robert Martin (capítulos Git)

## 🎯 Checklist de Verificación

### Antes de Commit

- [ ] ✅ Cambios son atómicos y relacionados
- [ ] ✅ Tests pasan localmente
- [ ] ✅ Código está formateado
- [ ] ✅ Mensaje sigue Conventional Commits
- [ ] ✅ No hay archivos temporales/debug
- [ ] ✅ Documentación actualizada si necesario

### Antes de Push

- [ ] ✅ Rebase con branch principal si necesario
- [ ] ✅ Historial está limpio
- [ ] ✅ No hay merge commits innecesarios
- [ ] ✅ Branch name sigue convenciones
- [ ] ✅ Commits son descriptivos

### Antes de Pull Request

- [ ] ✅ Descripción clara del cambio
- [ ] ✅ Links a issues relacionados
- [ ] ✅ Screenshots si hay cambios UI
- [ ] ✅ Tests cubren funcionalidad nueva
- [ ] ✅ Breaking changes documentados

---

## 💡 Tips Avanzados

### 1. **Stashing Inteligente**

```bash
# Guardar cambios con mensaje
git stash push -m "work in progress on feature X"

# Aplicar stash específico
git stash pop stash@{1}
```

### 2. **Cherry-pick Selectivo**

```bash
# Aplicar commit específico
git cherry-pick <commit-hash>

# Rango de commits
git cherry-pick start-commit..end-commit
```

### 3. **Bisect para Debug**

```bash
# Encontrar commit que introdujo bug
git bisect start
git bisect bad HEAD
git bisect good v1.0
# Git guiará el proceso
```

### 4. **Reflog para Recuperación**

```bash
# Ver historial completo
git reflog

# Recuperar commit "perdido"
git reset --hard HEAD@{5}
```

¡Con este sistema, tus prácticas Git serán ejemplares! 🚀
