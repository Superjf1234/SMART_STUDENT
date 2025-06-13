#!/bin/bash
# Script para resolver problemas de inicialización en Railway

echo "===== SOLUCIONANDO PROBLEMAS DE INICIALIZACIÓN EN RAILWAY ====="

# Verificamos la estructura de directorios actual
echo "Verificando estructura de directorios..."
ls -la
echo ""

# Creamos un archivo __init__.py en mi_app_estudio si no existe
if [ ! -f "mi_app_estudio/__init__.py" ]; then
    echo "Creando archivo __init__.py en mi_app_estudio"
    echo "# Módulo mi_app_estudio" > mi_app_estudio/__init__.py
fi

# Creamos un archivo explícito para ejecutar la aplicación
cat > run_app.py << EOL
"""
Punto de entrada explícito para la aplicación SMART_STUDENT.
Este archivo simplifica la ejecución para entornos de nube como Railway.
"""
import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para facilitar imports
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Importar la aplicación desde el módulo mi_app_estudio
try:
    from mi_app_estudio.mi_app_estudio import app
    print("INFO: Aplicación importada correctamente.")
except ImportError as e:
    print(f"ERROR: No se pudo importar la aplicación: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Configuración para Railway
app.compile()

# Ejecutar el backend
if __name__ == "__main__":
    # Obtener puerto del entorno o usar 8000 por defecto
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"INFO: Iniciando servidor en {host}:{port}")
    
    # Iniciar el servidor usando la API de Reflex
    from reflex.utils import exec
    exec.run_backend(app, port=port, host=host)
EOL

# Modificar el Procfile para usar el nuevo punto de entrada
cat > Procfile << EOL
web: python run_app.py
EOL

echo "Nuevo archivo run_app.py y Procfile creados."

# Crear un archivo de diagnóstico para verificar la configuración de Python en Railway
cat > check_env.py << EOL
"""
Script de diagnóstico para verificar el entorno de Python en Railway.
"""
import sys
import os
import reflex

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")
print(f"Reflex version: {reflex.__version__}")

# Verificar estructura de mi_app_estudio
if os.path.exists("mi_app_estudio"):
    print(f"mi_app_estudio contents: {os.listdir('mi_app_estudio')}")

# Intentar importar la aplicación explícitamente
try:
    print("Intentando importar app desde mi_app_estudio.mi_app_estudio...")
    from mi_app_estudio.mi_app_estudio import app
    print("¡Importación exitosa!")
except Exception as e:
    print(f"Error al importar: {e}")
    import traceback
    traceback.print_exc()
EOL

echo "===== ARCHIVOS DE SOLUCIÓN CREADOS ====="
echo "1. run_app.py - Punto de entrada explícito para la aplicación"
echo "2. Procfile actualizado para usar run_app.py"
echo "3. check_env.py - Script de diagnóstico del entorno"
echo ""
echo "Para aplicar estos cambios, ejecuta:"
echo "  git add run_app.py check_env.py mi_app_estudio/__init__.py Procfile"
echo "  git commit -m \"Fix: Solución para problemas de inicialización en Railway\""
echo "  git push origin main"
echo ""
echo "Para verificar el entorno en Railway, puedes modificar el Procfile temporalmente a:"
echo "  web: python check_env.py"
echo "===== FIN ====="
