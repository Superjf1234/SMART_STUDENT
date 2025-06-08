#!/usr/bin/env python3
# Script Python para ejecutar Reflex con el puerto adecuado
import os
import sys
import subprocess

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
