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
    print("=== RAILWAY DEPLOYMENT - ULTRA ROBUST START ===")
    
    # Variables de entorno críticas
    os.environ["PORT"] = os.environ.get("PORT", "8080")
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PYTHONPATH"] = "/app:/app/mi_app_estudio"
    
    # Configuraciones ultra-agresivas de memoria
    os.environ["NODE_OPTIONS"] = "--max-old-space-size=200"
    os.environ["NODE_ENV"] = "development"
    os.environ["REFLEX_ENV"] = "development"
    
    # Prevenir builds pesados
    os.environ["NEXT_TELEMETRY_DISABLED"] = "1"
    os.environ["REFLEX_SKIP_COMPILE"] = "1"
    
    print(f"PORT: {os.environ['PORT']}")
    print(f"HOST: {os.environ['HOST']}")
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    print(f"NODE_OPTIONS: {os.environ['NODE_OPTIONS']}")
    print(f"REFLEX_ENV: {os.environ['REFLEX_ENV']}")

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
    
    # Estrategia 1: Inicio normal con desarrollo forzado
    try:
        print("STRATEGY 1: Normal development start...")
        cmd = [
            sys.executable, "-m", "reflex", "run",
            "--backend-host", host,
            "--backend-port", port,
            "--env", "dev"  # Usar --env dev en lugar de --dev
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
    
    # Estrategia 3: Servidor Python directo
    print("STRATEGY 3: Direct Python server...")
    try:
        # Importar y crear la app directamente
        sys.path.insert(0, "/app")
        sys.path.insert(0, "/app/mi_app_estudio")
        
        import mi_app_estudio.mi_app_estudio as app_module
        
        # Iniciar servidor HTTP simple
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        server = HTTPServer((host, int(port)), SimpleHTTPRequestHandler)
        print(f"Direct server starting on {host}:{port}")
        server.serve_forever()
        
    except Exception as e:
        print(f"Strategy 3 failed: {e}")
        print("All strategies failed. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    start_with_fallback()
