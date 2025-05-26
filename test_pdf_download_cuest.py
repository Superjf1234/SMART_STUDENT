#!/usr/bin/env python3
# test_pdf_download_cuest.py - Test para la funcionalidad de descarga de PDF en cuestionarios

import os
import sys
import tempfile
from mi_app_estudio.utils import generate_pdf_report_from_answers

def test_pdf_generation():
    """Prueba la generación de PDF para cuestionarios."""
    print("\n--- Probando generación de PDF para cuestionarios ---")
    
    # Preguntas de ejemplo
    preguntas_ejemplo = [
        {
            "pregunta": "¿Cuál es la capital de Chile?",
            "explicacion": "La capital de Chile es Santiago."
        },
        {
            "pregunta": "¿Cuántos planetas tiene el sistema solar?",
            "alternativas": [
                {"letra": "a", "texto": "7 planetas"},
                {"letra": "b", "texto": "8 planetas", "correcta": True},
                {"letra": "c", "texto": "9 planetas"},
                {"letra": "d", "texto": "10 planetas"}
            ],
            "explicacion": "El sistema solar tiene 8 planetas reconocidos oficialmente."
        }
    ]
    
    # Generar PDF
    output_dir = tempfile.mkdtemp()  # Directorio temporal
    url = generate_pdf_report_from_answers(
        titulo="Prueba de Cuestionario - Sistema Solar",
        subtitulo="Curso: Astronomía - Libro: Sistema Solar",
        preguntas=preguntas_ejemplo,
        mostrar_respuestas=True,
        output_dir=output_dir,
        filename_prefix="test_cuestionario"
    )
    
    # Verificar resultados
    print(f"URL generada: {url}")
    filepath = os.path.join(output_dir, os.path.basename(url.replace("/assets/pdfs/", "")))
    print(f"Archivo creado en: {filepath}")
    
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ PDF generado correctamente: {size} bytes")
        # Mostrar el archivo en explorador (solo en sistemas compatibles)
        if sys.platform.startswith("darwin"):  # macOS
            os.system(f"open {filepath}")
        elif sys.platform.startswith("linux"):
            os.system(f"xdg-open {filepath} 2>/dev/null || echo 'No se pudo abrir automáticamente'")
        elif sys.platform.startswith("win"):  # Windows
            os.system(f"start {filepath}")
        else:
            print(f"Archivo creado en: {filepath}")
    else:
        print("❌ Error: No se generó el archivo PDF")

if __name__ == "__main__":
    test_pdf_generation()
