#!/usr/bin/env python3
"""
Script para verificar que las funciones públicas tengan docstrings.
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple


class DocstringChecker(ast.NodeVisitor):
    """Visitor para verificar docstrings en funciones públicas."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.errors: List[Tuple[int, str]] = []
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Verificar funciones."""
        if self._is_public_function(node):
            if not self._has_docstring(node):
                self.errors.append((
                    node.lineno,
                    f"Función pública '{node.name}' sin docstring"
                ))
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Verificar funciones async."""
        if self._is_public_function(node):
            if not self._has_docstring(node):
                self.errors.append((
                    node.lineno,
                    f"Función async pública '{node.name}' sin docstring"
                ))
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Verificar clases públicas."""
        if self._is_public_class(node):
            if not self._has_docstring(node):
                self.errors.append((
                    node.lineno,
                    f"Clase pública '{node.name}' sin docstring"
                ))
        self.generic_visit(node)
    
    def _is_public_function(self, node) -> bool:
        """Verificar si una función es pública."""
        # Funciones que empiezan con _ son privadas
        if node.name.startswith('_'):
            return False
        
        # Métodos especiales como __init__ no necesitan docstring
        if node.name.startswith('__') and node.name.endswith('__'):
            return False
        
        return True
    
    def _is_public_class(self, node: ast.ClassDef) -> bool:
        """Verificar si una clase es pública."""
        return not node.name.startswith('_')
    
    def _has_docstring(self, node) -> bool:
        """Verificar si un nodo tiene docstring."""
        if not node.body:
            return False
        
        first_stmt = node.body[0]
        return (isinstance(first_stmt, ast.Expr) and 
                isinstance(first_stmt.value, ast.Constant) and 
                isinstance(first_stmt.value.value, str))


def check_file(filepath: Path) -> List[Tuple[int, str]]:
    """Verificar docstrings en un archivo Python."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        checker = DocstringChecker(str(filepath))
        checker.visit(tree)
        return checker.errors
        
    except SyntaxError as e:
        return [(e.lineno or 0, f"Error de sintaxis: {e.msg}")]
    except Exception as e:
        return [(0, f"Error procesando archivo: {e}")]


def main():
    """Función principal."""
    backend_dir = Path("backend/app")
    
    if not backend_dir.exists():
        print("❌ Directorio backend/app no encontrado")
        return 0
    
    # Archivos a verificar
    python_files = list(backend_dir.rglob("*.py"))
    
    # Filtrar archivos que deben tener docstrings
    files_to_check = []
    for file_path in python_files:
        # Excluir __init__.py, tests, y archivos privados
        if (file_path.name == "__init__.py" or 
            "test" in file_path.name or 
            file_path.name.startswith("_")):
            continue
        files_to_check.append(file_path)
    
    total_errors = 0
    
    for file_path in files_to_check:
        errors = check_file(file_path)
        if errors:
            print(f"\n📄 {file_path}:")
            for line_no, message in errors:
                print(f"  ❌ Línea {line_no}: {message}")
                total_errors += 1
    
    if total_errors == 0:
        print("✅ Todas las funciones y clases públicas tienen docstrings")
        return 0
    else:
        print(f"\n❌ Encontrados {total_errors} problemas de docstrings")
        print("\n💡 Tip: Agrega docstrings a las funciones y clases públicas:")
        print('   def mi_funcion():')
        print('       """Descripción de la función."""')
        print('       pass')
        return 1


if __name__ == "__main__":
    sys.exit(main()) 