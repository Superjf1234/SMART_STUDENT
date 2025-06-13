#!/bin/bash
# Script para verificar estado y subir cambios a GitHub

cd /workspaces/SMART_STUDENT

# Mostrar mensaje inicial
echo ""
echo "=== VERIFICANDO ESTADO DE GIT ==="
git status

echo ""
echo "=== CONFIRMANDO ARCHIVOS MODIFICADOS ==="
ls -la mi_app_estudio/mi_app_estudio.py railway_direct_fix.py Procfile

echo ""
echo "=== SUBIENDO CAMBIOS A GITHUB ==="
git add mi_app_estudio/mi_app_estudio.py railway_direct_fix.py Procfile RAILWAY_ASSERTION_ERROR_FIX.md verify_railway_fix.sh prepare_for_deployment.sh
git commit -m "Fix: Solucionado error de AssertionError en rx.cond() para despliegue en Railway"
git push origin main

echo ""
echo "=== ESTADO FINAL ==="
git status
