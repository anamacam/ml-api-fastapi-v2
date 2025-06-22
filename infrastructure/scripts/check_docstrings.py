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
import pathlib
import sys
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import re
import argparse

NodeWithDocstring = Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
FunctionNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]


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
        self.project_root = pathlib.Path(project_root)
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

    def _check_file(self, file_path: pathlib.Path):
        """Verificar docstrings en un archivo específico"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                return  # Archivo vacío

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
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

    def _check_node_docstring(self, node: NodeWithDocstring, file_path: pathlib.Path):
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
                docstring, node, file_rel_path, object_type, object_name
            )

    def _check_docstring_quality(
        self,
        docstring: str,
        node: NodeWithDocstring,
        file_path: str,
        object_type: str,
        object_name: str,
    ):
        """Verificar calidad y formato del docstring"""
        line_number = node.lineno
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
        elif len(lines[0]) > 88:
            self.issues.append(
                DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    object_type=object_type,
                    object_name=object_name,
                    issue_type="summary_too_long",
                    severity="warning",
                    description=f"Línea de resumen excede los 88 caracteres ({len(lines[0])})",
                    suggestion="Acortar la línea de resumen.",
                )
            )

        # 3. Verificar si hay línea en blanco después del resumen
        if len(lines) > 1 and lines[1].strip() != "":
            self.issues.append(
                DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    object_type=object_type,
                    object_name=object_name,
                    issue_type="no_blank_line_after_summary",
                    severity="warning",
                    description="Falta una línea en blanco después del resumen del docstring.",
                    suggestion="Añadir una línea en blanco.",
                )
            )

        # 4. Verificaciones específicas para funciones
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._check_function_docstring(
                docstring, node, file_path, line_number, object_name
            )

    def _check_function_docstring(
        self,
        docstring: str,
        node: FunctionNode,
        file_path: str,
        line_number: int,
        object_name: str,
    ):
        """Analizar las secciones específicas de un docstring de función."""
        args_re = re.compile(r"Args:\s*\n")
        returns_re = re.compile(r"Returns:\s*\n")

        # Verificar sección de argumentos
        if not args_re.search(docstring) and node.args.args:
            self.issues.append(
                DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    object_type="function",
                    object_name=object_name,
                    issue_type="missing_args_section",
                    severity="warning",
                    description="Falta la sección 'Args' en el docstring.",
                    suggestion="Añadir sección 'Args:' con descripción de parámetros.",
                )
            )

        if not returns_re.search(docstring) and self._has_return_statement(node):
            self.issues.append(
                DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    object_type="function",
                    object_name=object_name,
                    issue_type="missing_returns_section",
                    severity="warning",
                    description="La función tiene 'return' pero falta la sección 'Returns:'.",
                    suggestion="Añadir sección 'Returns:' con descripción del valor de retorno.",
                )
            )

    def _has_return_statement(self, node: FunctionNode) -> bool:
        """Verifica si un nodo de función tiene una declaración de retorno explícita."""
        return any(isinstance(child, ast.Return) for child in ast.walk(node))

    def _generate_docstring_suggestion(
        self, node: NodeWithDocstring, object_type: str
    ) -> str:
        """Genera una sugerencia de plantilla de docstring."""
        if object_type == "function":
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                params = [
                    arg.arg for arg in node.args.args if arg.arg not in ("self", "cls")
                ]
                has_return = self._has_return_statement(node)

                suggestion = '"""One-line summary of the function.\\n\\n'
                if params:
                    suggestion += "Args:\\n"
                    for param in params:
                        suggestion += f"    {param} (type): Description of {param}.\\n"
                if has_return:
                    suggestion += "\\nReturns:\\n    type: Description of return value.\\n"
                suggestion += '"""'
                return suggestion
        # class
        return '"""Brief description of the class.\\n\\nAttributes:\\n    attr (type): Description.\\n"""'

    def _generate_report(self) -> DocstringReport:
        """Genera el reporte final de la verificación."""
        issues_by_severity = {}
        for issue in self.issues:
            issues_by_severity[issue.severity] = (
                issues_by_severity.get(issue.severity, 0) + 1
            )

        total_issues = len(self.issues)
        if self.total_objects > 0:
            compliance = (self.objects_with_docstrings / self.total_objects) * 100
        else:
            compliance = 100.0

        return DocstringReport(
            timestamp=datetime.utcnow().isoformat(),
            total_objects=self.total_objects,
            objects_with_docstrings=self.objects_with_docstrings,
            total_issues=total_issues,
            issues_by_severity=dict(issues_by_severity),
            issues=self.issues,
            compliance_score=compliance,
        )

    def generate_console_report(self, report: DocstringReport) -> str:
        """Genera un reporte legible para la consola."""
        report_lines = []
        report_lines.append(
            f"📄 Reporte de Calidad de Docstrings ({report.timestamp})"
        )
        report_lines.append("=" * 60)
        report_lines.append(
            f"📊 Resumen: {report.total_objects} objetos analizados, "
            f"{report.objects_with_docstrings} con docstrings."
        )
        report_lines.append(
            f"🎯 Puntaje de Cumplimiento: {report.compliance_score:.2f}%"
        )
        report_lines.append(f"🚨 Total de Issues: {report.total_issues}")
        for severity, count in report.issues_by_severity.items():
            report_lines.append(f"  - {severity.capitalize()}: {count}")
        report_lines.append("-" * 60)

        if report.issues:
            report_lines.append("🔍 Detalles de los Issues:")
            sorted_issues = sorted(report.issues, key=lambda x: x.file_path)
            for issue in sorted_issues:
                report_lines.append(
                    f"  - [{issue.severity.upper()}] {issue.file_path}:"
                    f"{issue.line_number} ({issue.object_name}) - {issue.description}"
                )
        else:
            report_lines.append("✅ ¡Excelente! No se encontraron issues.")

        return "\\n".join(report_lines)

    def generate_json_report(self, report: DocstringReport) -> str:
        """Genera un reporte en formato JSON."""
        return json.dumps(asdict(report), indent=4)


def main():
    """Punto de entrada principal para ejecutar el verificador."""
    parser = argparse.ArgumentParser(
        description="Verificador de Estándares de Docstrings para el proyecto."
    )
    parser.add_argument(
        "--format",
        choices=["console", "json"],
        default="console",
        help="Formato del reporte de salida.",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Archivo para guardar el reporte. Si no se especifica, se imprime en consola.",
    )
    args = parser.parse_args()

    checker = DocstringChecker()
    report = checker.check_project()

    if args.format == "json":
        output = checker.generate_json_report(report)
    else:
        output = checker.generate_console_report(report)

    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"📄 Reporte guardado en {args.output_file}")
    else:
        print(output)

    # Salir con código de error si hay issues de severidad 'error'
    if any(issue.severity == "error" for issue in report.issues):
        sys.exit(1)


if __name__ == "__main__":
    main()
