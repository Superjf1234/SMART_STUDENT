#!/bin/bash

echo "🚂 RAILWAY STARTUP - SMART STUDENT OPTIMIZADO"
echo "============================================================"

# Configurar variables para Railway
export REFLEX_ENV=prod
export NODE_ENV=production
export PYTHONPATH=/app
export PORT=${PORT:-8080}

echo "✅ REFLEX_ENV: $REFLEX_ENV"
echo "✅ NODE_ENV: $NODE_ENV"
echo "✅ Puerto: $PORT"
echo "✅ PYTHONPATH: $PYTHONPATH"

echo "============================================================"
echo "🚀 Iniciando aplicación optimizada..."

# Ejecutar Reflex con configuración correcta
python -m reflex run \
    --env prod \
    --backend-host 0.0.0.0 \
    --backend-port $PORT
