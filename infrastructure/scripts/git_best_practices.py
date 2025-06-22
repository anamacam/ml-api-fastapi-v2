#!/usr/bin/env python3
"""
Analizador Completo de Buenas Prácticas Git

Sistema avanzado que evalúa la calidad del repositorio Git analizando:
- Mensajes de commit (Conventional Commits)
- Estructura y naming de branches
- Tamaño y frecuencia de commits
- Historial y prácticas de Git

Score: Contribuye al sistema de calidad general
Autor: Sistema Automatizado de Calidad
Fecha: Diciembre 2024
"""

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class GitStats:
    """Estadísticas del repositorio Git."""

    total_commits: int = 0
    recent_commits: int = 0
    avg_files_per_commit: float = 0.0
    large_commits: int = 0
    conventional_commits: int = 0
    master_commits: int = 0
    branch_count: int = 0
    has_gitignore: bool = False
    has_readme: bool = False


class GitBestPracticesAnalyzer:
    """Analizador avanzado de buenas prácticas Git."""

    def __init__(self, repo_path: str = "."):
        """
        Inicializa el analizador.

        Args:
            repo_path: Ruta al repositorio Git
        """
        self.repo_path = Path(repo_path)
        self.conventional_types = [
            "feat",
            "fix",
            "docs",
            "style",
            "refactor",
            "test",
            "chore",
            "perf",
            "ci",
            "build",
        ]

    def run_git_command(self, command: List[str]) -> str:
        """
        Ejecuta comando git y retorna output.

        Args:
            command: Lista con comando git

        Returns:
            Output del comando
        """
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""

    def analyze_commit_messages(self) -> Tuple[int, int, List[str]]:
        """
        Analiza mensajes de commit para Conventional Commits.

        Returns:
            Tupla (total_commits, conventional_commits, problemas)
        """
        # Obtener últimos 100 commits
        commits = self.run_git_command(
            ["log", "--oneline", "-100", "--pretty=format:%s"]
        ).split("\n")

        if not commits or commits == [""]:
            return 0, 0, ["No hay commits en el repositorio"]

        conventional_pattern = rf'^({"|".join(self.conventional_types)})(\(.+\))?: .+'
        problems = []
        conventional_count = 0

        for i, commit_msg in enumerate(commits[:50]):  # Analizar últimos 50
            if not commit_msg:
                continue

            # Verificar si es conventional commit
            if re.match(conventional_pattern, commit_msg):
                conventional_count += 1
            else:
                problems.append(f"Commit no convencional: '{commit_msg[:60]}...'")

            # Verificar longitud
            if len(commit_msg) > 50:
                problems.append(
                    f"Mensaje muy largo ({len(commit_msg)} chars): '{
                                         commit_msg[:40]}...'"
                )

        return len(commits), conventional_count, problems[:10]  # Limitar problemas

    def analyze_commit_sizes(self) -> Tuple[float, int, List[str]]:
        """
        Analiza tamaños de commits.

        Returns:
            Tupla (promedio_archivos, commits_grandes, problemas)
        """
        # Últimos 20 commits con estadísticas
        stats = self.run_git_command(
            ["log", "--oneline", "-20", "--stat", "--pretty=format:%H"]
        )

        if not stats:
            return 0.0, 0, ["No hay estadísticas de commits"]

        commit_sizes = []
        problems = []
        large_commits = 0

        # Parsear estadísticas (simplificado)
        lines = stats.split("\n")

        for line in lines:
            if "files changed" in line:
                # Extraer número de archivos
                match = re.search(r"(\\d+) files? changed", line)
                if match:
                    files_count = int(match.group(1))
                    commit_sizes.append(files_count)

                    if files_count > 20:  # Threshold para commit grande
                        large_commits += 1
                        problems.append(f"Commit muy grande: {files_count} archivos")

        avg_files = sum(commit_sizes) / len(commit_sizes) if commit_sizes else 0
        return avg_files, large_commits, problems[:5]

    def analyze_branch_structure(self) -> Tuple[int, int, List[str]]:
        """
        Analiza estructura de branches.

        Returns:
            Tupla (total_branches, commits_en_master, problemas)
        """
        # Contar branches
        branches = self.run_git_command(["branch", "-a"]).split("\n")
        branch_count = len(
            [b for b in branches if b.strip() and not b.strip().startswith("*")]
        )

        # Commits recientes en master/main
        current_branch = self.run_git_command(["branch", "--show-current"])
        master_commits = 0
        problems = []

        if current_branch in ["master", "main"]:
            # Contar commits de último mes en master
            since_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            recent_commits = self.run_git_command(
                ["log", "--oneline", f"--since={since_date}", "--pretty=format:%H"]
            ).split("\n")
            master_commits = len([c for c in recent_commits if c.strip()])

            if master_commits > 10:
                problems.append(
                    f"Muchos commits directos en {current_branch}: {master_commits}"
                )

        return branch_count, master_commits, problems

    def check_essential_files(self) -> Tuple[bool, bool, List[str]]:
        """
        Verifica archivos esenciales del proyecto.

        Returns:
            Tupla (tiene_gitignore, tiene_readme, problemas)
        """
        problems = []

        gitignore_exists = (self.repo_path / ".gitignore").exists()
        readme_exists = any(
            [
                (self.repo_path / "README.md").exists(),
                (self.repo_path / "README.rst").exists(),
                (self.repo_path / "README.txt").exists(),
            ]
        )

        if not gitignore_exists:
            problems.append("Falta archivo .gitignore")

        if not readme_exists:
            problems.append("Falta archivo README")

        return gitignore_exists, readme_exists, problems

    def calculate_git_score(self, stats: GitStats) -> Tuple[float, str]:
        """
        Calcula el score de buenas prácticas Git.

        Args:
            stats: Estadísticas del repositorio

        Returns:
            Tupla (score, grade)
        """
        score = 0.0
        _ = 100.0

        # Conventional Commits (30 puntos)
        if stats.total_commits > 0:
            conventional_ratio = stats.conventional_commits / min(
                stats.total_commits, 50
            )
            score += conventional_ratio * 30

        # Tamaño de commits (25 puntos)
        if stats.avg_files_per_commit > 0:
            # Penalizar commits muy grandes
            size_score = max(0, 25 - (stats.avg_files_per_commit - 5) * 2)
            score += min(25, size_score)
        else:
            score += 25  # Sin commits grandes es bueno

        # Estructura de branches (20 puntos)
        if stats.branch_count > 1:
            score += 10  # Usar branches
        if stats.master_commits < 10:
            score += 10  # No muchos commits directos en master

        # Archivos esenciales (15 puntos)
        if stats.has_gitignore:
            score += 8
        if stats.has_readme:
            score += 7

        # Actividad reciente (10 puntos)
        if stats.recent_commits > 0:
            score += min(10, stats.recent_commits)

        # Determinar grade
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        return score, grade

    def analyze(self) -> Dict:
        """
        Ejecuta análisis completo de buenas prácticas Git.

        Returns:
            Diccionario con resultados del análisis
        """
        print("🔍 Analizando buenas prácticas Git...")

        # Verificar que estamos en repo Git
        try:
            self.run_git_command(["status"])
        except Exception:
            return {
                "error": "No es un repositorio Git válido",
                "score": 0,
                "grade": "F",
            }

        # Recopilar estadísticas
        stats = GitStats()
        problems = []

        # Analizar commits
        (
            total_commits,
            conventional_commits,
            commit_problems,
        ) = self.analyze_commit_messages()
        stats.total_commits = total_commits
        stats.conventional_commits = conventional_commits
        problems.extend(commit_problems)

        # Analizar tamaños
        avg_files, large_commits, size_problems = self.analyze_commit_sizes()
        stats.avg_files_per_commit = avg_files
        stats.large_commits = large_commits
        problems.extend(size_problems)

        # Analizar branches
        branch_count, master_commits, branch_problems = self.analyze_branch_structure()
        stats.branch_count = branch_count
        stats.master_commits = master_commits
        problems.extend(branch_problems)

        # Verificar archivos esenciales
        has_gitignore, has_readme, file_problems = self.check_essential_files()
        stats.has_gitignore = has_gitignore
        stats.has_readme = has_readme
        problems.extend(file_problems)

        # Calcular score
        score, grade = self.calculate_git_score(stats)

        return {
            "git_best_practices": {
                "score": round(score, 1),
                "grade": grade,
                "total_commits": stats.total_commits,
                "conventional_commits": stats.conventional_commits,
                "conventional_ratio": round(
                    stats.conventional_commits / max(stats.total_commits, 1) * 100, 1
                ),
                "avg_files_per_commit": round(stats.avg_files_per_commit, 1),
                "large_commits": stats.large_commits,
                "branch_count": stats.branch_count,
                "master_commits": stats.master_commits,
                "has_gitignore": stats.has_gitignore,
                "has_readme": stats.has_readme,
                "problems": problems[:15],  # Limitar problemas mostrados
                "recommendations": self.get_recommendations(stats, problems),
            },
            "timestamp": datetime.now().isoformat(),
            "repository_path": str(self.repo_path),
        }

    def get_recommendations(self, stats: GitStats, problems: List[str]) -> List[str]:
        """
        Genera recomendaciones basadas en el análisis.

        Args:
            stats: Estadísticas del repositorio
            problems: Lista de problemas encontrados

        Returns:
            Lista de recomendaciones
        """
        recommendations = []

        # Conventional Commits
        if stats.total_commits > 0:
            conventional_ratio = stats.conventional_commits / stats.total_commits
            if conventional_ratio < 0.7:
                recommendations.append(
                    "📝 Usar Conventional Commits: feat:, fix:, docs:, etc."
                )

        # Tamaño de commits
        if stats.avg_files_per_commit > 10:
            recommendations.append(
                "📦 Hacer commits más pequeños y atómicos (< 10 archivos)"
            )

        # Branches
        if stats.branch_count <= 1:
            recommendations.append("🌿 Usar feature branches para desarrollo")

        if stats.master_commits > 10:
            recommendations.append("🚫 Evitar commits directos en master/main")

        # Archivos esenciales
        if not stats.has_gitignore:
            recommendations.append("📄 Crear archivo .gitignore")

        if not stats.has_readme:
            recommendations.append("📖 Crear archivo README.md con documentación")

        return recommendations[:8]  # Limitar recomendaciones


