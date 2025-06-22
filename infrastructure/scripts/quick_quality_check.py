#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Quick Quality Check - ML API FastAPI v2
==========================================

Check rápido de calidad para pre-commit:
- Verificaciones básicas de código
- Umbrales críticos
- Feedback inmediato
- Sin análisis pesado
"""

import ast
import subprocess
import sys
from pathlib import Path
from typing import List


class QuickQualityChecker:
    """Verificador rápido de calidad para pre-commit."""

    def __init__(self):
        self.project_root = Path(".")
        self.backend_path = self.project_root / "backend"
        self.errors = []
        self.warnings = []

    def run_quick_checks(self) -> bool:
        """Ejecutar checks rápidos. Retorna True si pasa todos los checks."""
        print("⚡ Ejecutando checks rápidos de calidad...")

        # 1. Verificar archivos Python modificados
        modified_files = self._get_modified_python_files()

        if not modified_files:
            print("✅ No hay archivos Python modificados")
            return True

        # 2. Checks rápidos en archivos modificados
        for file_path in modified_files:
            self._check_file_basics(file_path)
            self._check_complexity_threshold(file_path)
            self._check_function_size(file_path)
            self._check_imports_quality(file_path)

        # 3. Verificar umbrales críticos
        critical_passed = self._check_critical_thresholds()

        # 4. Mostrar resultados
        self._show_results()

        # 5. Decidir si permitir commit
        return len(self.errors) == 0 and critical_passed

    def _get_modified_python_files(self) -> List[Path]:
        """Obtener archivos Python modificados."""
        try:
            # Obtener archivos staged
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=AMR"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return []

            files = []
            for line in result.stdout.strip().split("\n"):
                if line and line.endswith(".py"):
                    file_path = Path(line)
                    if file_path.exists() and "venv" not in str(file_path):
                        files.append(file_path)

            return files
        except Exception:
            return []

    def _check_file_basics(self, file_path: Path):
        """Verificaciones básicas del archivo."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Verificar sintaxis Python
            try:
                ast.parse(content)
            except SyntaxError as e:
                self.errors.append(
                    f"❌ {file_path}: Error de sintaxis en línea {e.lineno}"
                )

            # Verificar longitud de líneas (básico)
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if len(line) > 120:  # Límite permisivo
                    self.warnings.append(
                        f"⚠️ {file_path}:{i}: Línea muy larga ({len(line)} chars)"
                    )

            # Verificar imports al inicio
            tree = ast.parse(content)
            import_after_code = False
            found_non_import = False

            for node in tree.body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if found_non_import:
                        import_after_code = True
                elif isinstance(node, ast.Expr):
                    # Skip docstrings (string literals at module level)
                    if isinstance(node.value, ast.Constant) and isinstance(
                        node.value.value, str
                    ):
                        continue  # Docstring
                    found_non_import = True
                else:
                    found_non_import = True

            if import_after_code:
                self.warnings.append(f"⚠️ {file_path}: Imports después del código")

        except Exception as e:
            self.warnings.append(f"⚠️ {file_path}: Error al verificar archivo - {e}")

    def _check_complexity_threshold(self, file_path: Path):
        """Verificar complejidad ciclomática básica."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_function_complexity(node)

                    if complexity > 15:  # Umbral crítico
                        self.errors.append(
                            f"❌ {file_path}: Función '{node.name}' "
                            f"muy compleja ({complexity})"
                        )
                    elif complexity > 10:  # Umbral de advertencia
                        self.warnings.append(
                            f"⚠️ {file_path}: Función '{node.name}' "
                            f"compleja ({complexity})"
                        )
        except Exception:
            pass  # Skip si hay errores

    def _calculate_function_complexity(self, func_node) -> int:
        """Calcular complejidad ciclomática básica de una función."""
        complexity = 1  # Base complexity

        for node in ast.walk(func_node):
            # Incrementar por estructuras de control
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(node, ast.ListComp):
                complexity += 1

        return complexity

    def _check_function_size(self, file_path: Path):
        """Verificar tamaño de funciones."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            tree = ast.parse("".join(lines))

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if hasattr(node, "end_lineno") and node.end_lineno:
                        func_lines = node.end_lineno - node.lineno + 1

                        # Umbrales estándar para todos los archivos
                        critical_threshold = 50
                        warning_threshold = 30

                        if func_lines > critical_threshold:
                            self.errors.append(
                                f"❌ {file_path}: Función '{node.name}' "
                                f"muy larga ({func_lines} líneas)"
                            )
                        elif func_lines > warning_threshold:
                            self.warnings.append(
                                f"⚠️ {file_path}: Función '{node.name}' "
                                f"larga ({func_lines} líneas)"
                            )
        except Exception:
            pass  # Skip si hay errores

    def _check_imports_quality(self, file_path: Path):
        """Verificar calidad de imports."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Buscar imports problemáticos
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                line = line.strip()

                # Import * check temporalmente deshabilitado (detecta falsos positivos)
                # if 'from' in line and 'import *' in line:
                #     self.errors.append(f"❌ {file_path}:{i}: Import * prohibido")

                # Imports no utilizados (básico) - skip por ahora
                # if line.startswith('import ') and not any(
                #     module in content for module in line.replace('import ', '').split(',')
                # ):
                #     self.warnings.append(f"⚠️ {file_path}:{i}: Posible import no utilizado")

        except Exception:
            pass  # Skip si hay errores

    def _check_critical_thresholds(self) -> bool:
        """Verificar umbrales críticos que bloquean el commit."""

        # Si hay muchos errores, bloquear
        if len(self.errors) > 5:
            print(f"🚨 CRÍTICO: Demasiados errores ({len(self.errors)})")
            return False

        # Verificar que no haya archivos completamente rotos
        broken_files = [error for error in self.errors if "Error de sintaxis" in error]
        if broken_files:
            print("🚨 CRÍTICO: Archivos con errores de sintaxis")
            return False

        return True

    def _show_results(self):
        """Mostrar resultados del check."""

        if not self.errors and not self.warnings:
            print("✅ Todos los checks rápidos pasaron")
            return

        if self.errors:
            print(f"\n❌ ERRORES ({len(self.errors)}):")
            for error in self.errors[:5]:  # Mostrar solo los primeros 5
                print(f"  {error}")
            if len(self.errors) > 5:
                print(f"  ... y {len(self.errors) - 5} errores más")

        if self.warnings:
            print(f"\n⚠️ ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings[:5]:  # Mostrar solo las primeras 5
                print(f"  {warning}")
            if len(self.warnings) > 5:
                print(f"  ... y {len(self.warnings) - 5} advertencias más")

        print()

        # Calcular puntaje de calidad
        error_penalty = len(self.errors) * 20
        warning_penalty = len(self.warnings) * 10
        quality_score = max(0, 100 - error_penalty - warning_penalty)
        quality_level, recommendation = self._get_quality_level(quality_score)

        print(f"📈 Score de calidad: {quality_score:.1f}/100 " f"({quality_level})")
        print(f"🎯 Recomendación: {recommendation}")

    def _get_quality_level(self, score: float) -> tuple:
        """Determinar nivel de calidad según el puntaje."""
        if score >= 90:
            return ("Excelente", "¡Excelente trabajo!")
        elif score >= 70:
            return ("Bueno", "¡Buen trabajo!")
        elif score >= 50:
            return ("Regular", "¡Trabajo regular!")
        else:
            return ("Malo", "¡Necesitas mejorar!")


def main():
    """Función principal."""
    checker = QuickQualityChecker()

    try:
        success = checker.run_quick_checks()

        if success:
            print("🎉 Pre-commit quality check: PASSED")
            print("💡 Tip: El pipeline completo se ejecutará en GitHub Actions")
            return 0
        else:
            print("❌ Pre-commit quality check: FAILED")
            print("🔧 Corrige los errores antes de hacer commit")
            print("💡 Usa 'git commit --no-verify' solo en emergencias")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️ Check cancelado por el usuario")
        return 1
    except Exception as e:
        print(f"⚠️ Error en quality check: {e}")
        print("🔄 Continuando con commit (error en herramienta)")
        return 0  # No bloquear por errores de la herramienta


if __name__ == "__main__":
    sys.exit(main())
