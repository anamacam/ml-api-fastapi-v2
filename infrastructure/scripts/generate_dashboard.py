#!/usr/bin/env python3
"""
📊 Dashboard Generator - ML API FastAPI v2
==========================================

Genera dashboard HTML interactivo con:
- Gráficos de progreso histórico
- Métricas de calidad en tiempo real
- Comparación de tendencias
- Reportes visuales
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class DashboardGenerator:
    """Generador de dashboard de progreso."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def generate_dashboard(self):
        """Generar dashboard completo."""
        print("📊 Generando dashboard de progreso...")

        # Cargar datos
        progress_data = self._load_progress_data()
        current_report = self._load_current_report()

        # Generar HTML
        html_content = self._generate_html(progress_data, current_report)

        # Guardar dashboard
        dashboard_file = self.reports_dir / "dashboard.html"
        with open(dashboard_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ Dashboard generado: {dashboard_file}")
        return dashboard_file

    def _load_progress_data(self) -> Dict[str, Any]:
        """Cargar datos de progreso."""
        progress_file = self.reports_dir / "progress_summary.json"

        if progress_file.exists():
            with open(progress_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {
            "current_score": 73.8,
            "improvement": "Sin datos",
            "trend": "stable",
            "recommendations": [],
        }

    def _load_current_report(self) -> Dict[str, Any]:
        """Cargar reporte actual."""
        report_file = self.reports_dir / "current_debt.json"

        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {"metrics": []}

    def _load_history(self) -> List[Dict[str, Any]]:
        """Cargar historial para gráficos."""
        history_file = self.reports_dir / "quality_history.json"

        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return []

    def _generate_html(
        self, progress_data: Dict[str, Any], current_report: Dict[str, Any]
    ) -> str:
        """Generar HTML completo del dashboard."""
        history = self._load_history()

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Quality Dashboard - ML API FastAPI v2</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Quality Progress Dashboard</h1>
            <p class="subtitle">ML API FastAPI v2 - Tracking de Calidad en Tiempo Real</p>
            <div class="timestamp">Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </header>

        <div class="metrics-grid">
            {self._generate_score_card(progress_data)}
            {self._generate_progress_card(progress_data)}
            {self._generate_trend_card(progress_data)}
            {self._generate_milestone_card(progress_data)}
        </div>

        <div class="charts-section">
            <div class="chart-container">
                <h3>📈 Evolución del Score</h3>
                <canvas id="scoreChart"></canvas>
            </div>

            <div class="chart-container">
                <h3>🎯 Métricas Detalladas</h3>
                <canvas id="metricsChart"></canvas>
            </div>
        </div>

        <div class="recommendations-section">
            <h3>💡 Recomendaciones de Mejora</h3>
            <div class="recommendations-list">
                {self._generate_recommendations_html(
                    progress_data.get('recommendations', []))}
            </div>
        </div>

        <footer>
            <p>🚀 Sistema Anti-Deuda Técnica | Generado automáticamente</p>
        </footer>
    </div>

    <script>
        {self._generate_javascript(history, current_report)}
    </script>
</body>
</html>"""

    def _get_css_styles(self) -> str:
        """Obtener estilos CSS."""
        base_styles = self._get_base_css()
        layout_styles = self._get_layout_css()
        component_styles = self._get_component_css()
        responsive_styles = self._get_responsive_css()

        return (
            f"{base_styles}\n{layout_styles}\n{component_styles}\n{responsive_styles}"
        )

    def _get_base_css(self) -> str:
        """Estilos base y reset."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        """

    def _get_layout_css(self) -> str:
        """Estilos de layout principal."""
        return """
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .charts-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        """

    def _get_component_css(self) -> str:
        """Estilos de componentes."""
        return """
        header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-5px);
        }

        .score-excellent { color: #28a745; }
        .score-good { color: #17a2b8; }
        .score-warning { color: #ffc107; }
        .score-critical { color: #dc3545; }
        """

    def _get_responsive_css(self) -> str:
        """Estilos responsivos."""
        return """
        @media (max-width: 768px) {
            .charts-section {
                grid-template-columns: 1fr;
            }

            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
        """

    def _generate_score_card(self, progress_data: Dict[str, Any]) -> str:
        """Generar tarjeta de score principal."""
        score = progress_data.get("current_score", 73.8)

        if score >= 85:
            score_class = "score-excellent"
            icon = "🎉"
        elif score >= 75:
            score_class = "score-good"
            icon = "👍"
        elif score >= 65:
            score_class = "score-warning"
            icon = "⚠️"
        else:
            score_class = "score-critical"
            icon = "🚨"

        return f"""
        <div class="metric-card">
            <div class="metric-title">{icon} Score de Calidad</div>
            <div class="metric-value {score_class}">{score:.1f}</div>
            <div class="metric-change neutral">de 100 puntos</div>
        </div>
        """

    def _generate_progress_card(self, progress_data: Dict[str, Any]) -> str:
        """Generar tarjeta de progreso."""
        improvement = progress_data.get("improvement", "Sin datos")

        if "+" in improvement:
            change_class = "positive"
            icon = "📈"
        elif "-" in improvement:
            change_class = "negative"
            icon = "📉"
        else:
            change_class = "neutral"
            icon = "➡️"

        return f"""
        <div class="metric-card">
            <div class="metric-title">{icon} Progreso</div>
            <div class="metric-value">Progreso</div>
            <div class="metric-change {change_class}">{improvement}</div>
        </div>
        """

    def _generate_trend_card(self, progress_data: Dict[str, Any]) -> str:
        """Generar tarjeta de tendencia."""
        trend = progress_data.get("trend", "stable")

        trend_icons = {"improving": "🚀", "stable": "📊", "declining": "📉"}

        trend_labels = {
            "improving": "Mejorando",
            "stable": "Estable",
            "declining": "Disminuyendo",
        }

        icon = trend_icons.get(trend, "📊")
        label = trend_labels.get(trend, "Estable")

        return f"""
        <div class="metric-card">
            <div class="metric-title">{icon} Tendencia</div>
            <div class="metric-value">{label}</div>
            <div class="metric-change neutral">Últimos 5 puntos</div>
        </div>
        """

    def _generate_milestone_card(self, progress_data: Dict[str, Any]) -> str:
        """Generar tarjeta de milestone."""
        next_milestone = progress_data.get("next_milestone", "Alcanzar 75 puntos")

        return f"""
        <div class="metric-card">
            <div class="metric-title">🎯 Próximo Objetivo</div>
            <div class="metric-value" style="font-size: 1.2em;">{next_milestone}</div>
            <div class="metric-change neutral">Siguiente meta</div>
        </div>
        """

    def _generate_recommendations_html(self, recommendations: List[str]) -> str:
        """Generar HTML de recomendaciones."""
        if not recommendations:
            return '<div class="recommendation-item">🎉 ¡Todo perfecto! Sin recomendaciones.</div>'

        html = ""
        for rec in recommendations:
            html += f'<div class="recommendation-item">{rec}</div>'

        return html

    def _generate_javascript(
        self, history: List[Dict[str, Any]], current_report: Dict[str, Any]
    ) -> str:
        """Generar JavaScript para los gráficos."""
        # Preparar datos para gráficos
        if history:
            dates = [point["timestamp"][:10] for point in history]  # Solo fecha
            scores = [point["total_score"] for point in history]
        else:
            dates = [datetime.now().strftime("%Y-%m-%d")]
            scores = [73.8]

        return f"""
        // Gráfico de evolución del score
        const scoreCtx = document.getElementById('scoreChart').getContext('2d');
        new Chart(scoreCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: 'Score de Calidad',
                    data: {json.dumps(scores)},
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        min: 60,
                        max: 100
                    }}
                }}
            }}
        }});

        // Gráfico de métricas detalladas (ejemplo)
        const metricsCtx = document.getElementById('metricsChart').getContext('2d');
        new Chart(metricsCtx, {{
            type: 'radar',
            data: {{
                labels: ['Complejidad', 'Tests', 'Documentación', 'Estándares', 'Dependencias'],
                datasets: [{{
                    label: 'Calidad Actual',
                    data: [85, 90, 75, 80, 95],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.2)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
        """


def main():
    """Función principal."""
    generator = DashboardGenerator()
    dashboard_file = generator.generate_dashboard()
    print(f"📊 Dashboard disponible en: {dashboard_file}")


if __name__ == "__main__":
    main()
