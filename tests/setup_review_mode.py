"""
Script para simular el modo de revisión y verificar visualmente
la correcta visualización de los colores en la UI.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reflex as rx
from mi_app_estudio.evaluaciones import EvaluationState

def setup_review_mode():
    """
    Configura un estado de EvaluationState para simular el modo de revisión
    con algunas preguntas y respuestas.
    """
    state = EvaluationState()
    
    # Crear algunas preguntas de prueba
    preguntas = [
        {
            "tipo": "verdadero_falso",
            "pregunta": "La Tierra es redonda.",
            "correcta": "verdadero",
            "explicacion": "La Tierra tiene forma de geoide, similar a una esfera."
        },
        {
            "tipo": "alternativas",
            "pregunta": "¿Cuál es la capital de Chile?",
            "alternativas": [
                {"id": "a", "texto": "Buenos Aires"},
                {"id": "b", "texto": "Santiago"},
                {"id": "c", "texto": "Lima"},
                {"id": "d", "texto": "Bogotá"}
            ],
            "correcta": "b",
            "explicacion": "Santiago es la capital de Chile."
        }
    ]
    
    # Configurar respuestas (una correcta y una incorrecta)
    respuestas = {
        0: "verdadero",  # Correcta
        1: "a"           # Incorrecta
    }
    
    # Configurar el estado para el modo de revisión
    state.eval_preguntas = preguntas
    state.eval_user_answers = respuestas
    state.eval_current_idx = 0
    state.is_reviewing_eval = True
    state.is_eval_active = True
    
    print("Estado de revisión configurado correctamente.")
    print("Para ver los colores en la UI:")
    print("1. Ejecuta la aplicación con: python -m reflex run")
    print("2. Navega a la pestaña de Evaluaciones")
    print("3. En un estado real, completa una evaluación y haz clic en 'Revisar'")
    print("4. Verifica que:")
    print("   - '¡Respuesta correcta!' aparezca en color verde")
    print("   - 'Respuesta incorrecta' aparezca en color rojo")
    
    return state

if __name__ == "__main__":
    print("\n=== Configuración para prueba visual del modo de revisión ===")
    setup_review_mode()
    print("\nPara forzar el modo de revisión durante pruebas, puedes insertar este código:")
    print("""
    # Código para forzar modo de revisión (solo para pruebas)
    EvaluationState.eval_preguntas = [
        {
            "tipo": "verdadero_falso",
            "pregunta": "La Tierra es redonda.",
            "correcta": "verdadero",
            "explicacion": "La Tierra tiene forma de geoide, similar a una esfera."
        },
        {
            "tipo": "alternativas", 
            "pregunta": "¿Cuál es la capital de Chile?",
            "alternativas": [
                {"id": "a", "texto": "Buenos Aires"},
                {"id": "b", "texto": "Santiago"},
                {"id": "c", "texto": "Lima"},
                {"id": "d", "texto": "Bogotá"}
            ],
            "correcta": "b", 
            "explicacion": "Santiago es la capital de Chile."
        }
    ]
    EvaluationState.eval_user_answers = {
        0: "verdadero",  # Correcta
        1: "a"           # Incorrecta
    }
    EvaluationState.eval_current_idx = 0
    EvaluationState.is_reviewing_eval = True
    EvaluationState.is_eval_active = True
    """)
