#!/bin/bash
# Script de verificación post-upload

echo "===== VERIFICACIÓN POST-UPLOAD A GITHUB ====="
echo "Verificando que los cambios se hayan subido correctamente..."
echo ""

# Verificar el estado actual
echo "Estado actual del repositorio:"
git status
echo ""

# Mostrar los últimos commits
echo "Últimos 3 commits:"
git log --oneline -3
echo ""

# Verificar que los archivos importantes existen
echo "Verificando archivos importantes:"
files_to_check=(
    "mi_app_estudio/mi_app_estudio.py"
    "railway_direct_fix.py"
    "Procfile"
    "RAILWAY_ASSERTION_ERROR_FIX.md"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file - EXISTE"
    else
        echo "✗ $file - NO ENCONTRADO"
    fi
done
echo ""

# Verificar la configuración remota
echo "Configuración de repositorios remotos:"
git remote -v
echo ""

# Mostrar el hash del último commit
echo "Hash del último commit:"
git rev-parse HEAD
echo ""

echo "===== VERIFICACIÓN COMPLETADA ====="
echo "Para confirmar que los cambios están en GitHub, visita:"
echo "https://github.com/Superjf1234/SMART_STUDENT"
