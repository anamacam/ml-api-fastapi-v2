"""
Test TDD simple para health check.
"""

import pytest


def test_health_check_module_exists():
    """Test 1: Verificar que el módulo health existe."""
    # Este test debe fallar primero (RED)
    from app.utils import health

    assert health is not None
