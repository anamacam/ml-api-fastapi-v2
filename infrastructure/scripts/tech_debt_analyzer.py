#!/usr/bin/env python3
"""
🔍 Analizador de Deuda Técnica - ML API FastAPI v2
==================================================

Analiza el código para identificar y reportar deuda técnica en múltiples dimensiones:
- Complejidad ciclomática
- Cobertura de tests
- Duplicación de código
- Comentarios TODO/FIXME
- Convenciones de naming
- Métricas de archivos
- Dependencias obsoletas
"""

import os
import sys
import ast
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re


@dataclass
class DebtMetric:
    """Métrica individual de deuda técnica."""
    name: str
    value: float
    max_value: float
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    files_affected: List[str]
    recommendations: List[str]


@dataclass
class DebtReport:
    """Reporte completo de deuda técnica."""
    timestamp: str
    total_score: float
    max_score: float
    debt_percentage: float
    metrics: List[DebtMetric]
    summary: Dict[str, Any]


class TechnicalDebtAnalyzer:
    """Analizador principal de deuda técnica."""

    def __init__(self, project_root: str = "."):
        """
        Inicializar el analizador de deuda técnica.

        Args:
            project_root: Ruta raíz del proyecto a analizar.
        """
        self.project_root = Path(project_root)
        self.backend_path = self.project_root / "backend"
        self.frontend_path = self.project_root / "frontend"
        self.debt_report = DebtReport(
            timestamp=datetime.now().isoformat(),
            total_score=0.0,
            max_score=0.0,
            debt_percentage=0.0,
            metrics=[],
            summary={}
        )

    def analyze(self) -> DebtReport:
        """Ejecutar análisis completo de deuda técnica"""
        print("🔍 Iniciando análisis de deuda técnica...")

        # Análisis de código Python
        self._analyze_python_code_complexity()
        self._analyze_python_naming_conventions()
        self._analyze_todo_fixme_comments()
        self._analyze_file_metrics()

        # Análisis de documentación
        self._analyze_docstrings_quality()

        # Análisis de tests y TDD
        self._analyze_test_coverage()
        self._analyze_tdd_practices()

        # Análisis de dependencias
        self._analyze_dependencies()

        # Análisis de duplicación (simple)
        self._analyze_code_duplication()

        # Calcular score final
        self._calculate_final_score()

        print(f"✅ Análisis completado. Score: {self.debt_report.total_score:.1f}/{self.debt_report.max_score:.1f}")
        return self.debt_report

    def _analyze_python_code_complexity(self):
        """Analizar complejidad ciclomática del código Python"""
        print("  📊 Analizando complejidad ciclomática...")

        complex_files = []
        total_complexity = 0
        file_count = 0

        python_files = list(self.backend_path.rglob("*.py"))

        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                complexity = self._calculate_file_complexity(py_file)
                total_complexity += complexity
                file_count += 1

                if complexity > 10:  # Umbral de complejidad alta
                    complex_files.append(str(py_file.relative_to(self.project_root)))
            except Exception as e:
                print(f"    ⚠️  Error analizando {py_file}: {e}")

        avg_complexity = total_complexity / max(file_count, 1)
        severity = "low"
        if avg_complexity > 15:
            severity = "critical"
        elif avg_complexity > 10:
            severity = "high"
        elif avg_complexity > 7:
            severity = "medium"

        recommendations = []
        if complex_files:
            recommendations.extend([
                "Refactorizar funciones con alta complejidad ciclomática",
                "Dividir funciones grandes en funciones más pequeñas",
                "Implementar patrones de diseño para reducir complejidad"
            ])

        metric = DebtMetric(
            name="complejidad_ciclomatica",
            value=avg_complexity,
            max_value=20.0,
            description=f"Complejidad promedio: {avg_complexity:.1f}. Archivos complejos: {len(complex_files)}",
            severity=severity,
            files_affected=complex_files,
            recommendations=recommendations
        )

        self.debt_report.metrics.append(metric)

    def _calculate_file_complexity(self, file_path: Path) -> float:
        """Calcular complejidad ciclomática básica de un archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            tree = ast.parse(code)
            complexity = 1  # Base complexity

            for node in ast.walk(tree):
                # Incrementar complejidad por estructuras de control
                if isinstance(node, (ast.If, ast.While, ast.For, ast.FunctionDef,
                                   ast.AsyncFunctionDef, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, (ast.And, ast.Or)):
                    complexity += 1

            return complexity
        except:
            return 0

    def _analyze_python_naming_conventions(self):
        """Analizar convenciones de naming en Python"""
        print("  📝 Analizando convenciones de naming...")

        naming_issues = []
        python_files = list(self.backend_path.rglob("*.py"))

        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()

                tree = ast.parse(code)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not self._is_snake_case(node.name) and not node.name.startswith('_'):
                            naming_issues.append(f"{py_file.relative_to(self.project_root)}:{node.lineno} - función '{node.name}'")
                    elif isinstance(node, ast.ClassDef):
                        if not self._is_pascal_case(node.name):
                            naming_issues.append(f"{py_file.relative_to(self.project_root)}:{node.lineno} - clase '{node.name}'")
            except Exception:
                continue

        severity = "low"
        if len(naming_issues) > 20:
            severity = "high"
        elif len(naming_issues) > 10:
            severity = "medium"

        metric = DebtMetric(
            name="convenciones_naming",
            value=len(naming_issues),
            max_value=50.0,
            description=f"Violaciones de naming: {len(naming_issues)}",
            severity=severity,
            files_affected=[issue.split(':')[0] for issue in naming_issues[:10]],
            recommendations=[
                "Usar snake_case para funciones y variables",
                "Usar PascalCase para clases",
                "Revisar guía de estilo PEP 8"
            ] if naming_issues else []
        )

        self.debt_report.metrics.append(metric)

    def _is_snake_case(self, name: str) -> bool:
        """Verificar si un nombre está en snake_case"""
        return re.match(r'^[a-z_][a-z0-9_]*$', name) is not None

    def _is_pascal_case(self, name: str) -> bool:
        """Verificar si un nombre está en PascalCase"""
        return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None

    def _analyze_todo_fixme_comments(self):
        """Analizar comentarios TODO, FIXME, HACK, etc."""
        print("  📋 Analizando comentarios de deuda técnica...")

        debt_comments = []
        patterns = [r'TODO', r'FIXME', r'HACK', r'XXX', r'TEMP']

        # Analizar archivos Python
        for py_file in self.backend_path.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for i, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            debt_comments.append(f"{py_file.relative_to(self.project_root)}:{i} - {line.strip()}")
            except Exception:
                continue

        # Analizar archivos TypeScript/JavaScript
        for js_file in self.frontend_path.rglob("*.{ts,tsx,js,jsx}"):
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for i, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            debt_comments.append(f"{js_file.relative_to(self.project_root)}:{i} - {line.strip()}")
            except Exception:
                continue

        severity = "low"
        if len(debt_comments) > 15:
            severity = "high"
        elif len(debt_comments) > 8:
            severity = "medium"

        metric = DebtMetric(
            name="comentarios_deuda",
            value=len(debt_comments),
            max_value=30.0,
            description=f"Comentarios de deuda técnica: {len(debt_comments)}",
            severity=severity,
            files_affected=[comment.split(':')[0] for comment in debt_comments],
            recommendations=[
                "Resolver TODOs pendientes",
                "Refactorizar código marcado con HACK",
                "Documentar decisiones técnicas temporales"
            ] if debt_comments else []
        )

        self.debt_report.metrics.append(metric)

    def _analyze_file_metrics(self):
        """Analizar métricas de archivos (tamaño, líneas, etc.)"""
        print("  📏 Analizando métricas de archivos...")

        large_files = []
        total_lines = 0
        file_count = 0

        for py_file in self.backend_path.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())

                total_lines += lines
                file_count += 1

                if lines > 300:  # Archivos muy grandes
                    large_files.append(f"{py_file.relative_to(self.project_root)} ({lines} líneas)")
            except Exception:
                continue

        avg_lines = total_lines / max(file_count, 1)

        severity = "low"
        if len(large_files) > 5:
            severity = "high"
        elif len(large_files) > 2:
            severity = "medium"

        metric = DebtMetric(
            name="metricas_archivos",
            value=len(large_files),
            max_value=10.0,
            description=f"Archivos grandes: {len(large_files)}. Promedio: {avg_lines:.0f} líneas",
            severity=severity,
            files_affected=[f.split(' (')[0] for f in large_files],
            recommendations=[
                "Dividir archivos grandes en módulos más pequeños",
                "Aplicar principio de responsabilidad única",
                "Extraer clases o funciones a archivos separados"
            ] if large_files else []
        )

        self.debt_report.metrics.append(metric)

    def _analyze_docstrings_quality(self):
        """Analizar calidad y completitud de docstrings."""
        print("  📝 Analizando calidad de docstrings...")

        python_objects = []
        missing_docstrings = []
        incomplete_docstrings = []

        # Buscar en todo el proyecto, no solo backend
        for py_file in self.project_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()

                tree = ast.parse(code)
                relative_path = str(py_file.relative_to(self.project_root))

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        python_objects.append(node.name)

                        # Verificar si tiene docstring
                        docstring = ast.get_docstring(node)

                        if not docstring:
                            missing_docstrings.append(f"{relative_path}:{node.lineno} - {type(node).__name__} '{node.name}'")
                        else:
                            # Verificar calidad básica del docstring
                            if len(docstring.strip()) < 10:
                                incomplete_docstrings.append(f"{relative_path}:{node.lineno} - {type(node).__name__} '{node.name}' (muy corto)")
                            elif not docstring.strip().endswith('.'):
                                incomplete_docstrings.append(f"{relative_path}:{node.lineno} - {type(node).__name__} '{node.name}' (sin punto final)")
                            elif isinstance(node, ast.FunctionDef) and node.args.args and 'Args:' not in docstring and 'Parameters:' not in docstring:
                                if len(node.args.args) > 1:  # Más de solo 'self'
                                    incomplete_docstrings.append(f"{relative_path}:{node.lineno} - función '{node.name}' (sin documentar parámetros)")

            except Exception as e:
                print(f"    ⚠️  Error analizando docstrings en {py_file}: {e}")
                continue

        total_objects = len(python_objects)
        missing_count = len(missing_docstrings)
        incomplete_count = len(incomplete_docstrings)

        if total_objects > 0:
            completion_rate = ((total_objects - missing_count) / total_objects) * 100
        else:
            completion_rate = 100.0

        # Determinar severidad basada en completion rate
        severity = "low"
        if completion_rate < 40:
            severity = "critical"
        elif completion_rate < 60:
            severity = "high"
        elif completion_rate < 80:
            severity = "medium"

        affected_files = list(set([
            issue.split(':')[0] for issue in missing_docstrings + incomplete_docstrings
        ]))

        recommendations = []
        if missing_count > 0:
            recommendations.extend([
                "Agregar docstrings a funciones y clases públicas",
                "Seguir estándar PEP 257 para docstrings",
                "Usar formato Google Style o NumPy Style"
            ])
        if incomplete_count > 0:
            recommendations.extend([
                "Mejorar calidad de docstrings existentes",
                "Documentar parámetros, retornos y excepciones",
                "Terminar docstrings con punto final"
            ])

        metric = DebtMetric(
            name="calidad_docstrings",
            value=completion_rate,
            max_value=100.0,
            description=f"Completitud: {completion_rate:.1f}% ({total_objects - missing_count}/{total_objects} objetos con docstring). Incompletos: {incomplete_count}",
            severity=severity,
            files_affected=affected_files,
            recommendations=recommendations
        )

        self.debt_report.metrics.append(metric)

    def _analyze_test_coverage(self):
        """Analizar cobertura de tests"""
        print("  🧪 Analizando cobertura de tests...")

        test_files = list(self.backend_path.rglob("test_*.py"))
        source_files = [f for f in self.backend_path.rglob("*.py")
                       if "venv" not in str(f) and "test_" not in f.name and "__pycache__" not in str(f)]

        test_ratio = len(test_files) / max(len(source_files), 1)

        severity = "low"
        if test_ratio < 0.3:
            severity = "critical"
        elif test_ratio < 0.5:
            severity = "high"
        elif test_ratio < 0.7:
            severity = "medium"

        metric = DebtMetric(
            name="cobertura_tests",
            value=test_ratio * 100,
            max_value=100.0,
            description=f"Ratio tests/código: {test_ratio:.2f} ({len(test_files)} tests, {len(source_files)} archivos)",
            severity=severity,
            files_affected=[],
            recommendations=[
                "Aumentar cobertura de tests unitarios",
                "Implementar tests de integración",
                "Agregar tests para casos edge"
            ] if test_ratio < 0.8 else []
        )

        self.debt_report.metrics.append(metric)

    def _analyze_tdd_practices(self):
        """Analizar prácticas de Test-Driven Development (TDD)."""
        print("  🎯 Analizando prácticas TDD...")

        tdd_indicators = {
            'test_structure': 0,
            'test_naming': 0,
            'test_organization': 0,
            'test_first_approach': 0,
            'test_quality': 0
        }

        issues = []
        test_files = []

        # Buscar archivos de test
        for test_file in self.project_root.rglob("test_*.py"):
            if "venv" in str(test_file) or "__pycache__" in str(test_file):
                continue
            test_files.append(test_file)

        # También buscar en carpetas tests/
        for test_file in self.project_root.rglob("tests/**/*.py"):
            if "venv" in str(test_file) or "__pycache__" in str(test_file):
                continue
            if test_file not in test_files:
                test_files.append(test_file)

        if not test_files:
            issues.append("No se encontraron archivos de test")
            tdd_score = 0
            achieved_indicators = 0
            total_indicators = 0
        else:
            total_indicators = 0

            for test_file in test_files:
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    relative_path = str(test_file.relative_to(self.project_root))

                    # 1. Estructura de tests (pytest, unittest, etc.)
                    if any(pattern in content for pattern in ['def test_', 'class Test', '@pytest', 'unittest']):
                        tdd_indicators['test_structure'] += 1
                    else:
                        issues.append(f"{relative_path}: Sin estructura de test reconocible")

                    # 2. Naming conventions para tests
                    import re
                    test_functions = re.findall(r'def (test_\w+)', content)
                    if test_functions:
                        descriptive_names = [name for name in test_functions if len(name) > 10]
                        if len(descriptive_names) >= len(test_functions) * 0.7:
                            tdd_indicators['test_naming'] += 1
                        else:
                            issues.append(f"{relative_path}: Nombres de test poco descriptivos")

                    # 3. Organización (fixtures, setup, teardown)
                    if any(pattern in content for pattern in ['@pytest.fixture', 'setUp', 'tearDown', 'conftest']):
                        tdd_indicators['test_organization'] += 1

                    # 4. Enfoque TDD (arrange-act-assert, given-when-then)
                    if any(pattern in content.lower() for pattern in ['# arrange', '# act', '# assert',
                                                                     '# given', '# when', '# then',
                                                                     'arrange', 'act', 'assert']):
                        tdd_indicators['test_first_approach'] += 1

                    # 5. Calidad de tests (mocks, parametrize, etc.)
                    if any(pattern in content for pattern in ['@mock', '@patch', '@parametrize', 'Mock()', 'MagicMock']):
                        tdd_indicators['test_quality'] += 1

                    total_indicators += 5  # 5 indicadores por archivo

                except Exception as e:
                    issues.append(f"Error analizando {test_file}: {e}")

            # Calcular score TDD
            achieved_indicators = sum(tdd_indicators.values())
            tdd_score = (achieved_indicators / max(total_indicators, 1)) * 100 if total_indicators > 0 else 0

        # Determinar severidad
        severity = "low"
        if tdd_score < 30:
            severity = "critical"
        elif tdd_score < 50:
            severity = "high"
        elif tdd_score < 70:
            severity = "medium"

        # Recomendaciones basadas en indicadores faltantes
        recommendations = []
        if tdd_indicators['test_structure'] < len(test_files) * 0.8:
            recommendations.append("Usar frameworks de testing estándar (pytest, unittest)")
        if tdd_indicators['test_naming'] < len(test_files) * 0.7:
            recommendations.append("Usar nombres descriptivos para tests (test_should_do_something_when_condition)")
        if tdd_indicators['test_organization'] < len(test_files) * 0.5:
            recommendations.append("Implementar fixtures y setup/teardown para tests")
        if tdd_indicators['test_first_approach'] < len(test_files) * 0.3:
            recommendations.append("Seguir patrón Arrange-Act-Assert en tests")
        if tdd_indicators['test_quality'] < len(test_files) * 0.4:
            recommendations.append("Usar mocks y parametrización para tests robustos")

        if not recommendations:
            recommendations = ["Mantener buenas prácticas TDD", "Considerar agregar más tests de integración"]

        affected_files = [str(f.relative_to(self.project_root)) for f in test_files[:5]]

        metric = DebtMetric(
            name="practicas_tdd",
            value=tdd_score,
            max_value=100.0,
            description=f"Score TDD: {tdd_score:.1f}% ({len(test_files)} archivos test). Indicadores: {achieved_indicators}/{total_indicators}",
            severity=severity,
            files_affected=affected_files,
            recommendations=recommendations
        )

        self.debt_report.metrics.append(metric)

    def _analyze_dependencies(self):
        """Analizar dependencias obsoletas o problemáticas"""
        print("  📦 Analizando dependencias...")

        requirements_file = self.backend_path / "requirements" / "base.txt"
        package_json = self.frontend_path / "web-app" / "package.json"

        outdated_deps = []

        # Analizar Python dependencies (básico)
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]

                # Simulación simple de check de versiones
                for dep in deps[:5]:  # Solo primeras 5 para no ser muy pesado
                    if '==' in dep and any(old in dep.lower() for old in ['2.', '0.', '1.']):
                        outdated_deps.append(f"Python: {dep}")
            except Exception:
                pass

        # Analizar Node dependencies (básico)
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)

                deps = package_data.get('dependencies', {})
                for name, version in deps.items():
                    if version.startswith('^') and any(old in version for old in ['16.', '17.']):
                        outdated_deps.append(f"Node: {name}@{version}")
            except Exception:
                pass

        severity = "low"
        if len(outdated_deps) > 5:
            severity = "high"
        elif len(outdated_deps) > 2:
            severity = "medium"

        metric = DebtMetric(
            name="dependencias",
            value=len(outdated_deps),
            max_value=20.0,
            description=f"Dependencias potencialmente obsoletas: {len(outdated_deps)}",
            severity=severity,
            files_affected=outdated_deps,
            recommendations=[
                "Actualizar dependencias a versiones recientes",
                "Revisar breaking changes antes de actualizar",
                "Usar herramientas como dependabot"
            ] if outdated_deps else []
        )

        self.debt_report.metrics.append(metric)

    def _analyze_code_duplication(self):
        """Analizar duplicación de código (básico)"""
        print("  🔄 Analizando duplicación de código...")

        # Análisis muy básico: buscar funciones con nombres similares
        function_names = []
        duplicated_patterns = []

        for py_file in self.backend_path.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()

                tree = ast.parse(code)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        function_names.append((node.name, str(py_file.relative_to(self.project_root))))
            except Exception:
                continue

        # Buscar nombres de función similares (indicativo de duplicación)
        seen_names = {}
        for name, file_path in function_names:
            if name in seen_names and name not in ['__init__', 'main', 'test_']:
                duplicated_patterns.append(f"{name} en {file_path} y {seen_names[name]}")
            else:
                seen_names[name] = file_path

        severity = "low"
        if len(duplicated_patterns) > 10:
            severity = "high"
        elif len(duplicated_patterns) > 5:
            severity = "medium"

        metric = DebtMetric(
            name="duplicacion_codigo",
            value=len(duplicated_patterns),
            max_value=15.0,
            description=f"Patrones potenciales de duplicación: {len(duplicated_patterns)}",
            severity=severity,
            files_affected=[pattern.split(' en ')[1].split(' y ')[0] for pattern in duplicated_patterns],
            recommendations=[
                "Extraer código común a funciones utilitarias",
                "Implementar patrones DRY (Don't Repeat Yourself)",
                "Crear clases base para funcionalidad común"
            ] if duplicated_patterns else []
        )

        self.debt_report.metrics.append(metric)

    def _calculate_final_score(self):
        """Calcular score final de deuda técnica"""
        total_score = 0.0
        max_score = 0.0

        # Pesos por importancia
        weights = {
            'complejidad_ciclomatica': 0.18,
            'cobertura_tests': 0.18,
            'practicas_tdd': 0.18,
            'calidad_docstrings': 0.18,
            'convenciones_naming': 0.12,
            'comentarios_deuda': 0.08,
            'metricas_archivos': 0.05,
            'dependencias': 0.02,
            'duplicacion_codigo': 0.01
        }

        for metric in self.debt_report.metrics:
            weight = weights.get(metric.name, 0.1)

            # Para docstrings y TDD, el valor ya es un porcentaje (más alto = mejor)
            if metric.name in ['calidad_docstrings', 'practicas_tdd']:
                normalized_score = metric.value  # Ya está en porcentaje
            else:
                # Invertir score para que menor deuda = mayor score
                normalized_score = max(0, (metric.max_value - metric.value) / metric.max_value) * 100

            weighted_score = normalized_score * weight

            total_score += weighted_score
            max_score += 100 * weight

        self.debt_report.total_score = total_score
        self.debt_report.max_score = max_score
        self.debt_report.debt_percentage = 100 - (total_score / max_score * 100) if max_score > 0 else 100

        # Summary
        self.debt_report.summary = {
            'total_metrics': len(self.debt_report.metrics),
            'critical_issues': len([m for m in self.debt_report.metrics if m.severity == 'critical']),
            'high_issues': len([m for m in self.debt_report.metrics if m.severity == 'high']),
            'medium_issues': len([m for m in self.debt_report.metrics if m.severity == 'medium']),
            'low_issues': len([m for m in self.debt_report.metrics if m.severity == 'low']),
            'grade': self._get_grade(self.debt_report.debt_percentage)
        }

    def _get_grade(self, debt_percentage: float) -> str:
        """Obtener calificación basada en porcentaje de deuda"""
        if debt_percentage < 10:
            return 'A'
        elif debt_percentage < 20:
            return 'B'
        elif debt_percentage < 35:
            return 'C'
        elif debt_percentage < 50:
            return 'D'
        else:
            return 'F'

    def generate_report(self, format_type: str = "console") -> str:
        """Generar reporte en formato especificado"""
        if format_type == "json":
            return json.dumps(asdict(self.debt_report), indent=2, default=str)
        elif format_type == "console":
            return self._generate_console_report()
        else:
            raise ValueError(f"Formato no soportado: {format_type}")

    def _generate_console_report(self) -> str:
        """Generar reporte para consola"""
        report = []

        report.append("🔍 REPORTE DE DEUDA TÉCNICA")
        report.append("=" * 50)
        report.append(f"📅 Timestamp: {self.debt_report.timestamp}")
        report.append(f"📊 Score: {self.debt_report.total_score:.1f}/{self.debt_report.max_score:.1f}")
        report.append(f"💸 Deuda: {self.debt_report.debt_percentage:.1f}%")
        report.append(f"🎯 Calificación: {self.debt_report.summary['grade']}")
        report.append("")

        report.append("📈 RESUMEN DE ISSUES")
        report.append("-" * 30)
        report.append(f"🔴 Críticos: {self.debt_report.summary['critical_issues']}")
        report.append(f"🟠 Altos: {self.debt_report.summary['high_issues']}")
        report.append(f"🟡 Medios: {self.debt_report.summary['medium_issues']}")
        report.append(f"🟢 Bajos: {self.debt_report.summary['low_issues']}")
        report.append("")

        report.append("📋 MÉTRICAS DETALLADAS")
        report.append("-" * 30)

        for metric in self.debt_report.metrics:
            severity_icon = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(metric.severity, '⚪')

            report.append(f"{severity_icon} {metric.name.upper()}")
            report.append(f"   Valor: {metric.value:.1f}/{metric.max_value}")
            report.append(f"   {metric.description}")

            if metric.files_affected:
                report.append(f"   Archivos: {len(metric.files_affected)} afectados")
                for file_path in metric.files_affected[:3]:
                    report.append(f"     - {file_path}")
                if len(metric.files_affected) > 3:
                    report.append(f"     ... y {len(metric.files_affected) - 3} más")

            if metric.recommendations:
                report.append("   Recomendaciones:")
                for rec in metric.recommendations[:2]:
                    report.append(f"     • {rec}")

            report.append("")

        return "\n".join(report)


def main():
    """Función principal del analizador de deuda técnica."""
    parser = argparse.ArgumentParser(description="Analizador de Deuda Técnica")
    parser.add_argument("--format", choices=["console", "json"], default="console",
                       help="Formato de salida del reporte")
    parser.add_argument("--output", "-o", help="Archivo de salida (opcional)")

    args = parser.parse_args()

    try:
        analyzer = TechnicalDebtAnalyzer()
        report = analyzer.analyze()
        output = analyzer.generate_report(args.format)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"📄 Reporte guardado en: {args.output}")
        else:
            print(output)

        # Exit code basado en la calificación
        grade = report.summary['grade']
        if grade in ['A', 'B']:
            sys.exit(0)
        elif grade == 'C':
            sys.exit(1)
        else:
            sys.exit(2)

    except Exception as e:
        print(f"❌ Error durante análisis: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
