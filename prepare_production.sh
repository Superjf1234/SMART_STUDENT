#!/bin/bash
# Complete production preparation script for SMART_STUDENT

set -e  # Exit on any error

echo "🎯 SMART_STUDENT - Preparación Completa para Producción"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Verify environment
print_status "Verificando entorno..."

if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm no está instalado"
    exit 1
fi

print_success "Entorno verificado ✓"

# 2. Check required files
print_status "Verificando archivos requeridos..."

required_files=(
    "main.py"
    "rxconfig.py" 
    "requirements.txt"
    "package.json"
    "mi_app_estudio/mi_app_estudio.py"
    "backend/eval_logic.py"
    "backend/db_logic.py"
    "backend/config_logic.py"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        print_error "Archivo requerido no encontrado: $file"
        exit 1
    fi
done

print_success "Archivos requeridos verificados ✓"

# 3. Check API key
print_status "Verificando configuración de API..."

if [[ -f ".env" ]]; then
    if grep -q "GEMINI_API_KEY" .env; then
        print_success "API key configurada en .env ✓"
    else
        print_warning "API key no encontrada en .env"
    fi
else
    print_warning "Archivo .env no encontrado. Usa .env.example como referencia"
fi

# 4. Install dependencies
print_status "Instalando dependencias..."

echo "📦 Instalando dependencias Python..."
pip install -r requirements.txt

echo "📦 Instalando dependencias Node.js..."
npm install

print_success "Dependencias instaladas ✓"

# 5. Test basic imports
print_status "Probando imports básicos..."

python3 -c "
import sys
sys.path.append('.')
try:
    from mi_app_estudio import mi_app_estudio
    from backend import eval_logic, db_logic, config_logic
    print('✓ Todos los imports funcionan correctamente')
except ImportError as e:
    print(f'✗ Error en imports: {e}')
    sys.exit(1)
"

print_success "Imports verificados ✓"

# 6. Initialize database
print_status "Inicializando base de datos..."
python3 -c "
import sys
sys.path.append('.')
from backend import db_logic
db_logic.inicializar_db()
print('✓ Base de datos inicializada')
"

print_success "Base de datos lista ✓"

# 7. Build application
print_status "Compilando aplicación..."

export REFLEX_ENV=production
reflex init

print_success "Aplicación compilada ✓"

# 8. Create production package
print_status "Creando paquete de producción..."

# Create deployment directory
mkdir -p production_package

# Copy essential files
cp -r mi_app_estudio production_package/
cp -r backend production_package/
cp -r assets production_package/ 2>/dev/null || print_warning "assets/ no encontrado"
cp main.py production_package/
cp rxconfig.py production_package/
cp requirements.txt production_package/
cp package.json production_package/
cp package-lock.json production_package/ 2>/dev/null || true
cp Dockerfile production_package/
cp Procfile production_package/
cp .env.example production_package/
cp DEPLOYMENT_README.md production_package/

print_success "Paquete de producción creado ✓"

# 9. Final verification
print_status "Verificación final..."

echo ""
echo "🎉 ¡PREPARACIÓN COMPLETADA!"
echo "=========================="
echo ""
echo "📁 Paquete de producción disponible en: ./production_package/"
echo ""
echo "🚀 Opciones de deployment:"
echo "   1. Railway: https://railway.app (Recomendado)"
echo "   2. Render: https://render.com"
echo "   3. Heroku: https://heroku.com"
echo "   4. Vercel: https://vercel.com"
echo ""
echo "🔑 Variables de entorno requeridas:"
echo "   - REFLEX_ENV=production"
echo "   - GEMINI_API_KEY=tu_api_key_aqui"
echo ""
echo "📖 Ver DEPLOYMENT_README.md para instrucciones detalladas"
echo ""

print_success "¡Aplicación lista para producción! 🚀"
