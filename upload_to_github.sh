#!/bin/bash
# Script para subir los cambios a GitHub

echo "===== SUBIENDO CAMBIOS A GITHUB ====="
echo "Este script agregará y subirá los cambios realizados para solucionar el error AssertionError"

# Navegar al directorio del proyecto
cd /workspaces/SMART_STUDENT

# Agregar los archivos modificados
echo "Agregando archivos modificados..."
git add mi_app_estudio/mi_app_estudio.py railway_direct_fix.py Procfile RAILWAY_ASSERTION_ERROR_FIX.md verify_railway_fix.sh prepare_for_deployment.sh

# Crear un commit
echo "Creando commit..."
git commit -m "Fix: Solucionado error de AssertionError en rx.cond() para despliegue en Railway"

# Subir a GitHub
echo "Subiendo cambios a GitHub..."
git push origin main

echo "===== PROCESO COMPLETADO ====="
echo "Los cambios han sido subidos a GitHub. Puedes verificar en tu repositorio."
