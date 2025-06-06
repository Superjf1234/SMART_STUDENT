#!/bin/bash
# Railway startup script for SMART_STUDENT
set -e

echo "🚀 Starting SMART_STUDENT on Railway..."
echo "🔧 Environment: ${REFLEX_ENV:-production}"
echo "🌐 Backend Port: ${PORT:-8000}"
echo "📁 Python Path: ${PYTHONPATH:-/app}"

# Initialize Reflex if needed
echo "📦 Initializing Reflex..."
python -m reflex init --no-input --overwrite || true

# Export the app
echo "🏗️ Building frontend..."
python -m reflex export --no-zip || true

# Start the application
echo "🎯 Starting application..."
exec python -m reflex run \
  --backend-host 0.0.0.0 \
  --backend-port ${PORT:-8000} \
  --frontend-host 0.0.0.0 \
  --frontend-port 3000 \
  --env production
