#!/usr/bin/env python3
"""
Script final optimizado para Railway - SMART_STUDENT
Corrige todos los problemas identificados en los logs de Railway
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Función principal optimizada para Railway"""
    print("=== SMART_STUDENT Railway Deployment (FINAL) ===")
    
    # Configurar entorno básico
    if 'GEMINI_API_KEY' not in os.environ:
        print("ADVERTENCIA: Variable GEMINI_API_KEY no está definida")
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    
    # Railway siempre usa puerto 8080
    port = os.environ.get('PORT', '8080')
    print(f"Puerto Railway: {port}")
    
    # Verificar directorio .web
    web_dir = Path(".web")
    if not web_dir.exists():
        print("ERROR CRÍTICO: Directorio .web no existe")
        print("Ejecutando reflex init...")
        try:
            subprocess.run(["python", "-m", "reflex", "init"], check=True, timeout=60)
        except Exception as e:
            print(f"ERROR en reflex init: {e}")
            sys.exit(1)
    
    # Verificar package.json
    package_json = web_dir / "package.json"
    if not package_json.exists():
        print("ERROR: package.json no existe en .web/")
        print("Ejecutando reflex export...")
        try:
            subprocess.run(["python", "-m", "reflex", "export"], timeout=120)
        except Exception as e:
            print(f"ADVERTENCIA en reflex export: {e}")
    
    # Instalar dependencias frontend si es necesario
    node_modules = web_dir / "node_modules"
    if not node_modules.exists() and package_json.exists():
        print("Instalando dependencias frontend...")
        try:
            subprocess.run(["npm", "install"], cwd=str(web_dir), check=True, timeout=300)
            print("✅ Dependencias frontend instaladas")
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout en instalación de dependencias, continuando...")
        except Exception as e:
            print(f"⚠️ Error instalando dependencias: {e}, continuando...")
    
    # Comando corregido sin --frontend-host
    cmd = [
        "python", "-m", "reflex", "run",
        "--env", "prod",
        "--backend-host", "0.0.0.0",
        "--backend-port", port,
        "--frontend-port", port
    ]
    
    print(f"🚀 Ejecutando: {' '.join(cmd)}")
    
    # Ejecutar comando directamente
    try:
        os.execvp("python", cmd)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
