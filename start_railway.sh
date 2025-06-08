#!/bin/bash
# Script para iniciar la aplicación Reflex en Railway

# Obtener el puerto de la variable de entorno o usar 8000 como valor predeterminado
PORT=${PORT:-8000}

# Iniciar la aplicación Reflex con el puerto correcto
python -m reflex run --backend-host 0.0.0.0 --backend-port $PORT
