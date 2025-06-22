#!/usr/bin/env python3
"""
📝 Verificador de Estándares de Docstrings - ML API FastAPI v2
==============================================================

Verifica que los docstrings en el código Python cumplan con:
- PEP 257 (Docstring Conventions)
- Google Style Guide
- Numpy Style (opcional)
- Sphinx compatibility

Características:
- Detecta funciones/clases sin docstrings
- Verifica formato y estructura
- Sugiere mejoras automáticas
- Genera reportes detallados
"""

import ast
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DocstringIssue:
    """Representa un problema encontrado en un docstring"""

    file_path: str
    line_number: int
    object_type: str  # 'function', 'class', 'method'
    object_name: str
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    description: str
    suggestion: Optional[str] = None


@dataclass
class DocstringReport:
    """Reporte completo de verificación de docstrings"""

    timestamp: str
    total_objects: int
    objects_with_docstrings: int
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues: List[DocstringIssue]
    compliance_score: float


class DocstringChecker:
    """Verificador principal de docstrings"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backend_path = self.project_root / "backend"
        self.issues = []
        self.total_objects = 0
        self.objects_with_docstrings = 0

    def check_project(self) -> DocstringReport:
        """Verificar docstrings en todo el proyecto"""
        print("📝 Verificando estándares de docstrings...")

        # Buscar archivos Python
        python_files = []
        if self.backend_path.exists():
            python_files.extend(self.backend_path.rglob("*.py"))

        # Agregar scripts de infraestructura
        infra_path = self.project_root / "infrastructure" / "scripts"
        if infra_path.exists():
            python_files.extend(infra_path.rglob("*.py"))

        # Filtrar archivos del venv y cache
        python_files = [
            f
            for f in python_files
            if "venv" not in str(f) and "__pycache__" not in str(f)
        ]

        print(f"  📁 Encontrados {len(python_files)} archivos Python")

        for py_file in python_files:
            self._check_file(py_file)

        return self._generate_report()

    def _check_file(self, file_path: Path):
        """Verificar docstrings en un archivo específico"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                return  # Archivo vacío

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    self._check_node_docstring(node, file_path)

        except SyntaxError as e:
            self.issues.append(
                DocstringIssue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=getattr(e, "lineno", 1),
                    object_type="file",
                    object_name=file_path.name,
                    issue_type="syntax_error",
                    severity="error",
                    description=f"Error de sintaxis: {e.msg}",
                    suggestion="Corregir la sintaxis del archivo",
                )
            )
        except Exception as e:
            print(f"    ⚠️  Error procesando {file_path}: {e}")

    def _check_node_docstring(self, node: ast.AST, file_path: Path):
        """Verificar docstring de un nodo específico (función/clase)"""
        self.total_objects += 1

        object_type = "class" if isinstance(node, ast.ClassDef) else "function"
        object_name = node.name
        line_number = node.lineno
        file_rel_path = str(file_path.relative_to(self.project_root))

        # Obtener docstring
        docstring = ast.get_docstring(node)

        if docstring is None:
            # Verificar si es método privado/dunder (menos estricto)
            if object_name.startswith("_"):
                severity = "warning" if object_name.startswith("__") else "info"
                issue_type = "missing_docstring_private"
            else:
                severity = "error"
                issue_type = "missing_docstring"

            suggestion = self._generate_docstring_suggestion(node, object_type)

            self.issues.append(
                DocstringIssue(
                    file_path=file_rel_path,
                    line_number=line_number,
                    object_type=object_type,
                    object_name=object_name,
                    issue_type=issue_type,
                    severity=severity,
                    description=f"Falta docstring para {object_type} '{object_name}'",
                    suggestion=suggestion,
                )
            )
        else:
            self.objects_with_docstrings += 1
            # Verificar calidad del docstring
            self._check_docstring_quality(
                docstring, node, file_rel_path, line_number, object_type, object_name
            )

    def _check_docstring_quality(
        self,
        docstring: str,
        node: ast.AST,
        file_path: str,
        line_number: int,
        object_type: str,
        object_name: str,
    ):
        """Verificar calidad y formato del docstring"""

        # 1. Verificar línea de resumen
        lines = docstring.strip().split("\n")
        if not lines or not lines[0].strip():
            self.issues.append(
                DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    object_type=object_type,
                    object_name=object_name,
                    issue_type="empty_summary",
                    severity="error",
                    description="Docstring no tiene línea de resumen",
                    suggestion="Agregar una línea de resumen descriptiva al inicio",
                )
            )

        # 2. Verificar longitud de línea de resumen
        elif len(lines[0]) > 80:
            self.issues.append(
                DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    object_type=object_type,
                    object_name=object_name,
                    issue_type="summary_too_long",
                    severity="warning",
                    description=f"Línea de resumen muy larga ({len(lines[0])} caracteres)",
                    suggestion="Mantener la línea de resumen bajo 80 caracteres",
                )
            )

        # 3. Verificar que termine con punto
        if not lines[0].rstrip().endswith("."):
            self.issues.append(
                DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    object_type=object_type,
                    object_name=object_name,
                    issue_type="summary_no_period",
                    severity="info",
                    description="Línea de resumen no termina con punto",
                    suggestion="Agregar punto al final de la línea de resumen",
                )
            )

        # 4. Para funciones con parámetros, verificar documentación
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._check_function_docstring(
                docstring, node, file_path, line_number, object_name
            )

    def _check_function_docstring(
        self,
        docstring: str,
        node: ast.FunctionDef,
        file_path: str,
        line_number: int,
        object_name: str,
    ):
        """Verificar docstring específico de función"""

        # Obtener parámetros (excluyendo 'self' y 'cls')
        params = [arg.arg for arg in node.args.args if arg.arg not in ("self", "cls")]

        # Verificar si la función retorna algo
        has_return = self._has_return_statement(node)

        if params and len(docstring.split("\n")) < 3:
            self.issues.append(
                DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    object_type="function",
                    object_name=object_name,
                    issue_type="missing_parameters_doc",
                    severity="warning",
                    description=f"Función con parámetros ({', '.join(params)}) necesita documentación detallada",
                    suggestion="Agregar secciones Parameters y Returns según Google Style",
                )
            )

        # Verificar secciones estándar para funciones complejas
        if len(params) > 2 or has_return:
            docstring_lower = docstring.lower()

            if (
                "parameters" not in docstring_lower
                and "args" not in docstring_lower
                and "param" not in docstring_lower
            ):
                self.issues.append(
                    DocstringIssue(
                        file_path=file_path,
                        line_number=line_number,
                        object_type="function",
                        object_name=object_name,
                        issue_type="missing_parameters_section",
                        severity="info",
                        description="Función compleja sin sección de parámetros",
                        suggestion="Agregar sección 'Parameters:' o 'Args:'",
                    )
                )

            if has_return and "return" not in docstring_lower:
                self.issues.append(
                    DocstringIssue(
                        file_path=file_path,
                        line_number=line_number,
                        object_type="function",
                        object_name=object_name,
                        issue_type="missing_returns_section",
                        severity="info",
                        description="Función con return sin documentar valor de retorno",
                        suggestion="Agregar sección 'Returns:'",
                    )
                )

    def _has_return_statement(self, node: ast.FunctionDef) -> bool:
        """Verificar si la función tiene statements de return con valor"""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value is not None:
                return True
        return False

    def _generate_docstring_suggestion(self, node: ast.AST, object_type: str) -> str:
        """Generar sugerencia de docstring"""
        if object_type == "class":
            return f'''"""
{node.name.replace('_', ' ').title()}.

Esta clase [descripción de funcionalidad].

Attributes:
    [atributo]: [descripción]

Example:
    >>> obj = {node.name}()
    >>> # uso básico
"""'''
        else:  # function
            params = []
            if hasattr(node, "args"):
                params = [
                    arg.arg for arg in node.args.args if arg.arg not in ("self", "cls")
                ]

            params_section = ""
            if params:
                params_section = f"""
Args:
{chr(10).join(f'    {param}: [descripción]' for param in params)}"""

            return f'''"""
{node.name.replace('_', ' ').title()}.

[Descripción detallada de la función].{params_section}

Returns:
    [tipo]: [descripción del valor de retorno]

Example:
    >>> result = {node.name}({', '.join(['[valor]' for _ in params])})
    >>> # resultado esperado
"""'''

    def _generate_report(self) -> DocstringReport:
        """Generar reporte final"""
        issues_by_severity = {"error": 0, "warning": 0, "info": 0}
        for issue in self.issues:
            issues_by_severity[issue.severity] += 1

        # Calcular score de compliance
        if self.total_objects == 0:
            compliance_score = 100.0
        else:
            # Penalizar errores más que warnings
            error_penalty = issues_by_severity["error"] * 10
            warning_penalty = issues_by_severity["warning"] * 5
            info_penalty = issues_by_severity["info"] * 1

            total_penalty = error_penalty + warning_penalty + info_penalty
            max_penalty = self.total_objects * 10  # Máximo si todo fueran errores

            compliance_score = max(0, 100 - (total_penalty / max(max_penalty, 1) * 100))

        return DocstringReport(
            timestamp=datetime.now().isoformat(),
            total_objects=self.total_objects,
            objects_with_docstrings=self.objects_with_docstrings,
            total_issues=len(self.issues),
            issues_by_severity=issues_by_severity,
            issues=self.issues,
            compliance_score=compliance_score,
        )

    def generate_console_report(self, report: DocstringReport) -> str:
        """Generar reporte para consola"""
        output = []

        output.append("📝 REPORTE DE DOCSTRINGS")
        output.append("=" * 50)
        output.append(f"📅 Timestamp: {report.timestamp}")
        output.append(f"📊 Objetos analizados: {report.total_objects}")
        output.append(f"✅ Con docstrings: {report.objects_with_docstrings}")
        output.append(f"📈 Compliance: {report.compliance_score:.1f}%")
        output.append("")

        output.append("📋 RESUMEN DE ISSUES")
        output.append("-" * 30)
        output.append(f"🔴 Errores: {report.issues_by_severity['error']}")
        output.append(f"🟡 Warnings: {report.issues_by_severity['warning']}")
        output.append(f"🔵 Info: {report.issues_by_severity['info']}")
        output.append("")

        if report.issues:
            output.append("🔍 ISSUES DETALLADOS")
            output.append("-" * 30)

            # Agrupar por archivo
            issues_by_file = {}
            for issue in report.issues:
                if issue.file_path not in issues_by_file:
                    issues_by_file[issue.file_path] = []
                issues_by_file[issue.file_path].append(issue)

            for file_path, issues in issues_by_file.items():
                output.append(f"📁 {file_path}")

                for issue in issues[:5]:  # Limitar a 5 por archivo
                    severity_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}[
                        issue.severity
                    ]
                    output.append(
                        f"  {severity_icon} L{issue.line_number}: {issue.object_name} - {issue.description}"
                    )

                    if issue.suggestion and len(output) < 50:  # Limitar sugerencias
                        suggestion_lines = issue.suggestion.split("\n")[:3]
                        for line in suggestion_lines:
                            if line.strip():
                                output.append(f"      💡 {line.strip()}")

                if len(issues) > 5:
                    output.append(f"    ... y {len(issues) - 5} más")
                output.append("")
        else:
            output.append("🎉 ¡No se encontraron issues!")

        return "\n".join(output)

    def generate_json_report(self, report: DocstringReport) -> str:
        """Generar reporte en formato JSON"""
        return json.dumps(asdict(report), indent=2, default=str)


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Verificador de Docstrings")
    parser.add_argument(
        "--format",
        choices=["console", "json"],
        default="console",
        help="Formato de salida",
    )
    parser.add_argument("--output", "-o", help="Archivo de salida")

    args = parser.parse_args()

    try:
        checker = DocstringChecker()
        report = checker.check_project()

        if args.format == "json":
            output = checker.generate_json_report(report)
        else:
            output = checker.generate_console_report(report)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"📄 Reporte guardado en: {args.output}")
        else:
            print(output)

        # Exit code basado en compliance
        if report.compliance_score >= 90:
            sys.exit(0)
        elif report.compliance_score >= 70:
            sys.exit(1)
        else:
            sys.exit(2)

    except Exception as e:
        print(f"❌ Error durante verificación: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
