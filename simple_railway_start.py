#!/usr/bin/env python3
"""
SOLUCIÓN SIMPLE: Configurar GEMINI_API_KEY en el script
"""

import os
import sys

def main():
    """Script ultra-simple con GEMINI_API_KEY configurada"""
    
    print("=== SMART STUDENT - RAILWAY DEPLOYMENT ===")
    
    # Configurar variables básicas
    port = os.environ.get("PORT", "8080")
    host = "0.0.0.0"
    
    # SOLUCIÓN: Configurar GEMINI_API_KEY
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("✅ GEMINI_API_KEY configurada")
    
    # Configurar entorno
    os.environ["PYTHONPATH"] = "/app:/app/mi_app_estudio"
    os.environ["NODE_OPTIONS"] = "--max-old-space-size=400"
    
    # Cambiar directorio
    os.chdir("/app/mi_app_estudio")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Test de importación
    try:
        sys.path.insert(0, "/app")
        sys.path.insert(0, "/app/mi_app_estudio")
        import mi_app_estudio.mi_app_estudio
        print("✅ App import successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return 1
    
    print(f"🚀 Starting Reflex on port {port}")
    
    # Comando simple
    cmd = [
        sys.executable, "-m", "reflex", "run",
        "--backend-host", host,
        "--backend-port", port,
        "--env", "dev"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    # Ejecutar
    os.execv(sys.executable, cmd)

if __name__ == '__main__':
    sys.exit(main())
