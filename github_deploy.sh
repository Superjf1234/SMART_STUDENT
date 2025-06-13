#!/bin/bash
# Script mejorado para subir cambios a GitHub con seguimiento detallado

# Configuración de colores para mejor legibilidad
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== INICIANDO PROCESO DE SUBIDA A GITHUB =====${NC}"
echo "Fecha y hora: $(date)"
echo ""

# Navegar al directorio del proyecto
cd /workspaces/SMART_STUDENT
echo -e "${GREEN}✓ Directorio de trabajo: $(pwd)${NC}"
echo ""

# Verificar si hay cambios pendientes
echo -e "${YELLOW}VERIFICANDO CAMBIOS PENDIENTES...${NC}"
git status
echo ""

# Agregar archivos específicos relacionados con la solución
echo -e "${YELLOW}AGREGANDO ARCHIVOS MODIFICADOS...${NC}"
file_list=(
    "mi_app_estudio/mi_app_estudio.py"
    "railway_direct_fix.py"
    "Procfile"
    "RAILWAY_ASSERTION_ERROR_FIX.md"
    "verify_railway_fix.sh"
    "prepare_for_deployment.sh"
    "INSTRUCCIONES_SUBIR_A_GITHUB.md"
)

for file in "${file_list[@]}"; do
    if [ -f "$file" ]; then
        git add "$file"
        echo -e "${GREEN}✓ Agregado: $file${NC}"
    else
        echo -e "${RED}✗ No encontrado: $file${NC}"
    fi
done
echo ""

# Crear commit con mensaje descriptivo
echo -e "${YELLOW}CREANDO COMMIT...${NC}"
git commit -m "Fix: Solucionado error de AssertionError en rx.cond() para despliegue en Railway"
echo -e "${GREEN}✓ Commit creado${NC}"
echo ""

# Subir cambios a GitHub
echo -e "${YELLOW}SUBIENDO CAMBIOS A GITHUB...${NC}"
git push origin main
push_status=$?

if [ $push_status -eq 0 ]; then
    echo -e "${GREEN}✓ CAMBIOS SUBIDOS EXITOSAMENTE A GITHUB${NC}"
else
    echo -e "${RED}✗ ERROR AL SUBIR CAMBIOS. CÓDIGO: $push_status${NC}"
    echo "Por favor, verifica tu conexión y credenciales de GitHub."
fi
echo ""

# Verificación final
echo -e "${YELLOW}ESTADO FINAL DEL REPOSITORIO:${NC}"
git status
echo ""

echo -e "${YELLOW}ÚLTIMO COMMIT:${NC}"
git log -1
echo ""

echo -e "${GREEN}===== PROCESO FINALIZADO =====${NC}"
echo "Para verificar los cambios, visita: https://github.com/Superjf1234/SMART_STUDENT"
