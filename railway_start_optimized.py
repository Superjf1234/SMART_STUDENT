#!/usr/bin/env python3
"""
Script de inicio optimizado para Railway
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Configurar variables de entorno para Railway"""
    # Detectar si estamos en Railway
    is_railway = os.getenv("RAILWAY_ENVIRONMENT_NAME") is not None
    
    if is_railway:
        print("🚂 DETECTADO: Entorno Railway")
        
        # Configurar para producción
        os.environ["REFLEX_ENV"] = "prod"
        os.environ["NODE_ENV"] = "production"
        os.environ["PYTHONPATH"] = "/app"
        
        # Puerto dinámico de Railway
        port = os.getenv("PORT", "8080")
        os.environ["PORT"] = port
        
        print(f"✅ Puerto configurado: {port}")
        print(f"✅ REFLEX_ENV: {os.getenv('REFLEX_ENV')}")
        print(f"✅ PYTHONPATH: {os.getenv('PYTHONPATH')}")
    else:
        print("💻 DETECTADO: Entorno local")
        os.environ["REFLEX_ENV"] = "dev"
        os.environ["PORT"] = "3000"

def run_reflex():
    """Ejecutar Reflex con la configuración correcta"""
    port = os.getenv("PORT", "8080")
    env = os.getenv("REFLEX_ENV", "dev")
    
    if env == "prod":
        # Comando para producción (Railway)
        cmd = [
            sys.executable, "-m", "reflex", "run",
            "--env", "prod",
            "--backend-host", "0.0.0.0",
            "--backend-port", port
        ]
    else:
        # Comando para desarrollo local
        cmd = [
            sys.executable, "-m", "reflex", "run",
            "--env", "dev"
        ]
    
    print(f"🚀 Ejecutando: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando Reflex: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("⚡ Aplicación detenida por el usuario")
        sys.exit(0)

if __name__ == "__main__":
    setup_environment()
    run_reflex()
