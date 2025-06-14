#!/bin/bash
# Script para limpiar archivos obsoletos y optimizar el proyecto

echo "🧹 LIMPIANDO PROYECTO SMART_STUDENT..."

# Crear backup antes de limpiar
mkdir -p backup_before_clean
cp -r *.py *.md backup_before_clean/ 2>/dev/null

# Eliminar archivos de scripts de debug/fix acumulados
echo "Eliminando scripts de debug/fix obsoletos..."
rm -f aggressive_cleanup.py
rm -f analyze_*.py
rm -f check_*.py
rm -f count_*.py
rm -f debug_*.py
rm -f diagnose_*.py
rm -f find_*.py
rm -f fix_*.py
rm -f railway_*.py
rm -f test_*.py
rm -f verify_*.py
rm -f emergency_*.py
rm -f memory_*.py
rm -f simple_*.py
rm -f temp_*.py
rm -f trigger_*.py
rm -f ultra_*.py
rm -f upload_*.py

# Mantener solo los archivos esenciales de scripts
echo "Manteniendo archivos esenciales..."
# ultra_robust_start.py se mantiene (es el actual)

# Eliminar archivos de configuración duplicados
rm -f rxconfig_*.py
rm -f requirements_*.txt
rm -f Procfile.*
rm -f Dockerfile.*

# Mantener solo configuraciones principales:
# - rxconfig.py
# - requirements.txt  
# - Procfile
# - Dockerfile

# Eliminar archivos de documentación de fixes antiguos
echo "Eliminando documentación de fixes obsoletos..."
rm -f ACCION_*.md
rm -f BILINGUAL_*.md
rm -f COMPLETE_*.md
rm -f CURRENT_*.md
rm -f DEPLOYMENT_*.md
rm -f DOCKER_*.md
rm -f FINAL_*.md
rm -f GEMINI_*.md
rm -f GITHUB_*.md
rm -f ITERATION_*.md
rm -f MEMORY_*.md
rm -f PORT_*.md
rm -f PRODUCTION_*.md
rm -f RAILWAY_*.md
rm -f RESUMEN_*.md
rm -f RICH_*.md
rm -f SYNTAX_*.md
rm -f URGENT_*.md
rm -f VALIDATION_*.md
rm -f VarAttributeError_*.md

# Mantener documentación esencial:
# - README.md
# - RESTRUCTURE_PLAN.md (nuevo)

# Limpiar cache
echo "Limpiando archivos de cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null

# Limpiar logs
rm -f *.log
rm -f nohup.out

echo "✅ LIMPIEZA COMPLETADA"
echo "📁 Backup creado en: backup_before_clean/"
echo "🎯 Proyecto optimizado y listo para deploy"
