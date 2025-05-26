#!/usr/bin/env python3
"""
Script para probar la corrección del historial de evaluaciones.
Guarda una evaluación con respuestas correctas y total de preguntas, y luego verifica
que se recuperen correctamente desde la base de datos.
"""
import sys
import os
from datetime import datetime

# Asegurar que se pueden importar los módulos de backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db_logic import inicializar_db, guardar_resultado_evaluacion, obtener_historial

def test_historial_evaluaciones():
    """Prueba la funcionalidad de guardar y recuperar historial de evaluaciones."""
    print("Inicializando base de datos...")
    inicializar_db()
    
    username = "test_historial"
    curso = "8vo Básico"
    libro = "Ciencias Naturales"
    tema = "Sistema respiratorio"
    
    # Guardar una evaluación con nota 6.7 y 8 de 10 respuestas correctas
    print(f"Guardando evaluación para {username}...")
    nota = 6.7
    resp_correctas = 8
    total_preguntas = 10
    
    # Calcular el porcentaje
    porcentaje = (nota - 1.0) * 100 / 6.0
    print(f"Nota {nota} equivale a aproximadamente {porcentaje:.1f}%")
    
    # Guardar en BD con metadata correcta
    resultado = guardar_resultado_evaluacion(username, curso, libro, tema, nota, resp_correctas, total_preguntas)
    
    if resultado:
        print("Evaluación guardada correctamente.")
    else:
        print("ERROR: No se pudo guardar la evaluación.")
        return
    
    # Recuperar el historial
    print(f"Recuperando historial para {username}...")
    historial = obtener_historial(username)
    
    if not historial:
        print("ERROR: No se pudo recuperar el historial.")
        return
    
    print(f"Se encontraron {len(historial)} registros:")
    for i, evaluacion in enumerate(historial):
        print(f"Evaluación {i+1}:")
        print(f"  - ID: {evaluacion.get('id')}")
        print(f"  - Curso: {evaluacion.get('curso')}")
        print(f"  - Libro: {evaluacion.get('libro')}")
        print(f"  - Tema: {evaluacion.get('tema')}")
        print(f"  - Fecha: {evaluacion.get('fecha')}")
        print(f"  - Nota: {evaluacion.get('nota')}")
        print(f"  - Metadata: {evaluacion.get('metadata')}")

    # Verificar que la metadata se haya guardado correctamente
    if len(historial) > 0:
        ultima_evaluacion = historial[0]
        if "metadata" in ultima_evaluacion and ultima_evaluacion["metadata"]:
            metadata = ultima_evaluacion["metadata"]
            if "Correctas:" in metadata:
                print(f"✅ Metadata guardada correctamente: '{metadata}'")
            else:
                print(f"❌ Metadata con formato incorrecto: '{metadata}'")
        else:
            print("❌ No se encontró metadata en la evaluación.")

if __name__ == "__main__":
    test_historial_evaluaciones()
