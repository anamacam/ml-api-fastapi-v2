#!/usr/bin/env python3
"""
📄 Verificador de Estándares de Markdown - ML API FastAPI v2
============================================================

Verifica que los archivos Markdown cumplan con:
- CommonMark specification
- Markdownlint rules
- Consistencia de formato
- Enlaces válidos
- Estructura de documentos

Características:
- Integración con markdownlint-cli
- Verificación de enlaces
- Análisis de estructura
- Reportes detallados
"""

import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional
from collections import Counter


@dataclass
class MarkdownIssue:
    """Representa un problema encontrado en un archivo Markdown."""

    file_path: str
    line_number: int
    rule_id: str
    severity: str  # 'error', 'warning', 'info'
    description: str
    suggestion: Optional[str] = None


@dataclass
class MarkdownReport:
    """Reporte completo de verificación de Markdown."""

    timestamp: str
    total_files: int
    files_with_issues: int
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_rule: Dict[str, int]
    issues: List[MarkdownIssue]
    compliance_score: float


class MarkdownChecker:
    """Verificador principal de estándares Markdown."""

    def __init__(self, project_root: str = "."):
        self.project_root = pathlib.Path(project_root)
        self.issues = []
        self.total_files = 0
        self.files_with_issues = 0

        # Reglas y sus descripciones
        self.rule_descriptions = {
            "MD001": "Heading levels should only increment by one level at a time",
            "MD003": "Heading style should be consistent",
            "MD004": "Unordered list style should be consistent",
            "MD005": "Inconsistent indentation for list items at the same level",
            "MD007": "Unordered list indentation should be consistent",
            "MD009": "Trailing spaces are not allowed",
            "MD010": "Hard tabs are not allowed",
            "MD011": "Reversed link syntax",
            "MD012": "Multiple consecutive blank lines are not allowed",
            "MD013": "Line length should not exceed specified limit",
            "MD014": "Dollar signs used before commands without showing output",
            "MD018": "No space after hash on atx style heading",
            "MD019": "Multiple spaces after hash on atx style heading",
            "MD020": "No space inside hashes on closed atx style heading",
            "MD021": "Multiple spaces inside hashes on closed atx style heading",
            "MD022": "Headings should be surrounded by blank lines",
            "MD023": "Headings must start at the beginning of the line",
            "MD024": "Multiple headings with the same content",
            "MD025": "Multiple top level headings in the same document",
            "MD026": "Trailing punctuation in heading",
            "MD027": "Multiple spaces after blockquote symbol",
            "MD028": "Blank line inside blockquote",
            "MD029": "Ordered list item prefix should be consistent",
            "MD030": "Spaces after list markers should be consistent",
            "MD031": "Fenced code blocks should be surrounded by blank lines",
            "MD032": "Lists should be surrounded by blank lines",
            "MD033": "Inline HTML is not allowed",
            "MD034": "Bare URL used instead of link syntax",
            "MD035": "Horizontal rule style should be consistent",
            "MD036": "Emphasis used instead of a heading",
            "MD037": "Spaces inside emphasis markers",
            "MD038": "Spaces inside code span elements",
            "MD039": "Spaces inside link text",
            "MD040": "Fenced code blocks should have a language specified",
            "MD041": "First line in file should be a top level heading",
            "MD042": "No empty links",
            "MD043": "Required heading structure",
            "MD044": "Proper names should have the correct capitalization",
            "MD045": "Images should have alternate text (alt text)",
            "MD046": "Code block style should be consistent",
            "MD047": "Files should end with a single newline character",
            "MD048": "Code fence style should be consistent",
            "MD049": "Emphasis style should be consistent",
            "MD050": "Strong style should be consistent",
            "MD051": "Link fragments should be valid",
            "MD052": "Reference links and images should use a label that is defined",
            "MD053": "Link and image reference definitions should be needed",
        }

    def check_project(self) -> MarkdownReport:
        """Verificar archivos Markdown en todo el proyecto."""
        print("📄 Verificando estándares de Markdown...")

        # Buscar archivos Markdown
        md_files = list(self.project_root.rglob("*.md"))

        # Filtrar archivos del venv y node_modules
        md_files = [
            f for f in md_files if "venv" not in str(f) and "node_modules" not in str(f)
        ]

        self.total_files = len(md_files)
        print(f"  📁 Encontrados {self.total_files} archivos Markdown")

        if self.total_files == 0:
            return self._generate_report()

        # Ejecutar markdownlint
        self._run_markdownlint(md_files)

        # Verificaciones adicionales
        for md_file in md_files:
            self._check_file_structure(md_file)

        return self._generate_report()

    def _run_markdownlint(self, md_files: List[pathlib.Path]):
        """Ejecutar markdownlint en los archivos."""
        try:
            # Preparar comando
            cmd = ["markdownlint", "--json"] + [str(f) for f in md_files]

            # Ejecutar markdownlint
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                print("  ✅ No se encontraron issues con markdownlint")
                return

            # Parsear salida JSON si está disponible
            if result.stdout:
                try:
                    lint_results = json.loads(result.stdout)
                    self._parse_markdownlint_results(lint_results)
                except json.JSONDecodeError:
                    # Fallback: parsear salida de texto
                    self._parse_markdownlint_text(result.stdout)
            else:
                # Parsear stderr como texto
                self._parse_markdownlint_text(result.stderr)

        except FileNotFoundError:
            print("  ⚠️  markdownlint no está instalado. Instalando...")
            try:
                subprocess.run(
                    ["npm", "install", "-g", "markdownlint-cli"],
                    check=True,
                    capture_output=True,
                )
                print("  ✅ markdownlint instalado. Reintentando...")
                self._run_markdownlint(md_files)
            except subprocess.CalledProcessError:
                print("  ❌ No se pudo instalar markdownlint")
        except Exception as e:
            print(f"  ⚠️  Error ejecutando markdownlint: {e}")

    def _parse_markdownlint_results(self, results: List[Dict]):
        """Parsear resultados JSON de markdownlint."""
        files_with_issues = set()

        for file_result in results:
            file_path = file_result.get("fileName", "")
            rel_path = str(pathlib.Path(file_path).relative_to(self.project_root))

            for issue in file_result.get("issues", []):
                files_with_issues.add(rel_path)

                rule_names = issue.get("ruleNames", [])
                rule_id = rule_names[0] if rule_names else "Unknown"
                _ = rule_names[1] if len(rule_names) > 1 else rule_id

                self.issues.append(
                    MarkdownIssue(
                        file_path=rel_path,
                        line_number=issue.get("lineNumber", 0),
                        rule_id=rule_id,
                        severity="error",  # markdownlint solo reporta errores
                        description=issue.get(
                            "ruleDescription",
                            self.rule_descriptions.get(rule_id, "Unknown rule"),
                        ),
                        suggestion=self._get_rule_suggestion(rule_id),
                    )
                )

        self.files_with_issues = len(files_with_issues)

    def _parse_markdownlint_text(self, output: str):
        """Parsear salida de texto de markdownlint."""
        files_with_issues = set()

        for line in output.strip().split("\n"):
            if not line.strip():
                continue

            # Formato: file:line rule/alias description
            parts = line.split(":", 2)
            if len(parts) < 3:
                continue

            file_path = parts[0]
            try:
                line_number = int(parts[1])
            except ValueError:
                line_number = 0

            # Extraer regla y descripción
            rule_desc = parts[2].strip()
            rule_parts = rule_desc.split(" ", 1)
            rule_id = rule_parts[0] if rule_parts else "Unknown"
            description = rule_parts[1] if len(rule_parts) > 1 else rule_desc

            try:
                rel_path = str(pathlib.Path(file_path).relative_to(self.project_root))
            except ValueError:
                rel_path = file_path

            files_with_issues.add(rel_path)

            self.issues.append(
                MarkdownIssue(
                    file_path=rel_path,
                    line_number=line_number,
                    rule_id=rule_id,
                    severity="error",
                    description=description,
                    suggestion=self._get_rule_suggestion(rule_id),
                )
            )

        self.files_with_issues = len(files_with_issues)

    def _get_rule_suggestion(self, rule_id: str) -> Optional[str]:
        """Obtener sugerencia para una regla específica."""
        suggestions = {
            "MD034": "Usar formato de enlace: [texto](URL) en lugar de URL directa",
            "MD036": "Usar encabezados (# ## ###) en lugar de texto en negrita para títulos",
            "MD040": "Especificar lenguaje en bloques de código: ```python o ```bash",
            "MD013": "Dividir líneas largas o ajustar configuración de longitud",
            "MD033": "Evitar HTML inline, usar sintaxis Markdown equivalente",
            "MD041": "Comenzar documento con encabezado de nivel 1 (#)",
            "MD022": "Agregar líneas en blanco antes y después de encabezados",
            "MD032": "Agregar líneas en blanco antes y después de listas",
            "MD031": "Agregar líneas en blanco antes y después de bloques de código",
        }
        return suggestions.get(rule_id)

    def _check_file_structure(self, file_path: pathlib.Path):
        """Verificar estructura adicional del archivo."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Verificar título principal
            if not lines or not lines[0].startswith("# "):
                self.issues.append(
                    MarkdownIssue(
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=1,
                        rule_id="structure-title",
                        severity="warning",
                        description="El archivo no comienza con un título principal (H1)",
                        suggestion="Añade un título descriptivo como '# Mi Título' al inicio",
                    )
                )

            # Verificar consistencia en subtítulos (usar ## y no ### para nivel 2)
            for i, line in enumerate(lines, 1):
                if line.strip().startswith("### "):
                    self.issues.append(
                        MarkdownIssue(
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=i,
                            rule_id="structure-subtitle",
                            severity="info",
                            description="Se encontró un subtítulo de nivel 3 (###). ¿Debería ser nivel 2 (##)?",
                            suggestion="Considera usar '##' para subtítulos principales.",
                        )
                    )

            # Verificar saltos de línea antes de listas
            self._check_whitespace_around_lists(lines, file_path)

            # Verificar enlaces internos
            self._check_internal_links(
                [line.strip() for line in lines], str(file_path), file_path
            )

        except Exception as e:
            self.issues.append(
                MarkdownIssue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=1,
                    rule_id="file-read-error",
                    severity="error",
                    description=f"Error al procesar estructura: {e}",
                )
            )

    def _check_whitespace_around_lists(self, lines: List[str], file_path: pathlib.Path):
        """Verifica que las listas estén rodeadas por líneas en blanco."""
        in_list = False
        try:
            for i, line in enumerate(lines):
                is_list_item = line.strip().startswith(("- ", "* ", "+ ")) or re.match(
                    r"^\d+\.\s", line.strip()
                )
                if is_list_item and not in_list:
                    # Comienzo de una lista
                    if i > 0 and lines[i - 1].strip() != "":
                        self.issues.append(
                            MarkdownIssue(
                                file_path=str(file_path),
                                line_number=i,
                                rule_id="CUSTOM-W001",
                                severity="warning",
                                description="La lista no está precedida por una línea en blanco.",
                                suggestion="Añadir línea en blanco antes de la lista.",
                            )
                        )
                elif not is_list_item and in_list:
                    # Fin de una lista
                    if lines[i].strip() != "":
                        self.issues.append(
                            MarkdownIssue(
                                file_path=str(file_path),
                                line_number=i,
                                rule_id="CUSTOM-W002",
                                severity="warning",
                                description="La lista no está seguida de una línea en blanco.",
                                suggestion="Añadir línea en blanco después de la lista.",
                            )
                        )
                in_list = is_list_item
        except Exception as e:
            print(f"  ⚠️  Error en _check_whitespace_around_lists: {e}")

    def _check_internal_links(
        self, lines: List[str], file_path: str, current_file: pathlib.Path
    ):
        """Verifica que los enlaces internos a archivos .md sean válidos."""
        link_regex = re.compile(r"\[([^\]]+)\]\(([^)]+\.md(?:#[\w-]+)?)\)")
        for i, line in enumerate(lines):
            for match in link_regex.finditer(line):
                link_target = match.group(2).split("#")[0]
                target_path = (
                    current_file.parent / pathlib.Path(link_target)
                ).resolve()

                if not target_path.exists():
                    self.issues.append(
                        MarkdownIssue(
                            file_path=file_path,
                            line_number=i + 1,
                            rule_id="CUSTOM-L001",
                            severity="error",
                            description=f"Enlace interno roto a '{link_target}'.",
                            suggestion=f"Verifica la ruta del enlace en la línea {i + 1}.",
                        )
                    )

    def _generate_report(self) -> MarkdownReport:
        """Genera el reporte final."""
        issues_by_rule = Counter(issue.rule_id for issue in self.issues)
        issues_by_severity = Counter(issue.severity for issue in self.issues)
        compliance = self.calculate_compliance(issues_by_severity)

        return MarkdownReport(
            timestamp=datetime.utcnow().isoformat(),
            total_files=self.total_files,
            files_with_issues=len({issue.file_path for issue in self.issues}),
            total_issues=len(self.issues),
            issues_by_severity=dict(sorted(issues_by_severity.items())),
            issues_by_rule=dict(sorted(issues_by_rule.items())),
            issues=self.issues,
            compliance_score=compliance,
        )

    def calculate_compliance(self, issues_by_severity: Dict[str, int]) -> float:
        """Calcula el puntaje de cumplimiento."""
        # Penalizar errores más que warnings
        error_penalty = issues_by_severity.get("error", 0) * 5
        warning_penalty = issues_by_severity.get("warning", 0) * 1
        total_penalty = error_penalty + warning_penalty

        # Normalizar basado en el número de archivos
        max_penalty = (
            self.total_files * 10
        )  # Max 10 'puntos de penalización' por archivo
        if max_penalty == 0:
            return 100.0

        compliance_score = max(0.0, 100.0 - (total_penalty / max_penalty * 100.0))
        return compliance_score

    def generate_console_report(self, report: MarkdownReport) -> str:
        """Genera un reporte legible para la consola."""
        report_lines = []
        report_lines.append(f"📄 Reporte de Calidad de Markdown ({report.timestamp})")
        report_lines.append("=" * 60)
        report_lines.append(
            f"📊 Resumen: {report.total_files} archivos analizados, "
            f"{report.files_with_issues} con issues."
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
                    f"{issue.line_number} ({issue.rule_id}) - {issue.description}"
                )
        else:
            report_lines.append("✅ ¡Excelente! No se encontraron issues.")

        return "\n".join(report_lines)

    def generate_json_report(self, report: MarkdownReport) -> str:
        """Genera un reporte en formato JSON."""
        # El reporte ya contiene los issues como diccionarios
        report_dict = {
            "timestamp": report.timestamp,
            "summary": {
                "total_files": report.total_files,
                "files_with_issues": report.files_with_issues,
                "total_issues": report.total_issues,
                "compliance_score": report.compliance_score,
                "issues_by_severity": report.issues_by_severity,
                "issues_by_rule": report.issues_by_rule,
            },
            "issues": [asdict(issue) for issue in report.issues],
        }
        return json.dumps(report_dict, indent=4)


def main():
    """Punto de entrada principal para ejecutar el verificador."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Verificador de Estándares de Markdown para el proyecto."
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

    checker = MarkdownChecker()
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
