#!/usr/bin/env python3
"""
Railway Minimal Start - Último intento
Enfoque ultra-minimalista para evitar conflictos de puerto
"""

import os
import sys
import subprocess
import time

def main():
    """Ultra-simple start for Railway"""
    
    print("=== RAILWAY MINIMAL START ===")
    
    port = os.environ.get("PORT", "8080")
    host = "0.0.0.0"
    
    # Setup básico
    os.environ["PYTHONPATH"] = "/app:/app/mi_app_estudio"
    os.environ["NODE_OPTIONS"] = "--max-old-space-size=512"
    
    # Cambiar directorio
    os.chdir("/app/mi_app_estudio")
    print(f"Working in: {os.getcwd()}")
    
    # Import test
    try:
        sys.path.insert(0, "/app")
        sys.path.insert(0, "/app/mi_app_estudio")
        import mi_app_estudio.mi_app_estudio
        print("✓ Import OK")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return 1
    
    # ESTRATEGIA FINAL: Usar puerto diferente para frontend
    frontend_port = str(int(port) + 1000)  # Frontend en puerto 9080
    
    print(f"Backend port: {port}")
    print(f"Frontend port: {frontend_port} (internal)")
    
    # Comando ultra-simple
    cmd = [
        sys.executable, "-m", "reflex", "run",
        "--backend-host", host,
        "--backend-port", port,
        "--frontend-port", frontend_port,  # Puerto diferente para frontend
        "--env", "dev"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    # Ejecutar directamente
    os.execv(sys.executable, cmd)

if __name__ == '__main__':
    sys.exit(main())
