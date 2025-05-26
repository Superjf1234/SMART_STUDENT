#!/usr/bin/env python
"""
Script para probar la generación de PDFs en SMART_STUDENT.
"""

import os
import sys
import datetime
import traceback

# Asegúrate de que el directorio del proyecto esté en sys.path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Importa la función de generación de PDF
from mi_app_estudio.utils import generate_pdf_report_from_answers

def test_generate_pdf():
    """Prueba la generación de un PDF sencillo."""
    print("=== PROBANDO GENERACIÓN DE PDF ===")
    
    # Crear un conjunto de preguntas de prueba
    preguntas_test = [
        {
            "pregunta": "¿Cuál es la capital de Francia?",
            "alternativas": [
                {"letra": "a", "texto": "Madrid"},
                {"letra": "b", "texto": "París"},
                {"letra": "c", "texto": "Londres"},
                {"letra": "d", "texto": "Roma"}
            ],
            "correcta": "b",
            "explicacion": "París es la capital de Francia."
        },
        {
            "pregunta": "¿En qué año comenzó la Segunda Guerra Mundial?",
            "alternativas": [
                {"letra": "a", "texto": "1939"},
                {"letra": "b", "texto": "1940"},
                {"letra": "c", "texto": "1941"},
                {"letra": "d", "texto": "1945"}
            ],
            "correcta": "a",
            "explicacion": "La Segunda Guerra Mundial comenzó en 1939 con la invasión de Polonia por Alemania."
        }
    ]
    
    try:
        # Generar el PDF
        pdf_url = generate_pdf_report_from_answers(
            titulo="Test de Generación de PDF",
            subtitulo="Prueba para verificar la funcionalidad",
            preguntas=preguntas_test,
            mostrar_respuestas=True,
            filename_prefix="test_pdf"
        )
        
        print(f"PDF generado exitosamente. URL: {pdf_url}")
        
        # Verificar que el archivo existe
        pdf_path = pdf_url.lstrip("/")
        if os.path.exists(pdf_path):
            print(f"Archivo confirmado en: {pdf_path}")
            print(f"Tamaño del archivo: {os.path.getsize(pdf_path)} bytes")
        else:
            print(f"ADVERTENCIA: No se encontró el archivo en la ruta: {pdf_path}")
            
            # Intentar buscar en otras rutas posibles
            alt_paths = [
                os.path.join("assets", "pdfs", os.path.basename(pdf_path)),
                os.path.basename(pdf_path)
            ]
            
            for path in alt_paths:
                if os.path.exists(path):
                    print(f"Archivo encontrado en ruta alternativa: {path}")
                    print(f"Tamaño del archivo: {os.path.getsize(path)} bytes")
                    break
        
        return True
    except Exception as e:
        print(f"ERROR generando PDF de prueba: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Asegurar que existe el directorio de salida
    os.makedirs(os.path.join("assets", "pdfs"), exist_ok=True)
    
    # Probar la generación de PDF
    success = test_generate_pdf()
    
    if success:
        print("\nPrueba completada con éxito!")
        sys.exit(0)
    else:
        print("\nPrueba fallida.")
        sys.exit(1)
