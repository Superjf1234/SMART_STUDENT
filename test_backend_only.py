#!/usr/bin/env python3
"""
Test script para verificar que funciona backend-only
"""

import os
import sys
import subprocess

def test_backend_only():
    """Test del modo backend-only"""
    
    # Configurar entorno
    os.environ['PORT'] = '8080'
    os.environ['PYTHONPATH'] = '/workspaces/SMART_STUDENT:/workspaces/SMART_STUDENT/mi_app_estudio'
    
    # Cambiar directorio
    os.chdir('/workspaces/SMART_STUDENT/mi_app_estudio')
    
    print("=== TESTING BACKEND-ONLY MODE ===")
    print(f"Working directory: {os.getcwd()}")
    print(f"PORT: {os.environ.get('PORT')}")
    
    # Test de importación
    try:
        sys.path.insert(0, '/workspaces/SMART_STUDENT')
        sys.path.insert(0, '/workspaces/SMART_STUDENT/mi_app_estudio')
        import mi_app_estudio.mi_app_estudio
        print("✓ Import successful")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    # Test del comando
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-only',
        '--backend-host', '0.0.0.0',
        '--backend-port', '8080',
        '--env', 'prod',
        '--no-frontend'  # Ensure no frontend
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("This should start only the backend server...")
    
    return True

if __name__ == '__main__':
    test_backend_only()
