#!/bin/bash
# Script para iniciar la aplicación Reflex en Railway

# Obtener el puerto de la variable de entorno o usar 8000 como valor predeterminado
if [ -z "$PORT" ]; then
    PORT=8000
else
    # Asegurarse de que PORT sea un número
    if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
        echo "ERROR: PORT debe ser un número. Usando puerto 8000 por defecto."
        PORT=8000
    fi
fi

echo "Iniciando aplicación Reflex en el puerto: $PORT"

# Iniciar la aplicación Reflex con el puerto correcto
python -m reflex run --backend-host 0.0.0.0 --backend-port $PORT