def main():
    """Punto de entrada principal para el análisis de Git."""
    parser = argparse.ArgumentParser(
        description="Analizador de Buenas Prácticas de Git."
    )
    parser.add_argument(
        "--repo-path", default=".", help="Ruta al repositorio Git."
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Formato de salida del reporte.",
    )
    args = parser.parse_args()

    analyzer = GitBestPracticesAnalyzer(args.repo_path)
    results = analyzer.analyze()

    if args.output_format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text_output(results))


def format_text_output(results: Dict) -> str:
    """
    Formatea los resultados como texto legible.

    Args:
        results: Resultados del análisis

    Returns:
        String formateado para mostrar
    """
    if "error" in results:
        return f"❌ Error: {results['error']}"

    git_data = results.get("git_best_practices", {})

    output = []
    output.append("=" * 60)
    output.append("🔍 ANÁLISIS DE BUENAS PRÁCTICAS GIT")
    output.append("=" * 60)
    output.append("")

    # Score principal
    score = git_data.get("score", 0)
    grade = git_data.get("grade", "F")
    output.append(f"📊 SCORE GENERAL: {score}/100 (Grado {grade})")
    output.append("")

    # Estadísticas detalladas
    output.append("📈 ESTADÍSTICAS:")
    output.append(f"  • Total commits analizados: {git_data.get('total_commits', 0)}")
    output.append(
        f"  • Conventional commits: {git_data.get('conventional_commits', 0)} ({
                                                  git_data.get('conventional_ratio', 0)}%)"
    )
    output.append(
        f"  • Promedio archivos/commit: {git_data.get('avg_files_per_commit', 0)}"
    )
    output.append(f"  • Commits grandes: {git_data.get('large_commits', 0)}")
    output.append(f"  • Branches activos: {git_data.get('branch_count', 0)}")
    output.append(f"  • Commits en master: {git_data.get('master_commits', 0)}")
    output.append(f"  • .gitignore: {'✅' if git_data.get('has_gitignore') else '❌'}")
    output.append(f"  • README: {'✅' if git_data.get('has_readme') else '❌'}")
    output.append("")

    # Problemas encontrados
    problems = git_data.get("problems", [])
    if problems:
        output.append("⚠️  PROBLEMAS DETECTADOS:")
        for problem in problems:
            output.append(f"  • {problem}")
        output.append("")

    # Recomendaciones
    recommendations = git_data.get("recommendations", [])
    if recommendations:
        output.append("💡 RECOMENDACIONES:")
        for rec in recommendations:
            output.append(f"  • {rec}")
        output.append("")

    # Footer
    timestamp = results.get("timestamp", "")
    if timestamp:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        output.append(f"🕒 Análisis ejecutado: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

    output.append("=" * 60)

    return "\n".join(output)


if __name__ == "__main__":
    main()
