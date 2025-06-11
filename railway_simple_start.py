#!/usr/bin/env python3
"""
Script de inicio SIMPLIFICADO para Railway - SMART_STUDENT
"""
import os
import sys
import subprocess

def main():
    print("🚂 RAILWAY STARTUP - SMART STUDENT OPTIMIZADO")
    print("=" * 60)
    
    # Configurar variables críticas
    os.environ["REFLEX_ENV"] = "prod"
    os.environ["NODE_ENV"] = "production"
    os.environ["PYTHONPATH"] = "/app"
    
    # Puerto de Railway
    port = os.getenv("PORT", "8080")
    os.environ["PORT"] = port
    
    print(f"✅ Puerto: {port}")
    print(f"✅ REFLEX_ENV: prod")
    print(f"✅ PYTHONPATH: /app")
    print("=" * 60)
    
    # Comando simplificado
    cmd = [
        sys.executable, "-m", "reflex", "run",
        "--env", "prod",
        "--backend-host", "0.0.0.0",
        "--backend-port", port
    ]
    
    print(f"🚀 Ejecutando: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        # Ejecutar el comando
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Detenido por el usuario")
        sys.exit(0)

if __name__ == "__main__":
    main()
