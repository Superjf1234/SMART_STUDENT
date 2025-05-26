#!/usr/bin/env python
"""
Lanzador para la aplicación de prueba de descarga de cuestionario
"""
import os
import sys
from pathlib import Path

# Agregar la raíz del proyecto al path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

print("\n=== EJECUTANDO APLICACIÓN DE PRUEBA DE DESCARGA DE CUESTIONARIO ===\n")

# Crear un entorno de ejecución temporal para la aplicación
os.environ["REFLEX_DEBUG"] = "1"

try:
    # Importar y ejecutar la aplicación de prueba
    from test_download_app import app
    
    # Imprimir instrucciones
    print("\nInstrucciones:")
    print("1. La aplicación de prueba se iniciará en http://localhost:3000")
    print("2. Haz clic en el botón 'Descargar Cuestionario'")
    print("3. Verifica que el archivo HTML descargado contenga las preguntas correctamente")
    print("\nSi la descarga funciona correctamente, las correcciones son exitosas.\n")
    
    # Ejecutar la aplicación
    app.compile()
    print("\nCompilación completada. Iniciando servidor...")
    
    # Intentar ejecutar
    app.run()
    
except Exception as e:
    print(f"Error al ejecutar la aplicación de prueba: {e}")
    print("\nPara ejecutar manualmente la aplicación de prueba:")
    print("1. Ejecuta 'python -m test_download_app run'")
    print("2. Abre http://localhost:3000 en tu navegador")
