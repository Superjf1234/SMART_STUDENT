#!/bin/bash
# Script final para subir la corrección del error @app.add_page a GitHub

echo "===== SUBIENDO CORRECCIÓN FINAL A GITHUB ====="
echo "Corrigiendo error de @app.add_page en línea 2675"

cd /workspaces/SMART_STUDENT

# Agregar archivos modificados
echo "Agregando archivos modificados..."
git add mi_app_estudio/mi_app_estudio.py
git add test_basic.py
git add diagnose_app.py

# Crear commit con descripción específica
echo "Creando commit..."
git commit -m "Fix: Corregido error @app.add_page en línea 2675 - Sintaxis moderna de Reflex"

# Subir a GitHub
echo "Subiendo a GitHub..."
git push origin main

echo "✅ CORRECCIÓN SUBIDA A GITHUB"
echo "El error de @app.add_page ha sido solucionado"
echo "La aplicación ahora usa app.add_page() en lugar del decorador"
