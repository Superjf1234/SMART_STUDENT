#!/usr/bin/env python3
"""
Test configuration and setup for SMART_STUDENT
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_requirements_file_exists():
    """Test that requirements.txt exists and is readable"""
    requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    assert os.path.exists(requirements_path), "requirements.txt not found"
    
    with open(requirements_path, 'r') as f:
        content = f.read()
        assert len(content) > 0, "requirements.txt is empty"
        assert 'reflex' in content.lower(), "Reflex not found in requirements"


def test_rxconfig_exists():
    """Test that rxconfig.py exists and contains basic configuration"""
    rxconfig_path = os.path.join(os.path.dirname(__file__), '..', 'rxconfig.py')
    assert os.path.exists(rxconfig_path), "rxconfig.py not found"
    
    with open(rxconfig_path, 'r') as f:
        content = f.read()
        assert 'app_name' in content, "app_name not found in rxconfig.py"


def test_main_app_file_exists():
    """Test that main application file exists"""
    main_app_path = os.path.join(os.path.dirname(__file__), '..', 'mi_app_estudio', 'mi_app_estudio.py')
    assert os.path.exists(main_app_path), "Main application file not found"


def test_state_file_exists():
    """Test that state.py exists"""
    state_path = os.path.join(os.path.dirname(__file__), '..', 'mi_app_estudio', 'state.py')
    assert os.path.exists(state_path), "state.py not found"


def test_backend_directory_exists():
    """Test that backend directory exists with required files"""
    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
    assert os.path.exists(backend_path), "backend directory not found"
    assert os.path.isdir(backend_path), "backend is not a directory"


def test_assets_directory_exists():
    """Test that assets directory exists"""
    assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
    assert os.path.exists(assets_path), "assets directory not found"


def test_dockerfile_exists():
    """Test that Dockerfile exists for deployment"""
    dockerfile_path = os.path.join(os.path.dirname(__file__), '..', 'Dockerfile')
    assert os.path.exists(dockerfile_path), "Dockerfile not found"


if __name__ == "__main__":
    pytest.main([__file__])
