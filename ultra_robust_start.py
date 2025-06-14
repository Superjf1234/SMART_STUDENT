#!/usr/bin/env python3
"""
Script de inicio ultra-robusto para Railway - VERSIÓN CORREGIDA
"""
import os
import sys
import subprocess

def setup_environment():
    """Configurar variables de entorno optimizadas para Railway."""
    print("=== RAILWAY DEPLOYMENT - ULTRA ROBUST START (DIRECTORY FIXED + CWD) ===")
    
    # Variables de entorno críticas
    os.environ["PORT"] = os.environ.get("PORT", "8080")
    os.environ["HOST"] = "0.0.0.0"
    # Ajustar PYTHONPATH si todos los módulos principales están en /app
    os.environ["PYTHONPATH"] = "/app" 
    
    # Configuraciones de memoria y desarrollo
    os.environ["NODE_OPTIONS"] = "--max-old-space-size=256"
    os.environ["NODE_ENV"] = "development"
    os.environ["REFLEX_ENV"] = "dev"
    os.environ["NEXT_TELEMETRY_DISABLED"] = "1"
    
    print(f"PORT: {os.environ['PORT']}")
    print(f"HOST: {os.environ['HOST']}")
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    print(f"Initial working directory: {os.getcwd()}")

def test_config(cwd_path):
    """Verificar que rxconfig.py existe en el directorio especificado."""
    config_path = os.path.join(cwd_path, "rxconfig.py")
    if not os.path.exists(config_path):
        print(f"❌ ERROR: rxconfig.py not found in {config_path}")
        print(f"Contents of {cwd_path}: {os.listdir(cwd_path)}")
        return False
    print(f"✅ rxconfig.py found in {config_path}")
    return True

def test_import(cwd_path):
    """Probar importación del módulo principal desde el directorio especificado."""
    # Añadir cwd_path a sys.path temporalmente para la prueba de importación
    original_sys_path = list(sys.path)
    sys.path.insert(0, cwd_path)
    try:
        print(f"Testing app import from {cwd_path}...")
        import app_main 
        print("✅ App import successful")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sys.path = original_sys_path # Restaurar sys.path

def main():
    """Función principal."""
    setup_environment()
    
    project_root = "/app" # Directorio raíz del proyecto en Railway

    print(f"Ensuring execution from: {project_root}")
    # No es necesario cambiar de directorio si el script se ejecuta desde la raíz
    # os.chdir(project_root) # Comentado, ya que el Dockerfile debería establecer WORKDIR /app

    if not test_config(project_root):
        print("FATAL ERROR: Configuration file not found in project root")
        sys.exit(1)
    
    # La prueba de importación es más fiable si se hace antes de cambiar PYTHONPATH globalmente
    # o si se maneja el path correctamente.
    # if not test_import(project_root):
    #     print("FATAL ERROR: Cannot import application from project root")
    #     sys.exit(1)
    
    port = os.environ["PORT"]
    host = os.environ["HOST"]
    
    try:
        print(f"Starting Reflex in development mode from {project_root}...")
        cmd = [
            sys.executable, "-m", "reflex", "run",
            "--env", "dev",
            "--backend-host", host,
            "--backend-port", port
        ]
        print(f"Executing: {' '.join(cmd)} in {project_root}")
        
        # Especificar explícitamente el directorio de trabajo para subprocess
        result = subprocess.run(cmd, check=True, cwd=project_root)
        sys.exit(result.returncode)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Reflex execution failed: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
