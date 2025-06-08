#!/usr/bin/env python3
# Script Python para ejecutar Reflex con el puerto adecuado
import os
import sys
import subprocess
from pathlib import Path

# Cargar variables de entorno desde .env si existe
env_path = Path('.env')
if env_path.exists():
    print("Cargando variables de entorno desde .env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Verificar que GEMINI_API_KEY esté definida
if 'GEMINI_API_KEY' not in os.environ:
    print("ADVERTENCIA: Variable GEMINI_API_KEY no está definida")
    # Usar una clave ficticia para permitir que la aplicación se inicie
    os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"

# Obtener el puerto de la variable de entorno o usar 8000 como predeterminado
port = os.environ.get('PORT', '8000')

try:
    # Verificar que PORT sea un número válido
    port_num = int(port)
    print(f"Iniciando Reflex en el puerto: {port_num}")
except ValueError:
    print(f"ERROR: PORT '{port}' no es un número válido. Usando 8000 por defecto.")
    port = "8000"

# Construir el comando para ejecutar Reflex
cmd = [
    "python", "-m", "reflex", "run", 
    "--backend-host", "0.0.0.0", 
    "--backend-port", port
]

# Ejecutar el comando
try:
    subprocess.run(cmd)
except Exception as e:
    print(f"ERROR al ejecutar Reflex: {e}")
    sys.exit(1)
