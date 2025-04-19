"""
Módulo compartido para constantes, funciones y utilidades comunes de SMART_STUDENT.

Este módulo evita las importaciones circulares al proporcionar un punto central
para las definiciones usadas en múltiples partes de la aplicación.
"""

import reflex as rx
import sys

# Constantes compartidas
PRIMARY_COLOR_SCHEME = "blue"
ACCENT_COLOR_SCHEME = "amber"
FONT_FAMILY = "Poppins, sans-serif"
GOOGLE_FONT_STYLESHEET = [
    "https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap"
]
MAX_QUESTIONS = 15
EVALUATION_TIME = 120  # Tiempo en segundos (2 minutos = 120 segundos)
MIN_RESUMEN_LENGTH = 50

# Importación de Módulos Backend
BACKEND_AVAILABLE = False
try:
    from backend import (
        config_logic,
        db_logic,
        login_logic,
        resumen_logic,
        map_logic,
        eval_logic,
    )
    if hasattr(db_logic, "inicializar_db") and callable(db_logic.inicializar_db):
        db_logic.inicializar_db()
        print("INFO: Base de datos inicializada.")
    else:
        print("WARN: Función 'inicializar_db' no encontrada en db_logic.")
    print("INFO: Módulos de backend importados correctamente.")
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(
        f"ERROR CRITICO: No se pueden importar módulos del backend: {e}.",
        file=sys.stderr,
    )
    print(
        "Verifique: 1) Ejecutar desde raíz, 2) 'backend/__init__.py' existe, 3) No hay errores internos en backend/*.py.",
        file=sys.stderr,
    )

    class MockLogic:
        def __getattr__(self, name):
            def _mock_func(*args, **kwargs):
                print(f"ADVERTENCIA: Usando Mock para '{name}({args=}, {kwargs=})'.")
                mock_data = {
                    "CURSOS": {"Mock Curso": {"Mock Libro": "mock.pdf"}},
                    "verificar_login": lambda u, p: (u == "test" and p == "123")
                    or (u == "felipe" and p == "1234"),
                    "generar_resumen_logica": lambda *a, **kw: {
                        "status": "EXITO",
                        "resumen": "Resumen Mock...",
                        "puntos": "1. Punto Mock 1...\n2. Punto Mock 2...",
                        "message": "Generado con Mock",
                    },
                    "generar_resumen_pdf_bytes": lambda *a, **kw: b"%PDF...",
                    "generar_nodos_localmente": lambda *a, **kw: {
                        "status": "EXITO",
                        "nodos": [
                            {
                                "titulo": "Nodo Central",
                                "subnodos": ["Subnodo A", "Subnodo B"],
                            },
                            {"titulo": "Otro Nodo"},
                        ],
                    },
                    "generar_mermaid_code": lambda *a, **kw: (
                        "graph TD\nA[Centro]-->B(Nodo 1);B-->C{Sub A};B-->D(Sub B);A-->E(Otro);",
                        None,
                    ),
                    "generar_visualizacion_html": lambda *a, **kw: "data:text/html,<html><body><h1>Mock Map Viz</h1></body></html>",
                    "generar_evaluacion": lambda *a, **kw: {
                        "status": "EXITO",
                        "preguntas": [
                            {
                                "pregunta": "¿Mock Pregunta 1?",
                                "tipo": "opcion_multiple",
                                "opciones": [
                                    {"id": "a", "texto": "Op A"},
                                    {"id": "b", "texto": "Op B (Correcta)"},
                                ],
                                "respuesta_correcta": "b",
                                "explicacion": "Expl Mock 1.",
                            }
                        ],
                    },
                    "obtener_estadisticas_usuario": lambda *a, **kw: [
                        {
                            "curso": "Mock C",
                            "libro": "Mock L",
                            "tema": "Mock T",
                            "puntuacion": 85.0,
                            "fecha": "Hoy",
                        }
                    ],
                    "guardar_resultado_evaluacion": lambda *a, **kw: print(
                        "Mock: Guardando resultado..."
                    ),
                }
                return (
                    mock_data.get(name, lambda *a, **kw: None)(*args, **kwargs)
                    if callable(mock_data.get(name))
                    else mock_data.get(name)
                )

            return _mock_func

    config_logic = login_logic = db_logic = resumen_logic = map_logic = eval_logic = (
        MockLogic()
    )
    print("ADVERTENCIA: Usando Mocks para la lógica del backend.", file=sys.stderr)

# Funciones de utilidad compartidas
def error_callout(message: rx.Var[str]):
    """Componente para mostrar mensajes de error."""
    return rx.cond(
        message != "",
        rx.callout.root(
            rx.callout.icon(rx.icon("triangle-alert")),
            rx.callout.text(message),
            color_scheme="red",
            role="alert",
            w="100%",
            my="1em",
            size="2",
        ),
    )

def _curso_sort_key(curso: str) -> tuple:
    """Función para ordenar cursos por nivel y número."""
    try:
        num_str = curso.split()[0]
        sufijos = ["ro", "do", "to", "vo", "mo"]
        for sufijo in sufijos:
            num_str = num_str.replace(sufijo, "")
        num = int(num_str) if num_str.isdigit() else 99
        nivel = "1" if "Básico" in curso else "2" if "Medio" in curso else "9"
        return (nivel, num)
    except Exception as e:
        print(f"Error en _curso_sort_key para '{curso}': {e}")
        return ("9", 99)
