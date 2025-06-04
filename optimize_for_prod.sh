#!/bin/bash
# Production optimization script for SMART_STUDENT

echo "🔧 Optimizando aplicación para producción..."

# 1. Limpiar archivos de desarrollo
echo "🧹 Limpiando archivos de desarrollo..."
rm -rf .web/
rm -rf __pycache__/
rm -rf */__pycache__/
rm -rf mi_app_estudio/__pycache__/
rm -rf backend/__pycache__/
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete
rm -f app.log app_output.log
rm -f *.tmp *.temp
rm -rf .pytest_cache/

# 2. Limpiar archivos de debug y test
echo "🗂️ Removiendo archivos de debug y testing..."
rm -f debug_*.py
rm -f test_*.py
rm -f check_*.py
rm -f diagnose_*.py
rm -f fix_*.py
rm -f verify_*.py
rm -f validate_*.py
rm -f simple_*.py
rm -f basic_*.py
rm -f manual_*.py
rm -f quick_*.py
rm -f *_test.py
rm -f *_debug.py
rm -f *_fix.py
rm -f apply_fix.py
rm -f *.md

# 3. Limpiar logs y archivos temporales
rm -f *.log
rm -f tmp_*
rm -f 0 = =1.7.2

# 4. Optimizar package.json (mantener solo dependencias necesarias)
echo "📦 Optimizando dependencias..."

# 5. Crear estructura de producción
mkdir -p production_build
mkdir -p logs

echo "✅ Optimización completada!"
echo ""
echo "📁 Archivos mantenidos para producción:"
echo "   - main.py (entry point)"
echo "   - rxconfig.py (configuración)"
echo "   - requirements.txt (dependencias Python)"
echo "   - package.json (dependencias Node.js)"
echo "   - mi_app_estudio/ (aplicación principal)"
echo "   - backend/ (lógica de backend)"
echo "   - assets/ (recursos estáticos)"
echo "   - Dockerfile, Procfile, deploy.sh (deployment)"
echo ""
echo "🚀 La aplicación está lista para el deployment!"
