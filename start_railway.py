#!/usr/bin/env python3
# Script Python para ejecutar Reflex con el puerto adecuado para Railway
import os
import sys
import subprocess
from pathlib import Path

def load_env_file():
    """Cargar variables de entorno desde .env si existe"""
    env_path = Path('.env')
    if env_path.exists():
        print("Cargando variables de entorno desde .env")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def setup_environment():
    """Configurar variables de entorno necesarias"""
    # Verificar que GEMINI_API_KEY esté definida
    if 'GEMINI_API_KEY' not in os.environ:
        print("ADVERTENCIA: Variable GEMINI_API_KEY no está definida")
        # Usar una clave ficticia para permitir que la aplicación se inicie
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    
    # Railway siempre usa puerto 8080
    port = os.environ.get('PORT', '8080')
    
    try:
        port_num = int(port)
        print(f"Iniciando Reflex en el puerto: {port_num}")
        return str(port_num)
    except ValueError:
        print(f"ERROR: PORT '{port}' no es un número válido. Usando 8080 por defecto.")
        return "8080"

def initialize_reflex():
    """Inicializar Reflex si es necesario"""
    try:
        print("Verificando si Reflex necesita inicialización...")
        
        # Verificar si ya existe la configuración
        if not os.path.exists(".web"):
            print("Inicializando Reflex por primera vez...")
            result = subprocess.run(
                ["python", "-m", "reflex", "init", "--template", "blank"], 
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                print(f"Advertencia durante inicialización: {result.stderr}")
        else:
            print("Reflex ya está inicializado")
            
        # Instalar dependencias frontend con configuración optimizada para Railway
        print("Instalando dependencias frontend...")
        env = os.environ.copy()
        env.update({
            "NODE_OPTIONS": "--max-old-space-size=512",
            "BUN_CONFIG_NO_CLEAR_TERMINAL": "true"
        })
        
        # Verificar si las dependencias frontend están instaladas
        if not os.path.exists(".web/node_modules"):
            print("Instalando dependencias frontend con npm...")
            subprocess.run(["npm", "install"], cwd=".web", timeout=120)
        else:
            print("Dependencias frontend ya están instaladas")
            
    except subprocess.TimeoutExpired:
        print("Inicialización tomó demasiado tiempo, continuando...")
    except Exception as e:
        print(f"Advertencia durante inicialización: {e}")

def main():
    """Función principal"""
    print("=== Iniciando SMART_STUDENT en Railway ===")
    
    # Cargar configuración
    load_env_file()
    port = setup_environment()
    
    # Inicializar Reflex
    initialize_reflex()
    
    # Configurar comando de ejecución para Railway
    cmd = [
        "python", "-m", "reflex", "run", 
        "--env", "prod",
        "--backend-host", "0.0.0.0", 
        "--backend-port", port,
        "--frontend-port", port
    ]
    
    print(f"Ejecutando comando: {' '.join(cmd)}")
    
    # Ejecutar el comando
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR al ejecutar Reflex: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Aplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
