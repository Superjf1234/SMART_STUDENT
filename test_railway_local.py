#!/usr/bin/env python3
"""
Script de prueba local para simular el entorno de Railway
"""
import os
import sys
import subprocess
import time
from pathlib import Path
import pytest

def setup_railway_env():
    """Configurar variables de entorno como en Railway"""
    os.environ['PORT'] = '8080'
    os.environ['RAILWAY_ENVIRONMENT'] = 'production'
    os.environ['REFLEX_ENV'] = 'prod'
    os.environ['PYTHONPATH'] = '/workspaces/SMART_STUDENT'
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=256'
    
    # Verificar GEMINI_API_KEY
    if 'GEMINI_API_KEY' not in os.environ:
        print("⚠ GEMINI_API_KEY no está configurada, usando clave de prueba")
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"

# Configurar entorno antes de los tests
setup_railway_env()

def test_imports():
    """Probar que todas las importaciones funcionan"""
    print("Probando importaciones...")
    
    # Importar Reflex
    import reflex as rx
    print("✓ Reflex importado correctamente")
    
    # Importar paquete principal
    import mi_app_estudio
    print("✓ Paquete mi_app_estudio importado")
    
    # Importar módulo principal
    from mi_app_estudio import mi_app_estudio
    print("✓ Módulo principal importado")
    
    # Verificar que la app existe
    assert hasattr(mi_app_estudio, 'app'), "Objeto app no encontrado"
    print("✓ Objeto app encontrado")

def test_reflex_init():
    """Probar la inicialización de Reflex"""
    print("Probando inicialización de Reflex...")
    
    # Ejecutar reflex init si es necesario
    if not os.path.exists('.web'):
        print("Ejecutando reflex init...")
        result = subprocess.run(
            [sys.executable, '-m', 'reflex', 'init', '--template', 'blank'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode == 0, f"Reflex init falló: {result.stderr}"
        print("✓ Reflex init exitoso")
    else:
        print("✓ Reflex ya inicializado")


