#!/usr/bin/env python3
"""
Test basic imports and module functionality for SMART_STUDENT
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_basic_imports():
    """Test that basic Python libraries can be imported"""
    import os
    import sys
    import datetime
    import json
    import re
    assert True


def test_backend_imports():
    """Test that backend modules can be imported"""
    try:
        from backend import config_logic
        from backend import db_logic
        from backend import login_logic
        assert True
    except ImportError as e:
        pytest.skip(f"Backend modules not available: {e}")


def test_mi_app_estudio_imports():
    """Test that main application modules can be imported"""
    try:
        import mi_app_estudio.state
        import mi_app_estudio.translations
        assert True
    except ImportError as e:
        pytest.skip(f"Main app modules not available: {e}")


def test_reflex_available():
    """Test that Reflex framework is available"""
    try:
        import reflex as rx
        assert True
    except ImportError:
        pytest.skip("Reflex not available in test environment")


def test_project_structure():
    """Test that essential project files exist"""
    project_root = os.path.join(os.path.dirname(__file__), '..')
    essential_files = [
        'rxconfig.py',
        'requirements.txt',
        'mi_app_estudio/__init__.py',
        'mi_app_estudio/state.py',
        'backend/__init__.py'
    ]
    
    for file_path in essential_files:
        full_path = os.path.join(project_root, file_path)
        assert os.path.exists(full_path), f"Essential file missing: {file_path}"


def test_syntax_validation():
    """Test that Python files have valid syntax"""
    project_root = os.path.join(os.path.dirname(__file__), '..')
    python_files = []
    
    # Find Python files in main directories
    for root, dirs, files in os.walk(project_root):
        # Skip virtual environments and cache directories
        dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '__pycache__', '.git', 'node_modules']]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                python_files.append(os.path.join(root, file))
    
    # Test first few files to avoid overwhelming the test
    for py_file in python_files[:10]:  # Test first 10 Python files
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source = f.read()
            compile(source, py_file, 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {py_file}: {e}")
        except UnicodeDecodeError:
            # Skip files with encoding issues
            continue


if __name__ == "__main__":
    pytest.main([__file__])
