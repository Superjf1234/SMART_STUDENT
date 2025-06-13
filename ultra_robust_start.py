#!/usr/bin/env python3
"""
Script de inicio ultra-robusto para Railway con manejo de errores de compilación.
"""
import os
import sys
import subprocess
import time

def setup_environment():
    """Configurar variables de entorno optimizadas para Railway."""
    print("=== RAILWAY DEPLOYMENT - ULTRA ROBUST START (FIXED) ===")
    
    # Variables de entorno críticas
    os.environ["PORT"] = os.environ.get("PORT", "8080")
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PYTHONPATH"] = "/app:/app/mi_app_estudio"
    
    # Configuraciones ultra-agresivas de memoria
    os.environ["NODE_OPTIONS"] = "--max-old-space-size=200"
    os.environ["NODE_ENV"] = "development"
    os.environ["REFLEX_ENV"] = "dev"  # Cambiar a 'dev' para consistencia
    
    # Prevenir builds pesados
    os.environ["NEXT_TELEMETRY_DISABLED"] = "1"
    
    print(f"PORT: {os.environ['PORT']}")
    print(f"HOST: {os.environ['HOST']}")
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    print(f"NODE_OPTIONS: {os.environ['NODE_OPTIONS']}")
    print(f"REFLEX_ENV: {os.environ['REFLEX_ENV']}")
    print(f"Working directory: {os.getcwd()}")  # Mostrar directorio actual

def test_import():
    """Probar importación del módulo principal."""
    try:
        print("Testing app import...")
        import mi_app_estudio.mi_app_estudio
        print("✓ App import successful")
        return True
    except Exception as e:
        print(f"✗ App import failed: {e}")
        return False

def start_with_fallback():
    """Iniciar con múltiples estrategias de fallback."""
    setup_environment()
    
    if not test_import():
        print("ERROR: No se puede importar la aplicación")
        sys.exit(1)
    
    port = os.environ["PORT"]
    host = os.environ["HOST"]
    
    # CRITICAL FIX: NO cambiar de directorio - rxconfig.py está en /app
    print(f"Staying in root directory: {os.getcwd()}")
    
    # Estrategia 1: Inicio normal con desarrollo forzado (SIN cambio de directorio)
    try:
        print("STRATEGY 1: Normal development start (staying in root)...")
        cmd = [
            sys.executable, "-m", "reflex", "run",
            "--backend-host", host,
            "--backend-port", port,
            "--env", "dev"  # Usar dev para evitar build pesado
        ]
        print(f"Executing: {' '.join(cmd)}")
        os.execvpe(sys.executable, cmd, os.environ)
    except Exception as e:
        print(f"Strategy 1 failed: {e}")
    
    # Estrategia 2: Inicio sin frontend (solo backend)
    try:
        print("STRATEGY 2: Backend-only start...")
        cmd = [
            sys.executable, "-m", "reflex", "run",
            "--backend-only",
            "--backend-host", host,
            "--backend-port", port
        ]
        print(f"Executing: {' '.join(cmd)}")
        os.execvpe(sys.executable, cmd, os.environ)
    except Exception as e:
        print(f"Strategy 2 failed: {e}")
    
    print("All strategies failed. Exiting.")
    sys.exit(1)

if __name__ == "__main__":
    start_with_fallback()
