#!/usr/bin/env python3
# coding: utf-8

import sys
from mi_app_estudio.evaluaciones import EvaluationState

def test_verdadero_falso_questions():
    """
    Test para verificar el comportamiento de preguntas verdadero/falso
    en la función que determina si las respuestas son correctas.
    """
    # Crear instancia de EvaluationState para pruebas
    eval_state = EvaluationState()
    
    # Configurar una pregunta de prueba donde la respuesta correcta es "falso"
    eval_state.eval_preguntas = [
        {
            "id": 1,
            "pregunta": "El dióxido de carbono pasa de la sangre al alveolo porque hay mayor concentración de dióxido de carbono en el alveolo que en los capilares.",
            "tipo": "verdadero_falso",
            "correcta": "falso",  # La respuesta correcta es "falso"
            "explicacion": "El dióxido de carbono pasa de la sangre al alveolo porque hay mayor concentración de dióxido de carbono en los capilares que en el alveolo."
        }
    ]
    
    # Configurar como si estuviéramos en modo revisión
    eval_state.is_reviewing_eval = True
    eval_state.eval_current_idx = 0
    
    # Probar varias formas de respuesta falsa
    test_cases = [
        ("falso", True, "Respuesta falso (minúsculas)"),
        ("Falso", True, "Respuesta Falso (primera letra mayúscula)"),
        ("FALSO", True, "Respuesta FALSO (todas mayúsculas)"),
        ("false", True, "Respuesta false (en inglés)"),
        ("f", True, "Respuesta f (abreviada)"),
        ("verdadero", False, "Respuesta incorrecta: verdadero"),
        ("Verdadero", False, "Respuesta incorrecta: Verdadero"),
        ("true", False, "Respuesta incorrecta: true"),
    ]
    
    print("=== TEST DE PREGUNTAS VERDADERO/FALSO ===")
    print(f"Pregunta: {eval_state.eval_preguntas[0]['pregunta']}")
    print(f"Respuesta correcta: {eval_state.eval_preguntas[0]['correcta']}")
    print("\nProbando diferentes respuestas:")
    print("-" * 60)
    
    all_tests_passed = True
    
    for user_answer, expected_result, description in test_cases:
        # Establecer la respuesta del usuario
        eval_state.eval_user_answers = {0: user_answer}
        
        # Obtener el resultado de la evaluación
        result = eval_state.is_current_question_correct_in_review
        
        # Verificar si el resultado coincide con lo esperado
        passed = result == expected_result
        status = "✅ CORRECTO" if passed else "❌ ERROR"
        all_tests_passed = all_tests_passed and passed
        
        print(f"{status} - {description}")
        print(f"  Usuario contestó: '{user_answer}'")
        print(f"  Resultado obtenido: {result}")
        print(f"  Resultado esperado: {expected_result}")
        print("-" * 60)
    
    # Resumen final
    if all_tests_passed:
        print("\n✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
    
    return all_tests_passed

if __name__ == "__main__":
    success = test_verdadero_falso_questions()
    sys.exit(0 if success else 1)
