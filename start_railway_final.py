#!/usr/bin/env python3
"""
Script final optimizado para Railway - SMART_STUDENT
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def setup_railway_environment():
    """Configurar variables de entorno específicas para Railway"""
    print("🚀 Configurando entorno Railway...")
    
    # Variable API por defecto para desarrollo
    if 'GEMINI_API_KEY' not in os.environ:
        print("⚠️  GEMINI_API_KEY no definida, usando clave por defecto")
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    
    # Puerto Railway
    port = os.environ.get('PORT', '8080')
    print(f"📡 Puerto Railway: {port}")
    
    return port

def initialize_reflex():
    """Inicializar Reflex si es necesario"""
    print("🔧 Verificando configuración Reflex...")
    
    if not Path(".web").exists():
        print("📦 Inicializando Reflex por primera vez...")
        try:
            subprocess.run(
                ["python", "-m", "reflex", "init", "--template", "blank"],
                check=True,
                timeout=120
            )
            print("✅ Reflex inicializado")
        except Exception as e:
            print(f"❌ Error inicializando Reflex: {e}")
            return False
    
    return True

def install_frontend_dependencies():
    """Instalar dependencias del frontend"""
    web_dir = Path(".web")
    package_json = web_dir / "package.json"
    node_modules = web_dir / "node_modules"
    
    if not package_json.exists():
        print("❌ package.json no encontrado, reinicializando...")
        if not initialize_reflex():
            return False
    
    if not node_modules.exists() or not list(node_modules.glob("*")):
        print("📦 Instalando dependencias frontend...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=str(web_dir),
                check=True,
                timeout=300
            )
            print("✅ Dependencias frontend instaladas")
        except Exception as e:
            print(f"⚠️  Error instalando dependencias: {e}")
            print("🔄 Intentando con bun...")
            try:
                subprocess.run(
                    ["bun", "install"],
                    cwd=str(web_dir),
                    check=True,
                    timeout=300
                )
                print("✅ Dependencias instaladas con bun")
            except Exception as e2:
                print(f"❌ Error con bun también: {e2}")
                return False
    else:
        print("✅ Dependencias frontend ya instaladas")
    
    return True

def run_reflex_app(port):
    """Ejecutar la aplicación Reflex"""
    print("🚀 Iniciando aplicación SMART_STUDENT...")
    
    # Comando optimizado para Railway
    cmd = [
        "python", "-m", "reflex", "run",
        "--env", "prod",
        "--backend-host", "0.0.0.0",
        "--backend-port", port
    ]
    
    print(f"💻 Comando: {' '.join(cmd)}")
    
    try:
        # Usar execvp para reemplazar el proceso actual
        os.execvp("python", cmd)
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    print("=" * 60)
    print("🎓 SMART_STUDENT - Iniciando en Railway")
    print("=" * 60)
    
    # Configurar entorno
    port = setup_railway_environment()
    
    # Inicializar Reflex si es necesario
    if not initialize_reflex():
        print("❌ Fallo en inicialización de Reflex")
        sys.exit(1)
    
    # Instalar dependencias frontend
    if not install_frontend_dependencies():
        print("❌ Fallo en instalación de dependencias")
        sys.exit(1)
    
    # Ejecutar aplicación
    run_reflex_app(port)

if __name__ == "__main__":
    main()
