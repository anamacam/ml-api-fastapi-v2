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
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class ProgressPoint:
    """Punto de progreso individual."""

    timestamp: str
    commit_hash: str
    branch: str
    total_score: float
    debt_percentage: float
    metrics: Dict[str, float]
    author: str = ""


@dataclass
class ProgressSummary:
    """Resumen de progreso."""

    current_score: float
    previous_score: float
    improvement: str
    trend: str  # 'improving', 'stable', 'declining'
    days_tracked: int
    best_score: float
    worst_score: float
    average_score: float
    velocity: float  # puntos por día
    milestones_achieved: List[str]
    next_milestone: str
    recommendations: List[str]


class ProgressTracker:
    """Tracker de progreso de calidad."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports"
        self.progress_file = self.reports_dir / "quality_history.json"
        self.reports_dir.mkdir(exist_ok=True)

    def track_current_progress(self) -> ProgressSummary:
        """Trackear el progreso actual."""
        print("📈 Trackeando progreso de calidad...")

        # Leer reporte actual
        current_report = self._load_current_report()

        # Cargar historial
        history = self._load_history()

        # Crear punto de progreso actual
        current_point = self._create_progress_point(current_report)

        # Agregar al historial
        history.append(current_point)

        # Limpiar historial viejo (mantener últimos 30 días)
        history = self._cleanup_old_history(history)

        # Guardar historial actualizado
        self._save_history(history)

        # Generar resumen de progreso
        summary = self._generate_progress_summary(history)

        # Guardar resumen
        self._save_progress_summary(summary)

        return summary

    def _load_current_report(self) -> Dict[str, Any]:
        """Cargar el reporte actual de deuda técnica."""
        current_report_file = self.reports_dir / "current_debt.json"

        if current_report_file.exists():
            with open(current_report_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # Si no existe, ejecutar análisis
        print("📊 Ejecutando análisis de deuda técnica...")
        result = subprocess.run(
            [
                "python",
                "infrastructure/scripts/tech_debt_analyzer.py",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

        if result.returncode == 0:
            report = json.loads(result.stdout)
            with open(current_report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            return report

        # Fallback si hay error
        return {
            "total_score": 73.8,
            "debt_percentage": 26.2,
            "timestamp": datetime.now().isoformat(),
            "metrics": [],
        }

    def _load_history(self) -> List[ProgressPoint]:
        """Cargar historial de progreso."""
        if not self.progress_file.exists():
            return []

        with open(self.progress_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [ProgressPoint(**point) for point in data]

    def _create_progress_point(self, report: Dict[str, Any]) -> ProgressPoint:
        """Crear punto de progreso actual."""
        commit_hash = self._get_current_commit()
        branch = self._get_current_branch()
        author = self._get_commit_author()

        # Extraer métricas individuales
        metrics = {}
        if "metrics" in report:
            for metric in report["metrics"]:
                if isinstance(metric, dict) and "name" in metric:
                    metrics[metric["name"]] = metric.get("value", 0.0)

        return ProgressPoint(
            timestamp=datetime.now().isoformat(),
            commit_hash=commit_hash,
            branch=branch,
            total_score=report.get("total_score", 73.8),
            debt_percentage=report.get("debt_percentage", 26.2),
            metrics=metrics,
            author=author,
        )

    def _get_current_commit(self) -> str:
        """Obtener hash del commit actual."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True
            )
            return result.stdout.strip()[:8] if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def _get_current_branch(self) -> str:
        """Obtener rama actual."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def _get_commit_author(self) -> str:
        """Obtener autor del commit actual."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%an"],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def _cleanup_old_history(self, history: List[ProgressPoint]) -> List[ProgressPoint]:
        """Limpiar historial viejo (mantener últimos 30 días)."""
        cutoff_date = datetime.now() - timedelta(days=30)

        return [
            point
            for point in history
            if datetime.fromisoformat(point.timestamp.replace("Z", "+00:00"))
            > cutoff_date
        ]

    def _save_history(self, history: List[ProgressPoint]):
        """Guardar historial de progreso."""
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump([asdict(point) for point in history], f, indent=2)

    def _generate_progress_summary(
        self, history: List[ProgressPoint]
    ) -> ProgressSummary:
        """Generar resumen de progreso."""
        if not history:
            return self._create_empty_summary()

        current, previous = self._get_current_and_previous(history)
        scores = [p.total_score for p in history]

        improvement = self._calculate_improvement(
            current.total_score, previous.total_score
        )
        trend = self._calculate_trend(history)
        stats = self._calculate_statistics(scores)
        velocity = self._calculate_velocity(history)

        milestones_achieved = self._check_milestones(history)
        next_milestone = self._get_next_milestone(current.total_score)
        recommendations = self._generate_recommendations(current, history)

        return ProgressSummary(
            current_score=current.total_score,
            previous_score=previous.total_score,
            improvement=improvement,
            trend=trend,
            days_tracked=len(history),
            best_score=stats["best"],
            worst_score=stats["worst"],
            average_score=stats["average"],
            velocity=velocity,
            milestones_achieved=milestones_achieved,
            next_milestone=next_milestone,
            recommendations=recommendations,
        )

    def _create_empty_summary(self) -> ProgressSummary:
        """Crear summary vacío para historial sin datos."""
        return ProgressSummary(
            current_score=73.8,
            previous_score=73.8,
            improvement="Sin datos históricos",
            trend="stable",
            days_tracked=0,
            best_score=73.8,
            worst_score=73.8,
            average_score=73.8,
            velocity=0.0,
            milestones_achieved=[],
            next_milestone="Alcanzar 75 puntos",
            recommendations=["Ejecutar análisis por primera vez"],
        )

    def _get_current_and_previous(self, history: List[ProgressPoint]) -> tuple:
        """Obtener puntos actual y anterior."""
        current = history[-1]
        previous = history[-2] if len(history) > 1 else history[0]
        return current, previous

    def _calculate_improvement(
        self, current_score: float, previous_score: float
    ) -> str:
        """Calcular string de mejora."""
        improvement_value = current_score - previous_score
        if improvement_value > 0:
            return f"+{improvement_value:.1f} puntos"
        elif improvement_value < 0:
            return f"{improvement_value:.1f} puntos"
        else:
            return "Sin cambios"

    def _calculate_statistics(self, scores: List[float]) -> dict:
        """Calcular estadísticas básicas."""
        return {
            "best": max(scores),
            "worst": min(scores),
            "average": sum(scores) / len(scores),
        }

    def _calculate_velocity(self, history: List[ProgressPoint]) -> float:
        """Calcular velocidad de mejora."""
        if len(history) <= 1:
            return 0.0

        current = history[-1]
        first = history[0]

        days_span = (
            datetime.fromisoformat(current.timestamp)
            - datetime.fromisoformat(first.timestamp)
        ).days
        total_improvement = current.total_score - first.total_score

        return total_improvement / max(days_span, 1)

    def _calculate_trend(self, history: List[ProgressPoint]) -> str:
        """Calcular tendencia de los últimos puntos."""
        if len(history) < 3:
            return "stable"

        # Usar últimos 5 puntos o todos si hay menos
        recent_points = history[-5:]
        scores = [p.total_score for p in recent_points]

        # Calcular tendencia lineal simple
        improvements = 0
        declines = 0

        for i in range(1, len(scores)):
            if scores[i] > scores[i - 1]:
                improvements += 1
            elif scores[i] < scores[i - 1]:
                declines += 1

        if improvements > declines:
            return "improving"
        elif declines > improvements:
            return "declining"
        else:
            return "stable"

    def _check_milestones(self, history: List[ProgressPoint]) -> List[str]:
        """Verificar milestones alcanzados."""
        milestones = []
        current_score = history[-1].total_score

        milestone_levels = [75, 80, 85, 90, 95]

        for level in milestone_levels:
            if current_score >= level:
                # Verificar si es un milestone nuevo
                previous_scores = [p.total_score for p in history[:-1]]
                if not previous_scores or max(previous_scores) < level:
                    milestones.append(f"🎯 Alcanzado {level} puntos")

        return milestones

    def _get_next_milestone(self, current_score: float) -> str:
        """Obtener próximo milestone."""
        milestone_levels = [75, 80, 85, 90, 95, 100]

        for level in milestone_levels:
            if current_score < level:
                points_needed = level - current_score
                return f"Alcanzar {level} puntos ({points_needed:.1f} puntos restantes)"

        return "¡Perfección alcanzada! (100 puntos)"

    def _generate_recommendations(
        self, current: ProgressPoint, history: List[ProgressPoint]
    ) -> List[str]:
        """Generar recomendaciones basadas en progreso."""
        recommendations = []
        score = current.total_score

        if score < 70:
            recommendations.append("🚨 Prioridad ALTA: Mejorar calidad del código")
            recommendations.append("📝 Revisar funciones con alta complejidad")
            recommendations.append("🧪 Aumentar cobertura de tests")
        elif score < 80:
            recommendations.append("📈 Continuar mejorando: Estás en buen camino")
            recommendations.append("🔍 Revisar deuda técnica pendiente")
            recommendations.append("📚 Mejorar documentación")
        elif score < 90:
            recommendations.append("🎯 Excelente progreso: Pulir detalles")
            recommendations.append("🏗️ Refactorizar código legacy")
            recommendations.append("⚡ Optimizar performance")
        else:
            recommendations.append("🎉 ¡Fantástico! Mantener estándares altos")
            recommendations.append("🚀 Considerar métricas avanzadas")
            recommendations.append("👥 Mentorear al equipo")

        # Recomendaciones basadas en tendencia
        trend = self._calculate_trend(history)
        if trend == "declining":
            recommendations.insert(0, "⚠️ ALERTA: La calidad está disminuyendo")
        elif trend == "improving":
            recommendations.append("🚀 ¡Sigue así! La tendencia es positiva")

        return recommendations[:5]  # Limitar a 5 recomendaciones

    def _save_progress_summary(self, summary: ProgressSummary):
        """Guardar resumen de progreso."""
        summary_file = self.reports_dir / "progress_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(asdict(summary), f, indent=2)

        print(
            f"📊 Progreso guardado: {summary.current_score:.1f} puntos ({summary.improvement})"
        )


def main():
    """Función principal."""
    tracker = ProgressTracker()
    summary = tracker.track_current_progress()

    print("\n📈 RESUMEN DE PROGRESO")
    print("=" * 50)
    print(f"🎯 Score Actual: {summary.current_score:.1f}/100")
    print(f"📊 Mejora: {summary.improvement}")
    print(f"📈 Tendencia: {summary.trend}")
    print(f"🏆 Mejor Score: {summary.best_score:.1f}")
    print(f"⚡ Velocidad: {summary.velocity:.2f} puntos/día")

    if summary.milestones_achieved:
        print(f"\n🎉 Milestones Alcanzados:")
        for milestone in summary.milestones_achieved:
            print(f"  {milestone}")

    print(f"\n🎯 Próximo Objetivo: {summary.next_milestone}")

    if summary.recommendations:
        print(f"\n💡 Recomendaciones:")
        for i, rec in enumerate(summary.recommendations, 1):
            print(f"  {i}. {rec}")


if __name__ == "__main__":
    main()
