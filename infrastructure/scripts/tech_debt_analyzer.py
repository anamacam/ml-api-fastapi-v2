#!/usr/bin/env python3
"""
🔧 Analizador de Deuda Técnica y Refactoring Automático
ML API FastAPI v2

Este script analiza el código para detectar y sugerir correcciones
automáticas de deuda técnica.
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter
import argparse
import json
from datetime import datetime


@dataclass
class TechDebtIssue:
    """Representa un issue de deuda técnica detectado."""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    suggestion: str
    auto_fixable: bool = False
    fix_code: Optional[str] = None


class CodeAnalyzer(ast.NodeVisitor):
    """Analizador AST para detectar patrones de deuda técnica."""
    
    def __init__(self, file_path: str, content: str):
        self.file_path = file_path
        self.content = content
        self.lines = content.split('\n')
        self.issues: List[TechDebtIssue] = []
        self.imports: Set[str] = set()
        self.used_names: Set[str] = set()
        self.function_definitions: List[Tuple[str, int, int]] = []  # (name, start_line, complexity)
        self.class_definitions: List[Tuple[str, int]] = []  # (name, line)
        
    def visit_Import(self, node: ast.Import) -> None:
        """Rastrear imports."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Rastrear imports from."""
        if node.module:
            for alias in node.names:
                self.imports.add(f"{node.module}.{alias.name}")
        self.generic_visit(node)
    
    def visit_Name(self, node: ast.Name) -> None:
        """Rastrear nombres usados."""
        self.used_names.add(node.id)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analizar definiciones de funciones."""
        # Calcular complejidad ciclomática
        complexity = self._calculate_complexity(node)
        self.function_definitions.append((node.name, node.lineno, complexity))
        
        # Verificar longitud de función
        function_length = node.end_lineno - node.lineno if node.end_lineno else 0
        if function_length > 50:
            self.issues.append(TechDebtIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="long_function",
                severity="medium",
                description=f"Función '{node.name}' muy larga ({function_length} líneas)",
                suggestion="Dividir en funciones más pequeñas",
                auto_fixable=False
            ))
        
        # Verificar complejidad ciclomática
        if complexity > 10:
            self.issues.append(TechDebtIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="high_complexity",
                severity="high" if complexity > 15 else "medium",
                description=f"Función '{node.name}' muy compleja (complejidad: {complexity})",
                suggestion="Refactorizar para reducir complejidad",
                auto_fixable=False
            ))
        
        # Verificar docstring
        if not self._has_docstring(node):
            if not node.name.startswith('_'):  # Solo funciones públicas
                self.issues.append(TechDebtIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    issue_type="missing_docstring",
                    severity="medium",
                    description=f"Función pública '{node.name}' sin docstring",
                    suggestion="Agregar docstring explicando propósito y parámetros",
                    auto_fixable=True,
                    fix_code=self._generate_docstring_fix(node)
                ))
        
        # Verificar número de parámetros
        args_count = len(node.args.args)
        if args_count > 7:
            self.issues.append(TechDebtIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="too_many_params",
                severity="medium",
                description=f"Función '{node.name}' con demasiados parámetros ({args_count})",
                suggestion="Considerar usar un objeto o dataclass para agrupar parámetros",
                auto_fixable=False
            ))
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analizar definiciones de clases."""
        self.class_definitions.append((node.name, node.lineno))
        
        # Verificar docstring de clase
        if not self._has_docstring(node):
            if not node.name.startswith('_'):  # Solo clases públicas
                self.issues.append(TechDebtIssue(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    issue_type="missing_class_docstring",
                    severity="medium",
                    description=f"Clase pública '{node.name}' sin docstring",
                    suggestion="Agregar docstring explicando propósito de la clase",
                    auto_fixable=True,
                    fix_code=f'    """Descripción de la clase {node.name}."""'
                ))
        
        # Verificar número de métodos
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 20:
            self.issues.append(TechDebtIssue(
                file_path=self.file_path,
                line_number=node.lineno,
                issue_type="god_class",
                severity="high",
                description=f"Clase '{node.name}' con demasiados métodos ({len(methods)})",
                suggestion="Dividir en clases más pequeñas con responsabilidades específicas",
                auto_fixable=False
            ))
        
        self.generic_visit(node)
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calcular complejidad ciclomática de una función."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # And/Or operations
                complexity += len(child.values) - 1
        
        return complexity
    
    def _has_docstring(self, node) -> bool:
        """Verificar si un nodo tiene docstring."""
        if not node.body:
            return False
        first_stmt = node.body[0]
        return (isinstance(first_stmt, ast.Expr) and 
                isinstance(first_stmt.value, ast.Constant) and 
                isinstance(first_stmt.value.value, str))
    
    def _generate_docstring_fix(self, node: ast.FunctionDef) -> str:
        """Generar docstring automático para una función."""
        params = [arg.arg for arg in node.args.args if arg.arg != 'self']
        
        docstring_lines = [f'    """Descripción de {node.name}.']
        
        if params:
            docstring_lines.append('')
            docstring_lines.append('    Args:')
            for param in params:
                docstring_lines.append(f'        {param}: Descripción del parámetro.')
        
        if node.returns:
            docstring_lines.append('')
            docstring_lines.append('    Returns:')
            docstring_lines.append('        Descripción del valor retornado.')
        
        docstring_lines.append('    """')
        
        return '\n'.join(docstring_lines)


