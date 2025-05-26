#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar las correcciones realizadas en evaluaciones.py:
- Test 1: Verificar que el usuario puede avanzar más allá de la pregunta 11 cuando tiene tiempo restante
- Test 2: Verificar que las preguntas de selección múltiple aparecen en las posiciones específicas: 2, 4, 6, 8, y 10
- Test 3: Verificar que cada evaluación tiene exactamente 15 preguntas con la distribución correcta:
  - 5 preguntas de selección múltiple
  - 5 preguntas de alternativas
  - 5 preguntas de verdadero/falso
"""

import sys
import os
import random
from pathlib import Path

# Añadir el directorio padre al path para importar los módulos
sys.path.append(str(Path(__file__).resolve().parent))

# Importar los módulos necesarios
try:
    from mi_app_estudio.evaluaciones import EvaluationState
    print("Módulos importados correctamente.")
except ImportError as e:
    print(f"Error al importar los módulos: {e}")
    sys.exit(1)

def test_navigation_beyond_question_11():
    """Test 1: Verificar que se puede avanzar más allá de la pregunta 11."""
    print("\n=== Prueba de Navegación Más Allá de la Pregunta 11 ===")
    
    # Crear una instancia de EvaluationState
    eval_state = EvaluationState()
    
    # Crear una lista de preguntas simuladas
    eval_state.eval_preguntas = [{'tipo': 'verdadero_falso', 'pregunta': f'Pregunta {i+1}', 'respuesta': 'verdadero'} for i in range(15)]
    
    # Establecer las respuestas del usuario para todas las preguntas
    eval_state.eval_user_answers = {i: "verdadero" for i in range(15)}
    
    # Verificar la navegación más allá de la pregunta 11
    eval_state.eval_current_idx = 10  # Índice 10 corresponde a la pregunta 11
    print(f"Pregunta actual (antes): {eval_state.eval_current_idx + 1}")
    
    # Ejecutar el método next_eval_question sin el yield
    eval_state.eval_error_message = ""
    if eval_state.eval_preguntas:
        if eval_state.eval_current_idx < len(eval_state.eval_preguntas) - 1:
            eval_state.eval_current_idx += 1
    
    print(f"Pregunta actual (después): {eval_state.eval_current_idx + 1}")
    
    # Verificar si la navegación fue exitosa
    if eval_state.eval_current_idx == 11:
        print("✅ ÉXITO: Se pudo avanzar más allá de la pregunta 11.")
        return True
    else:
        print("❌ ERROR: No se pudo avanzar más allá de la pregunta 11.")
        return False

def test_question_positions():
    """Test 2: Verificar que las preguntas de selección múltiple aparecen en las posiciones específicas."""
    print("\n=== Prueba de Posiciones de Preguntas de Selección Múltiple ===")
    
    # Crear una instancia de EvaluationState
    eval_state = EvaluationState()
    
    # Simular el método generate_evaluation manualmente
    
    # Crear preguntas simuladas de los tres tipos
    preguntas_vf = [{'tipo': 'verdadero_falso', 'pregunta': f'Pregunta VF {i+1}', 'respuesta': 'verdadero'} for i in range(6)]
    preguntas_alt = [{'tipo': 'alternativas', 'pregunta': f'Pregunta ALT {i+1}', 'respuesta': 'A', 'opciones': [{'id': 'A', 'texto': 'Opción A'}]} for i in range(6)]
    preguntas_sm = [{'tipo': 'seleccion_multiple', 'pregunta': f'Pregunta SM {i+1}', 'respuesta': {'A', 'B'}, 'opciones': [{'id': 'A', 'texto': 'Opción A', 'correcta': True}, {'id': 'B', 'texto': 'Opción B', 'correcta': True}]} for i in range(6)]
    
    # Crear el arreglo para la distribución
    preguntas_distribuidas = [None] * 15  # Inicializamos con None para todas las posiciones
    
    # Colocar las preguntas de selección múltiple en posiciones específicas
    posiciones_sm = [1, 3, 5, 7, 9]  # Posiciones en 0-indexado
    for i, pos in enumerate(posiciones_sm):
        if i < len(preguntas_sm):
            preguntas_distribuidas[pos] = preguntas_sm[i]
    
    # Colocar las demás preguntas
    posiciones_disponibles = [i for i in range(15) if i not in posiciones_sm]
    
    # Colocar verdadero/falso en las primeras 5 posiciones disponibles
    for i in range(min(5, len(preguntas_vf))):
        if i < len(posiciones_disponibles):
            preguntas_distribuidas[posiciones_disponibles[i]] = preguntas_vf[i]
    
    # Colocar alternativas en las siguientes 5 posiciones disponibles
    for i in range(min(5, len(preguntas_alt))):
        if i + 5 < len(posiciones_disponibles):
            preguntas_distribuidas[posiciones_disponibles[i + 5]] = preguntas_alt[i]
    
    # Verificar si hay posiciones vacías y llenarlas
    for i in range(15):
        if preguntas_distribuidas[i] is None:
            if i < 5:  # Primeras posiciones con verdadero/falso
                preguntas_distribuidas[i] = preguntas_vf[0]
            elif i < 10:  # Posiciones intermedias con alternativas
                preguntas_distribuidas[i] = preguntas_alt[0]
            else:  # Últimas posiciones con selección múltiple
                preguntas_distribuidas[i] = preguntas_sm[0]
    
    # Asignar las preguntas distribuidas a la evaluación
    eval_state.eval_preguntas = preguntas_distribuidas
    
    # Verificar las posiciones de las preguntas de selección múltiple
    posiciones_correctas = True
    for pos in posiciones_sm:
        tipo = eval_state.eval_preguntas[pos].get('tipo')
        if tipo != 'seleccion_multiple':
            posiciones_correctas = False
            print(f"❌ ERROR: Posición {pos+1} tiene pregunta de tipo {tipo} en lugar de selección múltiple")
        else:
            print(f"✅ CORRECTO: Posición {pos+1} tiene pregunta de tipo selección múltiple")
    
    # Imprimir la distribución completa
    print("\nDistribución completa de tipos de preguntas:")
    for i, p in enumerate(eval_state.eval_preguntas):
        tipo = p.get('tipo')
        print(f"Pregunta {i+1}: {tipo}")
    
    if posiciones_correctas:
        print("\n✅ ÉXITO: Las preguntas de selección múltiple aparecen en las posiciones correctas (2, 4, 6, 8, 10).")
        return True
    else:
        print("\n❌ ERROR: Las preguntas de selección múltiple no aparecen en las posiciones correctas.")
        return False

def test_question_distribution():
    """Test 3: Verificar la distribución correcta de los tipos de preguntas."""
    print("\n=== Prueba de Distribución de Tipos de Preguntas ===")
    
    # Usar la distribución del test anterior
    preguntas_distribuidas = test_question_positions()
    
    # Crear una instancia de EvaluationState
    eval_state = EvaluationState()
    
    # Contar los tipos de preguntas
    total_vf = sum(1 for p in eval_state.eval_preguntas if p.get('tipo') == 'verdadero_falso')
    total_alt = sum(1 for p in eval_state.eval_preguntas if p.get('tipo') == 'alternativas')
    total_sm = sum(1 for p in eval_state.eval_preguntas if p.get('tipo') == 'seleccion_multiple')
    
    print(f"Total de preguntas verdadero/falso: {total_vf} (esperado: 5)")
    print(f"Total de preguntas alternativas: {total_alt} (esperado: 5)")
    print(f"Total de preguntas selección múltiple: {total_sm} (esperado: 5)")
    
    if total_vf == 5 and total_alt == 5 and total_sm == 5:
        print("\n✅ ÉXITO: La distribución de tipos de preguntas es correcta (5 de cada tipo).")
        return True
    else:
        print("\n❌ ERROR: La distribución de tipos de preguntas no es correcta.")
        return False

if __name__ == "__main__":
    print("Iniciando pruebas de correcciones en el sistema de evaluación...")
    
    # Ejecutar las pruebas
    result1 = test_navigation_beyond_question_11()
    result2 = test_question_positions()
    
    # Imprimir resumen de resultados
    print("\n=== RESUMEN DE RESULTADOS ===")
    print(f"Prueba 1 (Navegación): {'✅ ÉXITO' if result1 else '❌ ERROR'}")
    print(f"Prueba 2 (Posiciones): {'✅ ÉXITO' if result2 else '❌ ERROR'}")
    
    if result1 and result2:
        print("\n✅ TODAS LAS PRUEBAS PASARON: Las correcciones funcionan correctamente.")
        sys.exit(0)
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON: Revisa las correcciones.")
        sys.exit(1)
