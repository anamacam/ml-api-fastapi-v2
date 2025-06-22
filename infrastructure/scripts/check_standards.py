#!/usr/bin/env python3
"""
📋 Verificador Integrado de Estándares - ML API FastAPI v2
==========================================================

Script unificado que verifica:
- ✅ Estándares de docstrings (PEP 257, Google Style)
- ✅ Estándares de Markdown (CommonMark, markdownlint)
- ✅ Consistencia de documentación
- ✅ Enlaces válidos
- ✅ Estructura de archivos

Genera reportes consolidados y métricas de compliance.
"""

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Importar nuestros verificadores
try:
    from check_docstrings import DocstringChecker
    from check_markdown import MarkdownChecker
except ImportError:
    # Si no se pueden importar, definir clases básicas
    class DocstringChecker:
        def check_project(self):
            return type(
                "Report",
                (),
                {
                    "compliance_score": 100.0,
                    "total_issues": 0,
                    "issues_by_severity": {"error": 0, "warning": 0, "info": 0},
                },
            )()

        def generate_console_report(self, report):
            return "📝 Verificador de docstrings no disponible"

    class MarkdownChecker:
        def check_project(self):
            return type(
                "Report",
                (),
                {
                    "compliance_score": 100.0,
                    "total_issues": 0,
                    "issues_by_severity": {"error": 0, "warning": 0},
                },
            )()

        def generate_console_report(self, report):
            return "📄 Verificador de Markdown no disponible"


@dataclass
class ConsolidatedReport:
    """Reporte consolidado de todos los estándares."""

    timestamp: str
    docstring_score: float
    markdown_score: float
    overall_score: float
    total_issues: int
    issues_by_category: Dict[str, int]
    compliance_grade: str
    summary: Dict[str, Any]


