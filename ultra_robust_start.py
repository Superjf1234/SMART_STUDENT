#!/usr/bin/env python3
"""
Script de inicio ultra-robusto para Railway - VERSIÓN CORREGIDA
"""
import os
import sys
import subprocess

def setup_environment():
    """Configurar variables de entorno optimizadas para Railway."""
    print("=== RAILWAY DEPLOYMENT - ULTRA ROBUST START (DIRECTORY FIXED) ===")
    
    # Variables de entorno críticas
    os.environ["PORT"] = os.environ.get("PORT", "8080")
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PYTHONPATH"] = "/app:/app/mi_app_estudio"
    
    # Configuraciones de memoria y desarrollo
    os.environ["NODE_OPTIONS"] = "--max-old-space-size=256"
    os.environ["NODE_ENV"] = "development"
    os.environ["REFLEX_ENV"] = "dev"
    os.environ["NEXT_TELEMETRY_DISABLED"] = "1"
    
    print(f"PORT: {os.environ['PORT']}")
    print(f"HOST: {os.environ['HOST']}")
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Contents: {os.listdir('.')}")

def test_config():
    """Verificar que rxconfig.py existe en el directorio actual."""
    if not os.path.exists("rxconfig.py"):
        print("❌ ERROR: rxconfig.py not found in current directory")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files: {os.listdir('.')}")
        return False
    print("✅ rxconfig.py found")
    return True

def test_import():
    """Probar importación del módulo principal."""
    try:
        print("Testing app import...")
        import mi_app_estudio.mi_app_estudio
        print("✅ App import successful")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    setup_environment()
    
    # CRÍTICO: NO cambiar de directorio - quedarse en /app donde está rxconfig.py
    if not test_config():
        print("FATAL ERROR: Configuration file not found")
        sys.exit(1)
    
    if not test_import():
        print("FATAL ERROR: Cannot import application")
        sys.exit(1)
    
    port = os.environ["PORT"]
    host = os.environ["HOST"]
    
    # Comando corregido - ejecutar desde directorio raíz
    try:
        print("Starting Reflex in development mode from root directory...")
        cmd = [
            sys.executable, "-m", "reflex", "run",
            "--env", "dev",
            "--backend-host", host,
            "--backend-port", port
        ]
        print(f"Executing: {' '.join(cmd)}")
        
        # Usar subprocess.run en lugar de execvpe para mejor control
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Reflex execution failed: {e}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
