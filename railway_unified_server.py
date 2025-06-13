#!/usr/bin/env python3
"""
Railway Unified Server - Backend sirve frontend
"""

import os
import sys
import subprocess
import time

def main():
    """Start backend that serves frontend files"""
    
    print("=== RAILWAY UNIFIED SERVER ===")
    
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
    
    print(f"Starting unified server on port: {port}")
    
    # ESTRATEGIA: Solo backend, que automáticamente sirve frontend
    cmd = [
        sys.executable, "-m", "reflex", "run",
        "--backend-host", host,
        "--backend-port", port,
        "--env", "dev"
        # NO especificar frontend-port, que Reflex maneje automáticamente
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    # Ejecutar directamente
    os.execv(sys.executable, cmd)

if __name__ == '__main__':
    sys.exit(main())