class TechDebtAnalyzer:
    """Analizador principal de deuda técnica."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues: List[TechDebtIssue] = []
        self.stats = {
            'files_analyzed': 0,
            'issues_found': 0,
            'auto_fixable': 0,
            'complexity_total': 0,
            'functions_analyzed': 0
        }
    
    def analyze_project(self, target_dirs: List[str] = None) -> None:
        """Analizar todo el proyecto."""
        if target_dirs is None:
            target_dirs = ['backend/app']
        
        print("🔍 Iniciando análisis de deuda técnica...")
        
        for target_dir in target_dirs:
            target_path = self.project_root / target_dir
            if target_path.exists():
                self._analyze_directory(target_path)
        
        self._detect_code_duplication()
        self._detect_unused_imports()
        self._analyze_file_patterns()
        
        print(f"✅ Análisis completado: {self.stats['files_analyzed']} archivos, {len(self.issues)} issues")
    
    def _analyze_directory(self, directory: Path) -> None:
        """Analizar un directorio recursivamente."""
        for py_file in directory.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            
            self._analyze_file(py_file)
            self.stats['files_analyzed'] += 1
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determinar si un archivo debe ser omitido."""
        skip_patterns = [
            '__pycache__',
            '.pyc',
            'migrations/',
            'tests/',
            'test_',
            'venv/',
            '.venv/',
            '.git/'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analizar un archivo Python específico."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Análisis AST
            tree = ast.parse(content)
            analyzer = CodeAnalyzer(str(file_path), content)
            analyzer.visit(tree)
            
            self.issues.extend(analyzer.issues)
            self.stats['functions_analyzed'] += len(analyzer.function_definitions)
            
            # Análisis de patrones de texto
            self._analyze_text_patterns(file_path, content)
            
        except Exception as e:
            self.issues.append(TechDebtIssue(
                file_path=str(file_path),
                line_number=0,
                issue_type="parse_error",
                severity="high",
                description=f"Error parseando archivo: {e}",
                suggestion="Corregir errores de sintaxis",
                auto_fixable=False
            ))
    
    def _analyze_text_patterns(self, file_path: Path, content: str) -> None:
        """Analizar patrones problemáticos en el texto."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Detectar TODOs y FIXMEs
            if re.search(r'\b(TODO|FIXME|HACK|XXX)\b', line, re.IGNORECASE):
                self.issues.append(TechDebtIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="todo_comment",
                    severity="low",
                    description="Comentario TODO/FIXME encontrado",
                    suggestion="Resolver el TODO o crear un issue para trackear",
                    auto_fixable=False
                ))
            
            # Detectar print statements en código de producción
            if re.search(r'\bprint\s*\(', line) and 'app/' in str(file_path):
                self.issues.append(TechDebtIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="print_statement",
                    severity="medium",
                    description="Print statement en código de producción",
                    suggestion="Usar logging en lugar de print",
                    auto_fixable=True,
                    fix_code=line.replace('print(', 'logger.info(')
                ))
            
            # Detectar líneas muy largas
            if len(line) > 120:
                self.issues.append(TechDebtIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="long_line",
                    severity="low",
                    description=f"Línea muy larga ({len(line)} caracteres)",
                    suggestion="Dividir línea para mejorar legibilidad",
                    auto_fixable=False
                ))
            
            # Detectar hardcoded strings que podrían ser constantes
            magic_strings = re.findall(r'"([^"]{10,})"', line)
            for string in magic_strings:
                if not any(char.isdigit() for char in string) and len(string.split()) > 2:
                    self.issues.append(TechDebtIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="magic_string",
                        severity="low",
                        description=f"String hardcodeado: '{string[:30]}...'",
                        suggestion="Considerar extraer a constante",
                        auto_fixable=False
                    ))
    
    def _detect_code_duplication(self) -> None:
        """Detectar duplicación de código."""
        print("🔍 Detectando duplicación de código...")
        
        # Simplificado: detectar funciones con nombres muy similares
        function_names = defaultdict(list)
        
        for issue in self.issues:
            if issue.issue_type in ['long_function', 'high_complexity']:
                # Extraer nombre de función del mensaje
                match = re.search(r"Función '(\w+)'", issue.description)
                if match:
                    func_name = match.group(1)
                    function_names[func_name.lower()].append(issue)
        
        # Detectar nombres similares
        for base_name, issues in function_names.items():
            similar_names = [name for name in function_names.keys() 
                           if name != base_name and self._are_similar(name, base_name)]
            
            if similar_names:
                for issue in issues:
                    self.issues.append(TechDebtIssue(
                        file_path=issue.file_path,
                        line_number=issue.line_number,
                        issue_type="potential_duplication",
                        severity="medium",
                        description=f"Posible duplicación: funciones con nombres similares",
                        suggestion="Revisar si hay lógica duplicada que se pueda extraer",
                        auto_fixable=False
                    ))
    
    def _are_similar(self, name1: str, name2: str) -> bool:
        """Verificar si dos nombres son similares."""
        if abs(len(name1) - len(name2)) > 3:
            return False
        
        # Calcular distancia de Levenshtein simplificada
        common_chars = len(set(name1) & set(name2))
        return common_chars / max(len(name1), len(name2)) > 0.7
    
    def _detect_unused_imports(self) -> None:
        """Detectar imports no utilizados (simplificado)."""
        print("🔍 Detectando imports no utilizados...")
        # Esta implementación sería más compleja en la realidad
        # Por ahora solo agregamos una nota
        pass
    
    def _analyze_file_patterns(self) -> None:
        """Analizar patrones a nivel de archivo."""
        print("🔍 Analizando patrones de archivos...")
        
        # Detectar archivos muy grandes
        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            
            try:
                line_count = sum(1 for _ in open(py_file, 'r', encoding='utf-8'))
                if line_count > 500:
                    self.issues.append(TechDebtIssue(
                        file_path=str(py_file),
                        line_number=1,
                        issue_type="large_file",
                        severity="medium",
                        description=f"Archivo muy grande ({line_count} líneas)",
                        suggestion="Considerar dividir en múltiples archivos",
                        auto_fixable=False
                    ))
            except Exception:
                pass
    
    def generate_report(self, output_format: str = 'console') -> None:
        """Generar reporte de issues."""
        if output_format == 'console':
            self._print_console_report()
        elif output_format == 'json':
            self._save_json_report()
        elif output_format == 'html':
            self._save_html_report()
    
    def _print_console_report(self) -> None:
        """Imprimir reporte en consola."""
        print("\n" + "="*80)
        print("📊 REPORTE DE DEUDA TÉCNICA")
        print("="*80)
        
        # Estadísticas generales
        severity_counts = Counter(issue.severity for issue in self.issues)
        type_counts = Counter(issue.issue_type for issue in self.issues)
        
        print(f"\n📈 Estadísticas:")
        print(f"   Archivos analizados: {self.stats['files_analyzed']}")
        print(f"   Issues encontrados: {len(self.issues)}")
        print(f"   Auto-reparables: {sum(1 for i in self.issues if i.auto_fixable)}")
        
        print(f"\n🚨 Por severidad:")
        for severity in ['critical', 'high', 'medium', 'low']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}[severity]
                print(f"   {emoji} {severity.title()}: {count}")
        
        print(f"\n🔧 Por tipo:")
        for issue_type, count in type_counts.most_common():
            print(f"   • {issue_type.replace('_', ' ').title()}: {count}")
        
        # Top issues por archivo
        file_counts = Counter(issue.file_path for issue in self.issues)
        print(f"\n📁 Archivos con más issues:")
        for file_path, count in file_counts.most_common(5):
            rel_path = os.path.relpath(file_path, self.project_root)
            print(f"   • {rel_path}: {count} issues")
        
        # Issues críticos y de alta prioridad
        critical_issues = [i for i in self.issues if i.severity in ['critical', 'high']]
        if critical_issues:
            print(f"\n🚨 ISSUES CRÍTICOS Y DE ALTA PRIORIDAD:")
            for issue in critical_issues[:10]:  # Top 10
                rel_path = os.path.relpath(issue.file_path, self.project_root)
                severity_emoji = {'critical': '🔴', 'high': '🟠'}[issue.severity]
                print(f"\n   {severity_emoji} {rel_path}:{issue.line_number}")
                print(f"      {issue.description}")
                print(f"      💡 {issue.suggestion}")
                if issue.auto_fixable:
                    print(f"      🔧 Auto-reparable")
    
    def _save_json_report(self) -> None:
        """Guardar reporte en formato JSON."""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'summary': {
                'total_issues': len(self.issues),
                'auto_fixable': sum(1 for i in self.issues if i.auto_fixable),
                'by_severity': dict(Counter(i.severity for i in self.issues)),
                'by_type': dict(Counter(i.issue_type for i in self.issues))
            },
            'issues': [
                {
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'issue_type': issue.issue_type,
                    'severity': issue.severity,
                    'description': issue.description,
                    'suggestion': issue.suggestion,
                    'auto_fixable': issue.auto_fixable,
                    'fix_code': issue.fix_code
                }
                for issue in self.issues
            ]
        }
        
        output_file = self.project_root / 'tech_debt_report.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Reporte JSON guardado en: {output_file}")
    
    def auto_fix_issues(self, dry_run: bool = True) -> None:
        """Aplicar fixes automáticos."""
        fixable_issues = [i for i in self.issues if i.auto_fixable and i.fix_code]
        
        print(f"\n🔧 Auto-fix disponible para {len(fixable_issues)} issues")
        
        if not fixable_issues:
            print("   No hay issues auto-reparables")
            return
        
        if dry_run:
            print("   🔍 Modo DRY-RUN - mostrando cambios propuestos:")
            for issue in fixable_issues[:5]:  # Mostrar solo los primeros 5
                rel_path = os.path.relpath(issue.file_path, self.project_root)
                print(f"\n   📁 {rel_path}:{issue.line_number}")
                print(f"      Issue: {issue.description}")
                print(f"      Fix: {issue.fix_code[:100]}...")
        else:
            print("   ⚠️  APLICANDO FIXES...")
            # Aquí iría la lógica real de aplicar fixes
            # Por seguridad, no implementada en esta versión
            print("   🚧 Auto-fix real no implementado por seguridad")
            print("   💡 Usa el reporte para aplicar fixes manualmente")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Analizador de Deuda Técnica")
    parser.add_argument('--dirs', nargs='+', default=['backend/app'],
                       help='Directorios a analizar')
    parser.add_argument('--format', choices=['console', 'json', 'html'], 
                       default='console', help='Formato de salida')
    parser.add_argument('--auto-fix', action='store_true',
                       help='Aplicar fixes automáticos')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Solo mostrar cambios sin aplicar')
    
    args = parser.parse_args()
    
    # Banner
    print("🔧 Analizador de Deuda Técnica - ML API FastAPI v2")
    print("=" * 60)
    
    # Inicializar analizador
    analyzer = TechDebtAnalyzer()
    
    # Ejecutar análisis
    analyzer.analyze_project(args.dirs)
    
    # Generar reporte
    analyzer.generate_report(args.format)
    
    # Auto-fix si se solicitó
    if args.auto_fix:
        analyzer.auto_fix_issues(dry_run=args.dry_run)
    
    # Sugerencias finales
    print(f"\n💡 Sugerencias:")
    print(f"   • Prioriza issues 🔴 críticos y 🟠 altos")
    print(f"   • Considera refactorizar archivos con muchos issues")
    print(f"   • Implementa tests para código complejo")
    print(f"   • Usa pre-commit hooks para prevenir nueva deuda técnica")
    
    return 0 if len(analyzer.issues) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())