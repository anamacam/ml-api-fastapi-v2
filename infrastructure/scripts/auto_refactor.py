#!/usr/bin/env python3
"""
🔄 Auto-Refactor ML API FastAPI v2
Script para aplicar refactorings automáticos comunes.
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
import argparse
import tempfile
import shutil
from dataclasses import dataclass


@dataclass
class RefactorAction:
    """Acción de refactoring a aplicar."""
    file_path: str
    line_number: int
    action_type: str
    old_code: str
    new_code: str
    description: str


class AutoRefactor:
    """Refactorizador automático."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.actions: List[RefactorAction] = []
        self.backup_dir = self.project_root / ".refactor_backup"
    
    def analyze_and_refactor(self, target_dirs: List[str], dry_run: bool = True) -> None:
        """Analizar y aplicar refactorings."""
        print("🔄 Iniciando análisis para refactoring...")
        
        for target_dir in target_dirs:
            target_path = self.project_root / target_dir
            if target_path.exists():
                self._analyze_directory(target_path)
        
        print(f"📋 Encontradas {len(self.actions)} acciones de refactoring")
        
        if not dry_run:
            self._create_backup()
            self._apply_refactorings()
        else:
            self._show_preview()
    
    def _analyze_directory(self, directory: Path) -> None:
        """Analizar directorio para refactorings."""
        for py_file in directory.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            
            self._analyze_file(py_file)
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determinar si omitir archivo."""
        skip_patterns = [
            '__pycache__', '.pyc', 'migrations/', 'tests/', 'test_',
            'venv/', '.venv/', '.git/', '.refactor_backup/'
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analizar archivo para refactorings."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Aplicar diferentes tipos de refactoring
            self._detect_long_parameter_lists(file_path, content, lines)
            self._detect_magic_numbers(file_path, content, lines)
            self._detect_duplicated_string_literals(file_path, content, lines)
            self._detect_nested_conditions(file_path, content, lines)
            self._detect_large_functions(file_path, content)
            self._detect_unused_variables(file_path, content)
            
        except Exception as e:
            print(f"⚠️  Error analizando {file_path}: {e}")
    
    def _detect_long_parameter_lists(self, file_path: Path, content: str, lines: List[str]) -> None:
        """Detectar listas largas de parámetros."""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    args_count = len(node.args.args)
                    if args_count > 5:
                        # Generar refactoring a dataclass
                        params = [arg.arg for arg in node.args.args if arg.arg != 'self']
                        
                        # Crear dataclass
                        dataclass_name = f"{node.name.title()}Params"
                        dataclass_code = self._generate_dataclass(dataclass_name, params)
                        
                        # Nueva signature de función
                        new_signature = f"def {node.name}(self, params: {dataclass_name}):" if 'self' in [arg.arg for arg in node.args.args] else f"def {node.name}(params: {dataclass_name}):"
                        
                        self.actions.append(RefactorAction(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            action_type="extract_parameter_object",
                            old_code=f"def {node.name}(...)",
                            new_code=f"{dataclass_code}\n\n{new_signature}",
                            description=f"Extraer parámetros de '{node.name}' a dataclass"
                        ))
        except Exception as e:
            pass
    
    def _detect_magic_numbers(self, file_path: Path, content: str, lines: List[str]) -> None:
        """Detectar números mágicos."""
        magic_number_pattern = r'\b(\d{2,})\b'  # Números de 2+ dígitos
        
        for i, line in enumerate(lines, 1):
            # Evitar comentarios y strings
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                continue
            
            matches = re.finditer(magic_number_pattern, line)
            for match in matches:
                number = match.group(1)
                # Evitar números comunes que no son mágicos
                if number in ['100', '200', '404', '500', '1000', '10', '20', '30']:
                    continue
                
                constant_name = f"CONSTANT_{number}"
                
                self.actions.append(RefactorAction(
                    file_path=str(file_path),
                    line_number=i,
                    action_type="extract_constant",
                    old_code=line.strip(),
                    new_code=f"# Agregar al inicio del archivo:\n{constant_name} = {number}\n# Y reemplazar en línea {i}:\n{line.replace(number, constant_name)}",
                    description=f"Extraer número mágico {number} a constante"
                ))
    
    def _detect_duplicated_string_literals(self, file_path: Path, content: str, lines: List[str]) -> None:
        """Detectar strings literales duplicados."""
        string_counts = {}
        string_locations = {}
        
        for i, line in enumerate(lines, 1):
            # Buscar strings entre comillas
            strings = re.findall(r'"([^"]{5,})"', line)  # Strings de 5+ caracteres
            strings.extend(re.findall(r"'([^']{5,})'", line))
            
            for string in strings:
                if string not in string_counts:
                    string_counts[string] = 0
                    string_locations[string] = []
                
                string_counts[string] += 1
                string_locations[string].append(i)
        
        # Crear acciones para strings duplicados
        for string, count in string_counts.items():
            if count > 2:  # Duplicado 3+ veces
                constant_name = f"MSG_{string[:20].upper().replace(' ', '_').replace('-', '_')}"
                
                self.actions.append(RefactorAction(
                    file_path=str(file_path),
                    line_number=string_locations[string][0],
                    action_type="extract_string_constant",
                    old_code=f'"{string}"',
                    new_code=f"{constant_name} = \"{string}\"",
                    description=f"Extraer string duplicado ({count} veces) a constante"
                ))
    
    def _detect_nested_conditions(self, file_path: Path, content: str, lines: List[str]) -> None:
        """Detectar condiciones anidadas complejas."""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    nesting_level = self._calculate_nesting_level(node)
                    if nesting_level > 3:
                        self.actions.append(RefactorAction(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            action_type="reduce_nesting",
                            old_code=f"def {node.name}(...)",
                            new_code="# Usar early returns y extract methods",
                            description=f"Reducir anidamiento en '{node.name}' (nivel {nesting_level})"
                        ))
        except Exception:
            pass
    
    def _detect_large_functions(self, file_path: Path, content: str) -> None:
        """Detectar funciones grandes."""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_length = (node.end_lineno or 0) - node.lineno
                    if func_length > 30:
                        self.actions.append(RefactorAction(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            action_type="extract_method",
                            old_code=f"def {node.name}(...)",
                            new_code="# Dividir en funciones más pequeñas",
                            description=f"Extraer métodos de función grande '{node.name}' ({func_length} líneas)"
                        ))
        except Exception:
            pass
    
    def _detect_unused_variables(self, file_path: Path, content: str) -> None:
        """Detectar variables no utilizadas (simplificado)."""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Detectar variables asignadas pero no usadas
                    assigned_vars = set()
                    used_vars = set()
                    
                    for child in ast.walk(node):
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name):
                                    assigned_vars.add(target.id)
                        elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                            used_vars.add(child.id)
                    
                    unused_vars = assigned_vars - used_vars
                    for var in unused_vars:
                        if not var.startswith('_'):  # Evitar variables intencionalmente no usadas
                            self.actions.append(RefactorAction(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                action_type="remove_unused_variable",
                                old_code=f"variable '{var}'",
                                new_code="# Remover variable no utilizada",
                                description=f"Remover variable no utilizada '{var}' en '{node.name}'"
                            ))
        except Exception:
            pass
    
    def _generate_dataclass(self, class_name: str, params: List[str]) -> str:
        """Generar código de dataclass."""
        dataclass_lines = [
            "@dataclass",
            f"class {class_name}:",
            '    """Parámetros agrupados."""'
        ]
        
        for param in params:
            dataclass_lines.append(f"    {param}: Any  # Especificar tipo apropiado")
        
        return "\n".join(dataclass_lines)
    
    def _calculate_nesting_level(self, node: ast.FunctionDef) -> int:
        """Calcular nivel máximo de anidamiento."""
        max_nesting = 0
        
        def calculate_depth(node, current_depth=0):
            nonlocal max_nesting
            max_nesting = max(max_nesting, current_depth)
            
            nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try)
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, nesting_nodes):
                    calculate_depth(child, current_depth + 1)
                else:
                    calculate_depth(child, current_depth)
        
        calculate_depth(node)
        return max_nesting
    
    def _create_backup(self) -> None:
        """Crear backup antes de refactorizar."""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        self.backup_dir.mkdir()
        
        # Copiar archivos que serán modificados
        files_to_backup = set(action.file_path for action in self.actions)
        
        for file_path in files_to_backup:
            src = Path(file_path)
            if src.exists():
                rel_path = src.relative_to(self.project_root)
                dst = self.backup_dir / rel_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        
        print(f"📦 Backup creado en: {self.backup_dir}")
    
    def _apply_refactorings(self) -> None:
        """Aplicar refactorings (implementación básica)."""
        print("🔧 Aplicando refactorings...")
        
        applied_count = 0
        for action in self.actions:
            if action.action_type in ['extract_constant', 'extract_string_constant']:
                # Solo algunos refactorings automáticos seguros
                if self._apply_constant_extraction(action):
                    applied_count += 1
        
        print(f"✅ {applied_count} refactorings aplicados")
        print("💡 Revisa los cambios y usa git para confirmar")
    
    def _apply_constant_extraction(self, action: RefactorAction) -> bool:
        """Aplicar extracción de constantes."""
        try:
            file_path = Path(action.file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Agregar constante al inicio del archivo (después de imports)
            insert_line = 0
            for i, line in enumerate(lines):
                if not (line.strip().startswith('#') or 
                       line.strip().startswith('import') or 
                       line.strip().startswith('from') or
                       line.strip() == ''):
                    insert_line = i
                    break
            
            # Extraer información de la acción
            if 'CONSTANT_' in action.new_code:
                constant_def = action.new_code.split('\n')[1]  # Línea con la definición
                lines.insert(insert_line, constant_def + '\n')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
        except Exception as e:
            print(f"⚠️  Error aplicando refactoring en {action.file_path}: {e}")
            return False
    
    def _show_preview(self) -> None:
        """Mostrar preview de refactorings."""
        print("\n" + "="*80)
        print("🔍 PREVIEW DE REFACTORINGS")
        print("="*80)
        
        # Agrupar por tipo
        by_type = {}
        for action in self.actions:
            if action.action_type not in by_type:
                by_type[action.action_type] = []
            by_type[action.action_type].append(action)
        
        for refactor_type, actions in by_type.items():
            print(f"\n🔧 {refactor_type.replace('_', ' ').title()} ({len(actions)} acciones):")
            
            for action in actions[:3]:  # Mostrar solo primeras 3
                rel_path = os.path.relpath(action.file_path, self.project_root)
                print(f"   📁 {rel_path}:{action.line_number}")
                print(f"      {action.description}")
                print(f"      💻 {action.old_code[:50]}..." if len(action.old_code) > 50 else f"      💻 {action.old_code}")
            
            if len(actions) > 3:
                print(f"   ... y {len(actions) - 3} más")
    
    def generate_refactor_plan(self) -> None:
        """Generar plan de refactoring detallado."""
        plan_file = self.project_root / "REFACTOR_PLAN.md"
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write("# 🔄 Plan de Refactoring\n\n")
            f.write(f"Generado automáticamente - {len(self.actions)} acciones identificadas\n\n")
            
            # Agrupar por tipo
            by_type = {}
            for action in self.actions:
                if action.action_type not in by_type:
                    by_type[action.action_type] = []
                by_type[action.action_type].append(action)
            
            for refactor_type, actions in by_type.items():
                f.write(f"## {refactor_type.replace('_', ' ').title()}\n\n")
                f.write(f"**{len(actions)} acciones identificadas**\n\n")
                
                for action in actions:
                    rel_path = os.path.relpath(action.file_path, self.project_root)
                    f.write(f"### `{rel_path}:{action.line_number}`\n\n")
                    f.write(f"**Descripción**: {action.description}\n\n")
                    f.write(f"**Código actual**:\n```python\n{action.old_code}\n```\n\n")
                    f.write(f"**Refactoring sugerido**:\n```python\n{action.new_code}\n```\n\n")
                    f.write("---\n\n")
        
        print(f"📋 Plan de refactoring guardado en: {plan_file}")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Auto-Refactor para ML API")
    parser.add_argument('--dirs', nargs='+', default=['backend/app'],
                       help='Directorios a analizar')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Solo mostrar preview sin aplicar cambios')
    parser.add_argument('--apply', action='store_true',
                       help='Aplicar refactorings (¡Crea backup automáticamente!)')
    parser.add_argument('--plan', action='store_true',
                       help='Generar plan de refactoring detallado')
    
    args = parser.parse_args()
    
    print("🔄 Auto-Refactor ML API FastAPI v2")
    print("=" * 50)
    
    refactor = AutoRefactor()
    
    # Analizar y generar acciones
    refactor.analyze_and_refactor(args.dirs, dry_run=not args.apply)
    
    # Generar plan detallado si se solicita
    if args.plan:
        refactor.generate_refactor_plan()
    
    print(f"\n💡 Consejos:")
    print(f"   • Usa --plan para generar un plan detallado")
    print(f"   • Revisa siempre los cambios antes de aplicar")
    print(f"   • Los backups se crean automáticamente")
    print(f"   • Usa git para trackear cambios")


if __name__ == "__main__":
    main()