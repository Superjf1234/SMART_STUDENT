#!/usr/bin/env python3
"""
Script de inicio ultra-robusto para Railway - VERSIÓN CORREGIDA
"""
import os
import sys
import subprocess

def setup_environment():
    """Configurar variables de entorno optimizadas para Railway."""
    print("=== RAILWAY DEPLOYMENT - ULTRA ROBUST START (CWD STRICT) ===")
    
    os.environ["PORT"] = os.environ.get("PORT", "8080")
    os.environ["HOST"] = "0.0.0.0"
    # Simplificar PYTHONPATH, todos los módulos principales están en /app
    os.environ["PYTHONPATH"] = "/app"
    
    os.environ["NODE_OPTIONS"] = "--max-old-space-size=256"
    os.environ["NODE_ENV"] = "development" # Forzar desarrollo para mejor depuración inicial
    os.environ["REFLEX_ENV"] = "dev"
    os.environ["NEXT_TELEMETRY_DISABLED"] = "1"
    
    print(f"PORT: {os.environ['PORT']}")
    print(f"HOST: {os.environ['HOST']}")
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    print(f"Initial working directory (at script start): {os.getcwd()}")

def test_config(path_to_check):
    """Verificar que rxconfig.py existe en el path especificado."""
    config_file = os.path.join(path_to_check, "rxconfig.py")
    print(f"Checking for rxconfig.py at: {config_file}")
    if not os.path.exists(config_file):
        print(f"❌ ERROR: rxconfig.py not found in {config_file}")
        print(f"Contents of {path_to_check}: {os.listdir(path_to_check)}")
        # Intentar listar el contenido del directorio padre si es /app/mi_app_estudio
        if path_to_check.endswith("mi_app_estudio"):
            parent_dir = os.path.dirname(path_to_check)
            if os.path.exists(parent_dir):
                 print(f"Contents of {parent_dir}: {os.listdir(parent_dir)}")
        return False
    print(f"✅ rxconfig.py found in {config_file}")
    return True

def main():
    """Función principal."""
    setup_environment()
    
    project_root = "/app" # Directorio raíz del proyecto en Railway

    # No se debe cambiar de directorio aquí. El WORKDIR del Dockerfile debe ser /app
    # y el comando reflex se ejecutará con cwd=project_root.
    print(f"Script current working directory (before Reflex command): {os.getcwd()}")

    if not test_config(project_root):
        print(f"FATAL ERROR: rxconfig.py not found in the designated project root ({project_root}).")
        # Adicionalmente, verificar si está en el CWD actual por si acaso
        if os.getcwd() != project_root:
            print(f"Also checking current working directory ({os.getcwd()})...")
            test_config(os.getcwd())
        sys.exit(1)
    
    port = os.environ["PORT"]
    host = os.environ["HOST"]
    
    # Comando para ejecutar Reflex
    # Usar --env dev para mejor depuración inicial, luego cambiar a prod
    cmd = [
        sys.executable, "-m", "reflex", "run",
        "--env", "dev", 
        "--backend-host", host,
        "--backend-port", port
    ]
    
    print(f"Attempting to execute Reflex command: {' '.join(cmd)}")
    print(f"Target execution directory (cwd for subprocess): {project_root}")
    
    try:
        # Ejecutar el comando Reflex especificando explícitamente el directorio de trabajo
        # y capturando stdout/stderr para mejor depuración.
        process = subprocess.Popen(cmd, cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        print("--- Reflex STDOUT ---")
        print(stdout)
        print("--- Reflex STDERR ---")
        print(stderr)
        
        if process.returncode != 0:
            print(f"❌ Reflex execution failed with return code {process.returncode}")
            sys.exit(process.returncode)
        else:
            print("✅ Reflex process completed (though it might be a long-running server).")
            # Para un servidor, esto podría no ser alcanzado si Popen no bloquea hasta que termine.
            # Si es un servidor, se mantendrá corriendo. Si es un script que termina, saldrá.
            sys.exit(0) # Asumir éxito si returncode es 0
            
    except FileNotFoundError:
        print(f"❌ CRITICAL ERROR: The command {' '.join(cmd)} could not be found. Is Reflex installed correctly?")
        sys.exit(1)
    except subprocess.CalledProcessError as e: # Esto es más para subprocess.run(check=True)
        print(f"❌ Reflex execution failed (CalledProcessError): {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"❌ An unexpected error occurred while trying to run Reflex: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
