#!/bin/bash
# Production deployment script for SMART_STUDENT

echo "🚀 Preparando aplicación para producción..."

# 1. Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
rm -rf .web/
rm -rf __pycache__/
rm -rf mi_app_estudio/__pycache__/
rm -rf backend/__pycache__/
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# 2. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt
npm install

# 3. Verificar configuración
echo "⚙️ Verificando configuración..."
export REFLEX_ENV=production

# 4. Inicializar Reflex
echo "🔧 Inicializando Reflex..."
reflex init

# 5. Compilar aplicación
echo "🔨 Compilando aplicación..."
reflex export --frontend-only

echo "✅ Aplicación preparada para producción!"
echo ""
echo "📋 Opciones de deployment:"
echo "1. Railway: Conecta tu repositorio de GitHub a Railway.app"
echo "2. Render: Conecta tu repositorio a Render.com"
echo "3. Vercel: Usar 'vercel --prod'"
echo "4. Heroku: Usar 'git push heroku main'"
echo ""
echo "🔑 No olvides configurar las variables de entorno:"
echo "   - GEMINI_API_KEY"
echo "   - REFLEX_ENV=production"
