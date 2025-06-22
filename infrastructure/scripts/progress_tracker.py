#!/usr/bin/env python3
"""
📈 Progress Tracker - ML API FastAPI v2
=======================================

Trackea el progreso histórico de la calidad del código:
- Historial de scores
- Tendencias de mejora
- Métricas de progreso
- Alertas de regresión
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any


def get_git_log_stats(repo_path: Path) -> int:
    """Obtiene el número de commits en el repositorio."""
    try:
        result = subprocess.run(
            ["git", "log", "--all", "--count"], capture_output=True, text=True
        )
        return int(result.stdout.strip())
    except Exception:
        return 0


def analyze_linting(lint_path: Path) -> Dict[str, Any]:
    """Analiza el reporte de linting."""
    if not lint_path.exists():
        return {"total_errors": 0, "total_lines": 0, "errors_by_type": {}}
    with open(lint_path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_tests(test_path: Path) -> Dict[str, Any]:
    """Analiza el reporte de pruebas."""
    if not test_path.exists():
        return {"total_tests": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}
    with open(test_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    summary = data.get("summary", {})
    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    return {
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": (passed / total * 100) if total > 0 else 0.0,
    }


def analyze_coverage(coverage_path: Path) -> float:
    """Analiza el reporte de cobertura y devuelve el porcentaje total."""
    if not coverage_path.exists():
        return 0.0

    with open(coverage_path, "r", encoding="utf-8") as f:
        coverage_data = json.load(f)
    return coverage_data.get("totals", {}).get("percent_covered", 0.0)


def analyze_doc_quality(
    doc_checker_report_path: Path, md_checker_report_path: Path
) -> float:
    """Calcula un puntaje de calidad de documentación."""
    doc_score = 0.0
    md_score = 0.0

    if doc_checker_report_path.exists():
        with open(doc_checker_report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            doc_score = data.get("compliance_score", 0.0)

    if md_checker_report_path.exists():
        with open(md_checker_report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            md_score = data.get("compliance_score", 0.0)

    return (doc_score + md_score) / 2


def generate_progress_report(base_path: Path) -> Dict[str, Any]:
    """Genera un reporte de progreso completo del proyecto."""
    # Rutas a los artefactos de calidad
    lint_report_path = base_path / "reports/linting/flake8_stats.json"
    test_report_path = base_path / "reports/tests/report.json"
    coverage_report_path = base_path / "reports/coverage/coverage.json"
    docstring_report_path = base_path / "reports/documentation/docstring_report.json"
    markdown_report_path = base_path / "reports/documentation/markdown_report.json"

    # Análisis
    commit_count = get_git_log_stats(base_path)
    lint_stats = analyze_linting(lint_report_path)
    test_stats = analyze_tests(test_report_path)
    coverage_percent = analyze_coverage(coverage_report_path)
    doc_quality_score = analyze_doc_quality(
        docstring_report_path, markdown_report_path
    )

    # Métricas clave
    code_to_test_ratio = (
        (lint_stats["total_lines"] / test_stats["total_tests"])
        if test_stats["total_tests"] > 0
        else 0
    )

    report = {
        "commits": commit_count,
        "code_quality": {
            "lint_errors": lint_stats["total_errors"],
            "lines_of_code": lint_stats["total_lines"],
            "error_density": (
                (lint_stats["total_errors"] / lint_stats["total_lines"]) * 1000
                if lint_stats["total_lines"] > 0
                else 0
            ),
        },
        "testing": {
            "total_tests": test_stats["total_tests"],
            "passed": test_stats["passed"],
            "failed": test_stats["failed"],
            "pass_rate": test_stats["pass_rate"],
            "coverage": coverage_percent,
            "code_to_test_ratio": code_to_test_ratio,
        },
        "documentation": {"quality_score": doc_quality_score},
    }

    return report


def main():
    """Punto de entrada para generar y mostrar el reporte de progreso."""
    project_root = Path(__file__).parent.parent.parent
    report = generate_progress_report(project_root)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