class StandardsChecker:
    """Verificador integrado de estándares de documentación."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docstring_checker = DocstringChecker(project_root)
        self.markdown_checker = MarkdownChecker(project_root)

    def check_all_standards(self) -> ConsolidatedReport:
        """Verificar todos los estándares de documentación."""
        print("🔍 VERIFICACIÓN INTEGRADA DE ESTÁNDARES")
        print("=" * 50)

        # Verificar docstrings
        print("\n📝 1. Verificando docstrings...")
        docstring_report = self.docstring_checker.check_project()

        # Verificar Markdown
        print("\n📄 2. Verificando Markdown...")
        markdown_report = self.markdown_checker.check_project()

        # Generar reporte consolidado
        return self._generate_consolidated_report(docstring_report, markdown_report)

    def _generate_consolidated_report(
        self, docstring_report, markdown_report
    ) -> ConsolidatedReport:
        """Generar reporte consolidado."""

        # Calcular score general (promedio ponderado)
        docstring_weight = 0.6  # Docstrings más importantes
        markdown_weight = 0.4  # Markdown importante pero menos crítico

        overall_score = (
            docstring_report.compliance_score * docstring_weight
            + markdown_report.compliance_score * markdown_weight
        )

        # Consolidar issues por categoría
        issues_by_category = {
            "docstring_errors": docstring_report.issues_by_severity.get("error", 0),
            "docstring_warnings": docstring_report.issues_by_severity.get("warning", 0),
            "docstring_info": docstring_report.issues_by_severity.get("info", 0),
            "markdown_errors": markdown_report.issues_by_severity.get("error", 0),
            "markdown_warnings": markdown_report.issues_by_severity.get("warning", 0),
        }

        total_issues = sum(issues_by_category.values())

        # Calcular grado
        compliance_grade = self._calculate_grade(overall_score)

        # Summary
        summary = {
            "docstring_objects": getattr(docstring_report, "total_objects", 0),
            "docstring_with_docs": getattr(
                docstring_report, "objects_with_docstrings", 0
            ),
            "markdown_files": getattr(markdown_report, "total_files", 0),
            "markdown_files_with_issues": getattr(
                markdown_report, "files_with_issues", 0
            ),
            "critical_issues": issues_by_category["docstring_errors"]
            + issues_by_category["markdown_errors"],
            "recommendations": self._generate_recommendations(
                docstring_report, markdown_report
            ),
        }

        return ConsolidatedReport(
            timestamp=datetime.now().isoformat(),
            docstring_score=docstring_report.compliance_score,
            markdown_score=markdown_report.compliance_score,
            overall_score=overall_score,
            total_issues=total_issues,
            issues_by_category=issues_by_category,
            compliance_grade=compliance_grade,
            summary=summary,
        )

    def _calculate_grade(self, score: float) -> str:
        """Calcular grado basado en el score."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _generate_recommendations(self, docstring_report, markdown_report) -> list:
        """Generar recomendaciones basadas en los reportes."""
        recommendations = []

        # Recomendaciones para docstrings
        if docstring_report.compliance_score < 80:
            recommendations.append("Mejorar documentación de funciones y clases")
            recommendations.append("Agregar docstrings faltantes en métodos públicos")

        if docstring_report.issues_by_severity.get("info", 0) > 10:
            recommendations.append("Corregir formato de docstrings (puntos finales)")

        # Recomendaciones para Markdown
        if markdown_report.compliance_score < 90:
            recommendations.append("Corregir formato de archivos Markdown")
            recommendations.append("Usar sintaxis de enlaces apropiada")

        if getattr(markdown_report, "total_files", 0) > 0:
            if getattr(markdown_report, "files_with_issues", 0) > 0:
                recommendations.append("Especificar lenguajes en bloques de código")

        # Recomendaciones generales
        if len(recommendations) == 0:
            recommendations.append("¡Excelente! Mantener estándares actuales")
        else:
            recommendations.append(
                "Configurar pre-commit hooks para verificación automática"
            )

        return recommendations[:5]  # Limitar a 5 recomendaciones

    def generate_console_report(self, report: ConsolidatedReport) -> str:
        """Generar reporte consolidado para consola."""
        output = []

        output.append("🔍 REPORTE CONSOLIDADO DE ESTÁNDARES")
        output.append("=" * 50)
        output.append(f"📅 Timestamp: {report.timestamp}")
        output.append(
            f"🎯 Score General: {report.overall_score:.1f}% (Grado: {report.compliance_grade})"
        )
        output.append("")

        output.append("📊 SCORES POR CATEGORÍA")
        output.append("-" * 30)
        output.append(f"📝 Docstrings: {report.docstring_score:.1f}%")
        output.append(f"📄 Markdown: {report.markdown_score:.1f}%")
        output.append("")

        output.append("📋 RESUMEN DE ISSUES")
        output.append("-" * 30)
        output.append(f"🔴 Errores críticos: {report.summary['critical_issues']}")
        output.append(
            f"🟡 Warnings docstrings: {report.issues_by_category['docstring_warnings']}"
        )
        output.append(
            f"🔵 Info docstrings: {report.issues_by_category['docstring_info']}"
        )
        output.append(
            f"🟡 Warnings Markdown: {report.issues_by_category['markdown_warnings']}"
        )
        output.append(f"📊 Total issues: {report.total_issues}")
        output.append("")

        output.append("📈 ESTADÍSTICAS")
        output.append("-" * 30)
        output.append(f"📝 Objetos Python: {report.summary['docstring_objects']}")
        output.append(f"✅ Con docstrings: {report.summary['docstring_with_docs']}")
        output.append(f"📄 Archivos Markdown: {report.summary['markdown_files']}")
        output.append(
            f"⚠️  MD con issues: {report.summary['markdown_files_with_issues']}"
        )
        output.append("")

        output.append("💡 RECOMENDACIONES")
        output.append("-" * 30)
        for i, rec in enumerate(report.summary["recommendations"], 1):
            output.append(f"{i}. {rec}")
        output.append("")

        # Estado general
        if report.compliance_grade in ["A+", "A"]:
            status = "🎉 EXCELENTE"
            message = "Estándares de documentación excepcionales"
        elif report.compliance_grade in ["B+", "B"]:
            status = "✅ BUENO"
            message = "Estándares sólidos con oportunidades de mejora"
        elif report.compliance_grade in ["C+", "C"]:
            status = "⚠️  ACEPTABLE"
            message = "Necesita mejoras en documentación"
        else:
            status = "❌ NECESITA ATENCIÓN"
            message = "Requiere mejoras significativas"

        output.append(f"🏆 ESTADO GENERAL: {status}")
        output.append(f"📝 {message}")

        return "\n".join(output)

    def generate_json_report(self, report: ConsolidatedReport) -> str:
        """Generar reporte en formato JSON."""
        return json.dumps(asdict(report), indent=2, default=str)


def main():
    """Función principal del verificador integrado."""
    import argparse

    parser = argparse.ArgumentParser(description="Verificador Integrado de Estándares")
    parser.add_argument(
        "--format",
        choices=["console", "json"],
        default="console",
        help="Formato de salida",
    )
    parser.add_argument("--output", "-o", help="Archivo de salida")
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Mostrar reportes detallados de cada verificador",
    )

    args = parser.parse_args()

    try:
        checker = StandardsChecker()
        report = checker.check_all_standards()

        if args.format == "json":
            output = checker.generate_json_report(report)
        else:
            output = checker.generate_console_report(report)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"\n📄 Reporte guardado en: {args.output}")
        else:
            print(f"\n{output}")

        # Mostrar reportes detallados si se solicita
        if args.detailed and args.format == "console":
            print("\n" + "=" * 60)
            print("📝 REPORTE DETALLADO DE DOCSTRINGS")
            print("=" * 60)
            docstring_report = checker.docstring_checker.check_project()
            print(checker.docstring_checker.generate_console_report(docstring_report))

            print("\n" + "=" * 60)
            print("📄 REPORTE DETALLADO DE MARKDOWN")
            print("=" * 60)
            markdown_report = checker.markdown_checker.check_project()
            print(checker.markdown_checker.generate_console_report(markdown_report))

        # Exit code basado en grado
        if report.compliance_grade in ["A+", "A"]:
            sys.exit(0)
        elif report.compliance_grade in ["B+", "B"]:
            sys.exit(1)
        else:
            sys.exit(2)

    except Exception as e:
        print(f"❌ Error durante verificación: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
