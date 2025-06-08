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

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class MarkdownIssue:
    """Representa un problema encontrado en un archivo Markdown."""
    file_path: str
    line_number: int
    rule_id: str
    rule_name: str
    severity: str  # 'error', 'warning'
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
        self.project_root = Path(project_root)
        self.issues = []
        self.total_files = 0
        self.files_with_issues = 0

        # Reglas y sus descripciones
        self.rule_descriptions = {
            'MD001': 'Heading levels should only increment by one level at a time',
            'MD003': 'Heading style should be consistent',
            'MD004': 'Unordered list style should be consistent',
            'MD005': 'Inconsistent indentation for list items at the same level',
            'MD007': 'Unordered list indentation should be consistent',
            'MD009': 'Trailing spaces are not allowed',
            'MD010': 'Hard tabs are not allowed',
            'MD011': 'Reversed link syntax',
            'MD012': 'Multiple consecutive blank lines are not allowed',
            'MD013': 'Line length should not exceed specified limit',
            'MD014': 'Dollar signs used before commands without showing output',
            'MD018': 'No space after hash on atx style heading',
            'MD019': 'Multiple spaces after hash on atx style heading',
            'MD020': 'No space inside hashes on closed atx style heading',
            'MD021': 'Multiple spaces inside hashes on closed atx style heading',
            'MD022': 'Headings should be surrounded by blank lines',
            'MD023': 'Headings must start at the beginning of the line',
            'MD024': 'Multiple headings with the same content',
            'MD025': 'Multiple top level headings in the same document',
            'MD026': 'Trailing punctuation in heading',
            'MD027': 'Multiple spaces after blockquote symbol',
            'MD028': 'Blank line inside blockquote',
            'MD029': 'Ordered list item prefix should be consistent',
            'MD030': 'Spaces after list markers should be consistent',
            'MD031': 'Fenced code blocks should be surrounded by blank lines',
            'MD032': 'Lists should be surrounded by blank lines',
            'MD033': 'Inline HTML is not allowed',
            'MD034': 'Bare URL used instead of link syntax',
            'MD035': 'Horizontal rule style should be consistent',
            'MD036': 'Emphasis used instead of a heading',
            'MD037': 'Spaces inside emphasis markers',
            'MD038': 'Spaces inside code span elements',
            'MD039': 'Spaces inside link text',
            'MD040': 'Fenced code blocks should have a language specified',
            'MD041': 'First line in file should be a top level heading',
            'MD042': 'No empty links',
            'MD043': 'Required heading structure',
            'MD044': 'Proper names should have the correct capitalization',
            'MD045': 'Images should have alternate text (alt text)',
            'MD046': 'Code block style should be consistent',
            'MD047': 'Files should end with a single newline character',
            'MD048': 'Code fence style should be consistent',
            'MD049': 'Emphasis style should be consistent',
            'MD050': 'Strong style should be consistent',
            'MD051': 'Link fragments should be valid',
            'MD052': 'Reference links and images should use a label that is defined',
            'MD053': 'Link and image reference definitions should be needed'
        }

    def check_project(self) -> MarkdownReport:
        """Verificar archivos Markdown en todo el proyecto."""
        print("📄 Verificando estándares de Markdown...")

        # Buscar archivos Markdown
        md_files = list(self.project_root.rglob("*.md"))

        # Filtrar archivos del venv y node_modules
        md_files = [f for f in md_files
                   if "venv" not in str(f) and "node_modules" not in str(f)]

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

    def _run_markdownlint(self, md_files: List[Path]):
        """Ejecutar markdownlint en los archivos."""
        try:
            # Preparar comando
            cmd = ["markdownlint", "--json"] + [str(f) for f in md_files]

            # Ejecutar markdownlint
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
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
                subprocess.run(["npm", "install", "-g", "markdownlint-cli"],
                             check=True, capture_output=True)
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
            file_path = file_result.get('fileName', '')
            rel_path = str(Path(file_path).relative_to(self.project_root))

            for issue in file_result.get('issues', []):
                files_with_issues.add(rel_path)

                rule_names = issue.get('ruleNames', [])
                rule_id = rule_names[0] if rule_names else 'Unknown'
                rule_name = rule_names[1] if len(rule_names) > 1 else rule_id

                self.issues.append(MarkdownIssue(
                    file_path=rel_path,
                    line_number=issue.get('lineNumber', 0),
                    rule_id=rule_id,
                    rule_name=rule_name,
                    severity='error',  # markdownlint solo reporta errores
                    description=issue.get('ruleDescription', self.rule_descriptions.get(rule_id, 'Unknown rule')),
                    suggestion=self._get_rule_suggestion(rule_id)
                ))

        self.files_with_issues = len(files_with_issues)

    def _parse_markdownlint_text(self, output: str):
        """Parsear salida de texto de markdownlint."""
        files_with_issues = set()

        for line in output.strip().split('\n'):
            if not line.strip():
                continue

            # Formato: file:line rule/alias description
            parts = line.split(':', 2)
            if len(parts) < 3:
                continue

            file_path = parts[0]
            try:
                line_number = int(parts[1])
            except ValueError:
                line_number = 0

            # Extraer regla y descripción
            rule_desc = parts[2].strip()
            rule_parts = rule_desc.split(' ', 1)
            rule_id = rule_parts[0] if rule_parts else 'Unknown'
            description = rule_parts[1] if len(rule_parts) > 1 else rule_desc

            try:
                rel_path = str(Path(file_path).relative_to(self.project_root))
            except ValueError:
                rel_path = file_path

            files_with_issues.add(rel_path)

            self.issues.append(MarkdownIssue(
                file_path=rel_path,
                line_number=line_number,
                rule_id=rule_id,
                rule_name=rule_id,
                severity='error',
                description=description,
                suggestion=self._get_rule_suggestion(rule_id)
            ))

        self.files_with_issues = len(files_with_issues)

    def _get_rule_suggestion(self, rule_id: str) -> Optional[str]:
        """Obtener sugerencia para una regla específica."""
        suggestions = {
            'MD034': 'Usar formato de enlace: [texto](URL) en lugar de URL directa',
            'MD036': 'Usar encabezados (# ## ###) en lugar de texto en negrita para títulos',
            'MD040': 'Especificar lenguaje en bloques de código: ```python o ```bash',
            'MD013': 'Dividir líneas largas o ajustar configuración de longitud',
            'MD033': 'Evitar HTML inline, usar sintaxis Markdown equivalente',
            'MD041': 'Comenzar documento con encabezado de nivel 1 (#)',
            'MD022': 'Agregar líneas en blanco antes y después de encabezados',
            'MD032': 'Agregar líneas en blanco antes y después de listas',
            'MD031': 'Agregar líneas en blanco antes y después de bloques de código'
        }
        return suggestions.get(rule_id)

    def _check_file_structure(self, file_path: Path):
        """Verificar estructura adicional del archivo."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            rel_path = str(file_path.relative_to(self.project_root))

            # Verificar que README tenga estructura básica
            if file_path.name.lower() == 'readme.md':
                self._check_readme_structure(lines, rel_path)

            # Verificar enlaces internos (básico)
            self._check_internal_links(lines, rel_path, file_path)

        except Exception as e:
            print(f"    ⚠️  Error verificando {file_path}: {e}")

    def _check_readme_structure(self, lines: List[str], file_path: str):
        """Verificar estructura básica de README."""
        has_description = False
        has_installation = False
        has_usage = False

        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['descripción', 'description', 'about']):
                has_description = True
            elif any(word in line_lower for word in ['instalación', 'installation', 'setup', 'inicio']):
                has_installation = True
            elif any(word in line_lower for word in ['uso', 'usage', 'getting started']):
                has_usage = True

        if not has_description:
            self.issues.append(MarkdownIssue(
                file_path=file_path,
                line_number=1,
                rule_id='CUSTOM001',
                rule_name='missing-description',
                severity='warning',
                description='README debería incluir sección de descripción',
                suggestion='Agregar sección que describa el propósito del proyecto'
            ))

    def _check_internal_links(self, lines: List[str], file_path: str, current_file: Path):
        """Verificar enlaces internos básicos."""
        import re

        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        for i, line in enumerate(lines, 1):
            matches = re.findall(link_pattern, line)

            for text, url in matches:
                # Solo verificar enlaces relativos
                if url.startswith(('http://', 'https://', 'mailto:', '#')):
                    continue

                # Verificar si el archivo existe
                target_path = current_file.parent / url
                if not target_path.exists():
                    self.issues.append(MarkdownIssue(
                        file_path=file_path,
                        line_number=i,
                        rule_id='CUSTOM002',
                        rule_name='broken-internal-link',
                        severity='warning',
                        description=f'Enlace interno roto: {url}',
                        suggestion='Verificar que el archivo/ruta existe'
                    ))

    def _generate_report(self) -> MarkdownReport:
        """Generar reporte final."""
        issues_by_severity = {'error': 0, 'warning': 0}
        issues_by_rule = {}

        for issue in self.issues:
            issues_by_severity[issue.severity] += 1
            issues_by_rule[issue.rule_id] = issues_by_rule.get(issue.rule_id, 0) + 1

        # Calcular score de compliance
        if self.total_files == 0:
            compliance_score = 100.0
        else:
            # Penalizar errores más que warnings
            error_penalty = issues_by_severity['error'] * 5
            warning_penalty = issues_by_severity['warning'] * 2

            total_penalty = error_penalty + warning_penalty
            max_penalty = self.total_files * 20  # Máximo si todo fueran errores

            compliance_score = max(0, 100 - (total_penalty / max(max_penalty, 1) * 100))

        return MarkdownReport(
            timestamp=datetime.now().isoformat(),
            total_files=self.total_files,
            files_with_issues=self.files_with_issues,
            total_issues=len(self.issues),
            issues_by_severity=issues_by_severity,
            issues_by_rule=issues_by_rule,
            issues=self.issues,
            compliance_score=compliance_score
        )

    def generate_console_report(self, report: MarkdownReport) -> str:
        """Generar reporte para consola."""
        output = []

        output.append("📄 REPORTE DE MARKDOWN")
        output.append("=" * 50)
        output.append(f"📅 Timestamp: {report.timestamp}")
        output.append(f"📁 Archivos analizados: {report.total_files}")
        output.append(f"⚠️  Archivos con issues: {report.files_with_issues}")
        output.append(f"📈 Compliance: {report.compliance_score:.1f}%")
        output.append("")

        output.append("📋 RESUMEN DE ISSUES")
        output.append("-" * 30)
        output.append(f"🔴 Errores: {report.issues_by_severity['error']}")
        output.append(f"🟡 Warnings: {report.issues_by_severity['warning']}")
        output.append("")

        if report.issues_by_rule:
            output.append("📊 TOP REGLAS VIOLADAS")
            output.append("-" * 30)
            sorted_rules = sorted(report.issues_by_rule.items(),
                                key=lambda x: x[1], reverse=True)
            for rule, count in sorted_rules[:5]:
                output.append(f"  {rule}: {count} issues")
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
                    severity_icon = {'error': '🔴', 'warning': '🟡'}[issue.severity]
                    output.append(f"  {severity_icon} L{issue.line_number}: {issue.rule_id} - {issue.description}")

                    if issue.suggestion:
                        output.append(f"      💡 {issue.suggestion}")

                if len(issues) > 5:
                    output.append(f"    ... y {len(issues) - 5} más")
                output.append("")
        else:
            output.append("🎉 ¡No se encontraron issues!")

        return "\n".join(output)

    def generate_json_report(self, report: MarkdownReport) -> str:
        """Generar reporte en formato JSON."""
        return json.dumps(asdict(report), indent=2, default=str)


def main():
    """Función principal del verificador de Markdown."""
    import argparse

    parser = argparse.ArgumentParser(description="Verificador de Estándares Markdown")
    parser.add_argument("--format", choices=["console", "json"], default="console",
                       help="Formato de salida")
    parser.add_argument("--output", "-o", help="Archivo de salida")

    args = parser.parse_args()

    try:
        checker = MarkdownChecker()
        report = checker.check_project()

        if args.format == "json":
            output = checker.generate_json_report(report)
        else:
            output = checker.generate_console_report(report)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
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
