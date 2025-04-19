"""
Aplicación SMART_STUDENT - Versión Optimizada y Depurada.

Script principal de la interfaz web con Reflex.
"""

import reflex as rx
import sys, os, datetime, traceback, re
from typing import Dict, List, Optional, Set, Union, Any

from .evaluaciones import EvaluationState

# ----> AÑADE ESTA LÍNEA <----
from .state import AppState, PRIMARY_COLOR_SCHEME, ACCENT_COLOR_SCHEME, GOOGLE_FONT_STYLESHEET, FONT_FAMILY, error_callout # Importa AppState y constantes/helpers necesarios desde state.py
# --------------------------

# --- AÑADIMOS LA FUNCIÓN PARA MOSTRAR LAS PREGUNTAS ACTIVAS ---
def vista_pregunta_activa():
    """Componente que muestra la pregunta activa durante la evaluación."""
    pregunta_actual = EvaluationState.current_eval_question
    if not isinstance(pregunta_actual, dict):
        print(f"WARN (vista_pregunta_activa): pregunta_actual no es válida: {pregunta_actual}")
        return rx.center(rx.spinner(size="3"), height="300px")  # Cambiado de "large" a "3"

    tipo_pregunta = pregunta_actual.get("tipo", "opcion_multiple")
    print(f"DEBUG (vista_pregunta_activa): Renderizando pregunta tipo '{tipo_pregunta}' idx={EvaluationState.eval_current_idx}")

    return rx.card(
        rx.vstack(
            # Encabezado (Progreso y Tiempo)
            rx.hstack(
                rx.text(f"Pregunta {EvaluationState.eval_current_idx + 1} de {EvaluationState.eval_total_q}"),
                rx.spacer(),
                rx.text(EvaluationState.eval_time_formatted, font_weight="bold", color=EvaluationState.eval_time_color),
                justify="between", width="100%", mb="1em"
            ),
            rx.progress(value=EvaluationState.eval_progress, width="100%", size="2", color_scheme=PRIMARY_COLOR_SCHEME, mb="1.5em"),

            # Texto de la pregunta
            rx.heading(pregunta_actual.get("pregunta", "Error al cargar texto"), size="5", mb="1.5em", text_align="left", width="100%"),

            # Opciones (Ejemplo para opción múltiple y V/F)
            rx.cond(
                (tipo_pregunta == "opcion_multiple") | (tipo_pregunta == "alternativas") | (tipo_pregunta == "verdadero_falso"),
                 rx.radio_group(
                     rx.vstack(
                         rx.foreach(
                             EvaluationState.get_current_question_options,
                             lambda opcion: rx.radio(opcion["texto"], value=opcion["id"], size="2", my="0.2em")
                         ),
                         spacing="2", align_items="start"
                     ),
                     value=EvaluationState.eval_user_answers.get(EvaluationState.eval_current_idx, ""),
                     on_change=lambda value: EvaluationState.set_eval_answer(value),
                     width="100%",
                 ),
                 rx.text(f"UI para tipo '{tipo_pregunta}' aún no implementada."), # Placeholder
            ),

            # Botones de Navegación (Simplificado sin confirmación por ahora)
            rx.hstack(
                rx.button("Anterior", on_click=EvaluationState.prev_eval_question, is_disabled=EvaluationState.is_first_eval_question, variant="outline"),
                rx.spacer(),
                 rx.cond(
                     EvaluationState.is_last_eval_question,
                     rx.button("Terminar Evaluación", on_click=EvaluationState.calculate_eval_score, color_scheme="green"),
                     rx.button("Siguiente", on_click=EvaluationState.next_eval_question)
                 ),
                margin_top="2em", width="100%"
            ),
            # Mensaje de error específico
            error_callout(EvaluationState.eval_error_message),
            spacing="4", width="100%", max_width="700px", align_items="center"
        ),
        padding="2em", width="100%", max_width="800px"
    )
# --- FIN DE LA FUNCIÓN PARA MOSTRAR LAS PREGUNTAS ACTIVAS ---

# Definimos la función de evaluación directamente aquí para evitar problemas de importación
def evaluacion_tab():
    """Contenido de la pestaña de evaluación, muestra formulario o quiz activo."""
    # Print de debug para renderizado
    print(f"DEBUG (RENDER evaluacion_tab): Estado ACTUAL -> Curso='{AppState.selected_curso}', Libro='{AppState.selected_libro}', Tema='{AppState.selected_tema}', EvalActiva={EvaluationState.is_eval_active}")

    return rx.vstack(
        # Título se muestra siempre
        rx.heading("📝 Evaluación de Conocimientos", size="6", mb="1em", text_align="center"),

        # --- LÓGICA CONDICIONAL ---
        rx.cond(
            EvaluationState.is_eval_active,  # SI la evaluación está activa...
            vista_pregunta_activa(),         # ...muestra la vista de la pregunta.

            # SI NO (la evaluación no está activa)...
            rx.vstack(                       # ...muestra el formulario de configuración.
                rx.text(
                    "Pon a prueba tu comprensión del tema con preguntas generadas automáticamente.",
                    color="gray.500", mb="2em", text_align="center", max_width="600px",
                ),
                error_callout(AppState.error_message_ui), # Error general de UI
                rx.card(
                    rx.vstack(
                        rx.select(
                            AppState.cursos_list, placeholder="Selecciona un Curso...",
                            value=AppState.selected_curso, on_change=AppState.handle_curso_change,
                            size="3", color_scheme=PRIMARY_COLOR_SCHEME, width="100%",
                        ),
                        rx.select(
                            AppState.libros_para_curso, placeholder="Selecciona un Libro...",
                            value=AppState.selected_libro, on_change=AppState.handle_libro_change,
                            size="3", color_scheme=PRIMARY_COLOR_SCHEME, width="100%",
                            is_disabled=rx.cond(~AppState.selected_curso, True, False), # Simplificado
                        ),
                        rx.text_area(
                            placeholder="Tema específico a evaluar...",
                            value=AppState.selected_tema, on_change=AppState.set_selected_tema,
                            size="3", min_height="100px", width="100%",
                            is_disabled=rx.cond(~AppState.selected_libro, True, False), # Simplificado
                        ),
                        rx.button(
                            rx.cond(
                                EvaluationState.is_generation_in_progress, # Usa EvaluationState
                                rx.hstack(rx.spinner(size="2"), "Generando evaluación..."),
                                "Crear Evaluación"
                            ),
                            on_click=EvaluationState.generate_evaluation, # Llama al método correcto
                            size="3", color_scheme="purple", width="100%", margin_top="1em",
                            is_disabled=rx.cond(
                                (AppState.selected_tema == "") | EvaluationState.is_generation_in_progress,
                                True, False
                            ),
                        ),
                       width="100%", spacing="4", padding="2em",
                    ),
                    variant="surface", width="100%", max_width="500px",
                ),
              # Layout del formulario
              width="100%", spacing="4", align_items="center", padding="1em", margin_top="1em"
            )
        ),
        # --- FIN LÓGICA CONDICIONAL ---

        # Layout general de la pestaña
        width="100%",
        align_items="center",
        padding="1em",
    )

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

# Constantes
PRIMARY_COLOR_SCHEME = "blue"
ACCENT_COLOR_SCHEME = "amber"
FONT_FAMILY = "Poppins, sans-serif"
GOOGLE_FONT_STYLESHEET = [
    "https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap"
]

# Helper Function
def _curso_sort_key(curso: str) -> tuple:
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


# Funciones Helper para UI
def create_card(
    title, icon, description, action_text, on_click, color_scheme=PRIMARY_COLOR_SCHEME
):
    return rx.card(
        rx.vstack(
            rx.icon(icon, size=52, color=f"var(--{color_scheme}-9)"),
            rx.heading(title, size="4", mt="0.5em", text_align="center", flex_grow=0),
            rx.text(
                description,
                text_align="center",
                size="2",
                color_scheme="gray",
                flex_grow=1,
            ),
            rx.spacer(height="0.8em"),
            rx.box(
                rx.button(
                    action_text,
                    on_click=on_click,
                    size="2",
                    variant="soft",
                    color_scheme=color_scheme,
                    width="180px",
                ),
                width="100%",
                display="flex",
                justify_content="center",
            ),
            align="center",
            justify="between",
            p="1.8em",
            spacing="3",
            h="100%",
        ),
        variant="surface",
        size="3",
        h="320px",
        min_width="300px",
        as_child=True,
    )

def error_callout(message: rx.Var[str]):
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

def nav_button(text: str, tab_name: rx.Var[str], active_tab: rx.Var[str]):
    return rx.button(
        text,
        on_click=lambda: AppState.set_active_tab(tab_name),
        variant=rx.cond(active_tab == tab_name, "solid", "ghost"),
        color_scheme=rx.cond(active_tab == tab_name, PRIMARY_COLOR_SCHEME, "gray"),
        size="2",
    )

# Definición de Páginas/Pestañas
def login_page():
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.icon("graduation-cap", size=36, color_scheme=PRIMARY_COLOR_SCHEME),
                rx.vstack(
                    rx.heading(
                        "SMART_STUDENT", size="8", weight="bold", text_align="center"
                    ),
                    rx.spacer(height="0.5em"),
                    rx.text(
                        "Aprende, Crea y Destaca",
                        color_scheme="gray",
                        text_align="center",
                    ),
                    spacing="0",
                    align_items="center",
                ),
                spacing="3",
                align_items="center",
                justify="center",
                margin_bottom="1em",
                width="100%",
            ),
            rx.card(
                rx.form(
                    rx.vstack(
                        rx.heading("Iniciar Sesión", size="6", text_align="center"),
                        rx.text(
                            "Accede a tus aprendizajes",
                            margin_bottom="1.5em",
                            color_scheme="gray",
                            text_align="center",
                        ),
                        rx.input(
                            placeholder="Usuario",
                            id="username",
                            on_change=AppState.set_username_input,
                            value=AppState.username_input,
                            size="3",
                            width="100%",
                            required=True,
                            auto_focus=True,
                        ),
                        rx.input(
                            placeholder="Contraseña",
                            id="password",
                            type="password",
                            on_change=AppState.set_password_input,
                            value=AppState.password_input,
                            size="3",
                            width="100%",
                            required=True,
                        ),
                        rx.cond(
                            AppState.login_error_message != "",
                            rx.text(
                                AppState.login_error_message,
                                color="red",
                                size="2",
                                mt="0.5em",
                                text_align="center",
                            ),
                        ),
                        rx.button(
                            "Iniciar Sesión",
                            type="submit",
                            width="100%",
                            color_scheme=PRIMARY_COLOR_SCHEME,
                            size="3",
                            margin_top="1em",
                        ),
                        rx.link(
                            "¿Olvidaste tu contraseña?",
                            size="2",
                            color_scheme="gray",
                            mt="1em",
                            href="#",
                            _hover={
                                "color": f"var(--{PRIMARY_COLOR_SCHEME}-9)",
                                "text_decoration": "underline",
                            },
                            text_align="center",
                        ),
                        spacing="4",
                        padding="1.5em",
                        width="100%",
                    ),
                    on_submit=AppState.handle_login,
                    reset_on_submit=False,
                ),
                width="400px",
                max_width="90%",
            ),
            spacing="4",
            width="100%",
            height="100vh",
            padding="2em",
            align="center",
            justify="center",
        ),
        width="100%",
        height="100%",
    )

def inicio_tab():
    """Contenido de la pestaña de inicio."""
    return rx.vstack(
        rx.heading("🏠 Bienvenido a SMART STUDENT", size="6", mb="2em", text_align="center"),
        rx.text(
            "Tu asistente de estudio inteligente potenciado por IA. Explora las herramientas para mejorar tu aprendizaje.",
            color="gray.500",
            mb="2em",
            text_align="center",
            max_width="800px",
        ),
        rx.center(
            rx.card(
                rx.vstack(
                    rx.grid(
                        create_card(
                            "Libros Digitales",
                            "book",
                            "Accede a tus libros digitales y contenidos de estudio.",
                            "Ver Libros",
                            lambda: AppState.set_active_tab("libros"),
                            "green",
                        ),
                        create_card(
                            "Resúmenes Inteligentes",
                            "file-text",
                            "Genera resúmenes y puntos clave para estudiar de forma eficiente.",
                            "Crear Resumen",
                            lambda: AppState.set_active_tab("resumen"),
                            PRIMARY_COLOR_SCHEME,
                        ),
                        create_card(
                            "Mapas Conceptuales",
                            "git-branch",
                            "Visualiza conexiones entre conceptos para mejorar tu comprensión.",
                            "Crear Mapa",
                            lambda: AppState.set_active_tab("mapa"),
                            ACCENT_COLOR_SCHEME,
                        ),
                        create_card(
                            "Evaluaciones",
                            "clipboard-check",
                            "Pon a prueba tu conocimiento con preguntas generadas automáticamente.",
                            "Crear Evaluación",
                            lambda: AppState.set_active_tab("evaluacion"),
                            "purple",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    spacing="6",
                    width="100%",
                    padding="2em",
                ),
                variant="surface",
                width="100%",
                max_width="1200px",
            )
        ),
        rx.center(
            rx.card(
                rx.vstack(
                    rx.heading(
                        "Recursos Populares", size="5", mb="1em", text_align="center"
                    ),
                    rx.hstack(
                        rx.foreach(
                            ["Matemáticas", "Ciencias", "Historia", "Lenguaje"],
                    lambda c: rx.cond(
                        AppState.cursos_list.contains(c),
                        rx.button(
                            c,
                            # --- CORRECCIÓN AQUÍ ---
                            # Pasamos la referencia al método y el argumento capturado 'c'
                            on_click=AppState.go_to_curso_and_resumen(c),
                                    variant="soft",
                                    color_scheme=PRIMARY_COLOR_SCHEME,
                                    size="3",
                                ),
                                rx.fragment(),
                            ),
                        ),
                        spacing="3",
                        justify="center",
                        wrap="wrap",
                    ),
                    width="100%",
                    align="center",
                    padding="2em",
                ),
                variant="surface",
                width="100%",
                max_width="800px",
                margin_top="2em",
            )
        ),
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="1em",
    )

def resumen_tab():
    """Contenido de la pestaña de resúmenes."""
    return rx.vstack(
        rx.heading("📄 Genera Resúmenes Inteligentes", size="6", mb="2em", text_align="center"),
        rx.text(
            "Simplifica temas complejos con resúmenes generados por IA para facilitar tu comprensión y estudio.",
            color="gray.500",
            mb="2em",
            text_align="center",
            max_width="600px",
        ),
        error_callout(AppState.error_message_ui),
        rx.card(
            rx.vstack(
                rx.select(
                    AppState.cursos_list,
                    placeholder="Selecciona un Curso...",
                    value=AppState.selected_curso,
                    on_change=AppState.handle_curso_change,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                ),
                rx.select(
                    AppState.libros_para_curso,
                    placeholder="Selecciona un Libro...",
                    value=AppState.selected_libro,
                    on_change=AppState.handle_libro_change,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                    is_disabled=rx.cond(
                        (AppState.selected_curso == "") | (AppState.selected_curso == "Error al Cargar Cursos"),
                        True,
                        False,
                    ),
                ),
                rx.text_area(
                    placeholder="Tema específico a resumir...",
                    value=AppState.selected_tema,
                    on_change=AppState.set_selected_tema,
                    size="3",
                    min_height="100px",
                    width="100%",
                    is_disabled=rx.cond(
                        AppState.selected_libro == "",
                        True,
                        False,
                    ),
                ),
                rx.hstack(
                    rx.hstack(
                        rx.switch(
                            is_checked=AppState.include_puntos,
                            on_change=AppState.set_include_puntos,
                            size="2",
                            color_scheme=ACCENT_COLOR_SCHEME,
                            disabled=rx.cond(
                                AppState.selected_tema == "", True, False
                            ),
                        ),
                        rx.text("Incluir puntos clave", size="2", ml="0.5em"),
                        spacing="2",
                        align_items="center",
                    ),
                    rx.spacer(),
                    width="100%",
                    align_items="center",
                    margin_top="0.5em",
                ),
                rx.button(
                    rx.cond(
                        AppState.is_generating_resumen,
                        rx.hstack(rx.spinner(size="2"), "Generando resumen..."),
                        "Generar Resumen"
                    ),
                    on_click=AppState.generate_summary,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                    margin_top="1em",
                    is_disabled=rx.cond(
                        AppState.is_generating_resumen | (AppState.selected_tema == ""),
                        True,
                        False,
                    ),
                ),
                width="100%",
                spacing="4",
                padding="2em",
            ),
            variant="surface",
            width="100%",
            max_width="500px",
        ),
        # Espacio para mostrar el resumen generado
        rx.cond(
            (AppState.resumen_content != "") | (AppState.puntos_content != ""),
            rx.card(
                rx.vstack(
                    rx.heading("Resultado", size="5", mb="1em"),
                    rx.cond(
                        AppState.resumen_content != "",
                        rx.vstack(
                            rx.heading("Resumen", size="4", mb="0.5em"),
                            rx.box(
                                rx.markdown(AppState.resumen_content),
                                max_h="55vh",
                                overflow_y="auto",
                                bg="var(--accent-2)",
                                p="1.5em",
                                border_radius="large",
                                w="100%",
                                border="1px solid var(--accent-5)",
                            ),
                            width="100%",
                            align_items="flex-start",
                            spacing="2",
                            margin_bottom="1.5em",
                        ),
                    ),
                    rx.cond(
                        AppState.include_puntos & (AppState.puntos_content != ""),
                        rx.vstack(
                            rx.heading("Puntos Clave", size="4", mb="0.5em"),
                            rx.box(
                                rx.markdown(AppState.puntos_content),
                                max_h="55vh",
                                overflow_y="auto",
                                bg="var(--gray-2)",
                                p="1.5em",
                                border_radius="large",
                                w="100%",
                                border="1px solid var(--gray-5)",
                            ),
                            width="100%",
                            align_items="flex-start",
                            spacing="2",
                        ),
                    ),
                    rx.hstack(
                        rx.button(
                            rx.icon("download", mr="0.2em"),
                            "Descargar PDF",
                            on_click=AppState.download_pdf,
                            variant="soft",
                            size="2",
                            color_scheme=PRIMARY_COLOR_SCHEME,
                        ),
                        rx.button(
                            rx.icon("git-branch", mr="0.2em"),
                            "Crear Mapa",
                            on_click=AppState.go_to_mapa_tab,
                            variant="soft",
                            size="2",
                            color_scheme=ACCENT_COLOR_SCHEME,
                            is_disabled=rx.cond(
                                AppState.is_generating_mapa,
                                True,
                                False,
                            ),
                        ),
                        rx.button(
                            rx.icon("clipboard-check", mr="0.2em"),
                            "Crear Evaluación",
                            on_click=AppState.go_to_evaluacion_tab,
                            variant="soft",
                            size="2",
                            color_scheme="purple",
                        ),
                        justify="center",
                        spacing="4",
                        mt="1.5em",
                        width="100%",
                    ),
                    width="100%",
                    padding="2em",
                    spacing="4",
                ),
                variant="surface",
                width="100%",
                max_width="800px",
                margin_top="2em",
            ),
        ),
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="5em",
    )

def mapa_tab():
    """Contenido de la pestaña de mapas conceptuales."""
    return rx.vstack(
        rx.heading("🧠 Crea Mapas Conceptuales", size="6", mb="2em", text_align="center"),
        rx.text(
            "Visualiza relaciones entre conceptos y fortalece tu comprensión con mapas conceptuales personalizados.",
            color="gray.500",
            mb="2em",
            text_align="center",
            max_width="600px",
        ),
        error_callout(AppState.error_message_ui),
        rx.card(
            rx.vstack(
                rx.select(
                    AppState.cursos_list,
                    placeholder="Selecciona un Curso...",
                    value=AppState.selected_curso,
                    on_change=AppState.handle_curso_change,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                ),
                rx.select(
                    AppState.libros_para_curso,
                    placeholder="Selecciona un Libro...",
                    value=AppState.selected_libro,
                    on_change=AppState.handle_libro_change,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                    is_disabled=rx.cond(
                        (AppState.selected_curso == "") | (AppState.selected_curso == "Error al Cargar Cursos"),
                        True,
                        False,
                    ),
                ),
                rx.text_area(
                    placeholder="Tema central del mapa...",
                    value=AppState.selected_tema,
                    on_change=AppState.set_selected_tema,
                    size="3",
                    min_height="100px",
                    width="100%",
                ),
                rx.hstack(
                    rx.hstack(
                        rx.switch(
                            is_checked=AppState.mapa_orientacion_horizontal,
                            on_change=AppState.set_mapa_orientacion,
                            size="2",
                            color_scheme=ACCENT_COLOR_SCHEME,
                        ),
                        rx.text("Orientación Horizontal", size="2", ml="0.5em"),
                        spacing="2",
                        align_items="center",
                    ),
                    rx.spacer(),
                    width="100%",
                    align_items="center",
                    margin_top="0.5em",
                ),
                rx.button(
                    rx.cond(
                        AppState.is_generating_mapa,
                        rx.hstack(rx.spinner(size="2"), "Generando mapa..."),
                        "Generar Mapa"
                    ),
                    on_click=AppState.generate_map,
                    size="3",
                    color_scheme=ACCENT_COLOR_SCHEME,
                    width="100%",
                    margin_top="1em",
                    is_disabled=rx.cond(
                        AppState.is_generating_mapa | (AppState.selected_tema == ""),
                        True,
                        False,
                    ),
                ),
                width="100%",
                spacing="4",
                padding="2em",
            ),
            variant="surface",
            width="100%",
            max_width="500px",
        ),
        # Espacio para mostrar el mapa generado
        rx.cond(
            AppState.mapa_image_url != "",
            rx.card(
                rx.vstack(
                    rx.heading("Mapa Conceptual", size="5", mb="1em", text_align="center"),
                    rx.box(
                        rx.html(
                            f'<iframe src="{AppState.mapa_image_url}" width="100%" height="600px" style="border:1px solid var(--gray-5); border-radius:8px; background:white;"></iframe>'
                        ),
                        width="100%",
                        min_h="620px",
                        border="1px solid var(--gray-4)",
                        border_radius="large",
                        box_shadow="sm",
                        p="0.5em",
                    ),
                    rx.hstack(
                        rx.button(
                            rx.icon("download", mr="0.2em"),
                            "Descargar PDF",
                            on_click=AppState.download_pdf,  # Cambiado de download_map_pdf a download_pdf
                            variant="soft",
                            size="2",
                            color_scheme=PRIMARY_COLOR_SCHEME,
                        ),
                        rx.button(
                            rx.icon("file-text", mr="0.2em"),
                            "Crear Resumen",
                            on_click=AppState.go_to_resumen_tab,
                            variant="soft",
                            size="2",
                            color_scheme=PRIMARY_COLOR_SCHEME,
                        ),
                        rx.button(
                            rx.icon("clipboard-check", mr="0.2em"),
                            "Crear Evaluación",
                            on_click=AppState.go_to_evaluacion_tab,
                            variant="soft",
                            size="2",
                            color_scheme="purple",
                        ),
                        justify="center",
                        spacing="4",
                        mt="1.5em",
                        width="100%",
                    ),
                    width="100%",
                    padding="2em",
                    spacing="4",
                ),
                variant="surface",
                width="100%",
                max_width="900px",
                margin_top="2em",
            ),
        ),
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="5em",
    )

def perfil_tab():
    return rx.vstack(
        rx.heading("Perfil y Progreso", size="6", mb="1.5em", text_align="center"),
        rx.grid(
            # Aquí iría el contenido del perfil
        ),
        rx.card(
            # Aquí iría el contenido de estadísticas
        ),
        w="100%",
        max_width="1000px",
        margin="0 auto",
        p="2em",
        spacing="5",
    )

def ayuda_tab():
    content = {"empezar": "### Cómo empezar\n1...", "faq": "### FAQ\n**Q:** ...?"}
    return rx.vstack(
        rx.heading("Ayuda", size="6", mb="1em", text_align="center"),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Empezar", value="empezar"),
                rx.tabs.trigger("FAQ", value="faq"),
                size="2",
                w="100%",
                justify="center",
                border_bottom="1px solid var(--gray-6)",
            ),
            rx.tabs.content(
                rx.box(
                    rx.markdown(content["empezar"]),
                    p="1.5em",
                    border="1px solid var(--gray-4)",
                    border_radius="medium",
                    mt="1em",
                    bg="var(--gray-1)",
                ),
                value="empezar",
            ),
            rx.tabs.content(
                rx.box(
                    rx.markdown(content["faq"]),
                    p="1.5em",
                    border="1px solid var(--gray-4)",
                    border_radius="medium",
                    mt="1em",
                    bg="var(--gray-1)",
                ),
                value="faq",
            ),
            w="100%",
            default_value="empezar",
        ),
        w="100%",
        max_w="900px",
        m="0 auto",
        p="2em",
        spacing="4",
    )

def libros_tab():
    """Contenido de la pestaña de libros digitales."""
    return rx.vstack(
        rx.heading("📚 Biblioteca Digital", size="6", mb="2em", text_align="center"),
        rx.text(
            "Accede a tu colección de libros digitales para estudiar y repasar los contenidos académicos.",
            color="gray.500",
            mb="2em",
            text_align="center",
            max_width="600px",
        ),
        error_callout(AppState.error_message_ui),
        rx.card(
            rx.vstack(
                rx.select(
                    AppState.cursos_list,
                    placeholder="Selecciona un Curso...",
                    value=AppState.selected_curso,
                    on_change=AppState.handle_libros_curso_change,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                ),
                rx.select(
                    AppState.libros_para_curso,
                    placeholder="Selecciona un Libro...",
                    value=AppState.selected_libro,
                    on_change=AppState.handle_libros_libro_change,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                    is_disabled=rx.cond(
                        (AppState.selected_curso == "") | (AppState.selected_curso == "Error al Cargar Cursos"),
                        True,
                        False,
                    ),
                ),
                rx.cond(
                    (AppState.selected_curso != "") & (AppState.selected_libro != ""),
                    rx.link(
                        rx.button(
                            rx.hstack(
                                rx.icon("download", size=16), rx.text("Descargar PDF")
                            ),
                            size="3",
                            color_scheme="green",
                            variant="solid",
                            width="100%",
                            margin_top="1em",
                        ),
                        href=AppState.pdf_url,
                        is_external=False,
                        target="_blank",
                        width="100%",
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon("download", size=16), rx.text("Descargar PDF")
                        ),
                        is_disabled=True,
                        size="3",
                        width="100%",
                        color_scheme="gray",
                        margin_top="1em",
                    ),
                ),
                width="100%",
                spacing="4",
                padding="2em",
            ),
            variant="surface",
            width="100%",
            max_width="500px",
        ),
        rx.cond(
            (AppState.selected_curso != "") & (AppState.selected_libro != ""),
            rx.card(
                rx.vstack(
                    rx.heading("Información del Libro", size="5", mb="1em", text_align="center"),
                    rx.box(
                        rx.vstack(
                            rx.heading(AppState.selected_libro, size="4", mb="0.5em"),
                            rx.text(
                                f"Curso: {AppState.selected_curso}",
                                color="gray.500",
                                mb="0.5em",
                            ),
                            rx.text(
                                "Este libro contiene material educativo importante para tu aprendizaje.",
                                mb="1em",
                            ),
                            rx.link(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("file-text", mr="0.2em"),
                                        "Crear Resumen"
                                    ),
                                    variant="soft",
                                    size="2",
                                    color_scheme=PRIMARY_COLOR_SCHEME,
                                ),
                                on_click=lambda: AppState.set_active_tab("resumen"),
                                text_decoration="none",
                            ),
                            width="100%",
                            align_items="flex-start",
                            spacing="2",
                        ),
                        width="100%",
                    ),
                    width="100%",
                    padding="2em",
                    spacing="4",
                ),
                variant="surface",
                width="100%",
                max_width="500px",
                margin_top="2em",
            ),
        ),
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="5em",
    )

def main_dashboard():
     return rx.vstack(
         rx.hstack(
             rx.icon("graduation-cap", size=28, color_scheme=PRIMARY_COLOR_SCHEME),
             rx.heading("SMART", size="5", weight="bold"),
             rx.heading("STUDENT", size="5", weight="light", color_scheme="gray"),
             rx.spacer(),
             rx.color_mode.switch(size="2"),
             rx.tooltip(
                 rx.button(
                     rx.icon("log-out", size=16),
                     # --- ¡¡LA CORRECCIÓN ESTÁ AQUÍ!! ---
                     on_click=AppState.logout,  # SIN LAMBDA, SIN PARÉNTESIS
                     # ----------------------------------
                     color_scheme="red",
                     variant="soft",
                     size="2",
                 ),
                 content="Cerrar Sesión",
             ),
             p="1.5em 2em", w="100%", bg="var(--gray-1)", border_bottom="1px solid var(--gray-4)",
             position="sticky", top="0", z_index="10", align_items="center", justify="start", mb="0.5em",
         ),
         rx.tabs.root(
             rx.tabs.list(
                 rx.tabs.trigger("Inicio", value="inicio", on_click=lambda: AppState.set_active_tab("inicio")),
                 rx.tabs.trigger("Libros", value="libros", on_click=lambda: AppState.set_active_tab("libros")),
                 rx.tabs.trigger("Resúmenes", value="resumen", on_click=lambda: AppState.set_active_tab("resumen")),
                 rx.tabs.trigger("Mapas", value="mapa", on_click=lambda: AppState.set_active_tab("mapa")),
                 rx.tabs.trigger("Evaluaciones", value="evaluacion", on_click=lambda: AppState.set_active_tab("evaluacion")),
                 rx.tabs.trigger("Perfil", value="perfil", on_click=lambda: AppState.set_active_tab("perfil")),
                 rx.tabs.trigger("Ayuda", value="ayuda", on_click=lambda: AppState.set_active_tab("ayuda")),
                 size="2", w="100%", justify="center", border_bottom="1px solid var(--gray-6)",
             ),
             rx.tabs.content(inicio_tab(), value="inicio"),
             rx.tabs.content(libros_tab(), value="libros"),
             rx.tabs.content(resumen_tab(), value="resumen"),
             rx.tabs.content(mapa_tab(), value="mapa"),
             rx.tabs.content(evaluacion_tab(), value="evaluacion"),
             rx.tabs.content(perfil_tab(), value="perfil"),
             rx.tabs.content(ayuda_tab(), value="ayuda"),
             value=AppState.active_tab,
             w="100%", h="calc(100vh - 60px)", padding="1em"
         ),
          w="100%", h="100vh", spacing="0", align_items="stretch",
     )

# Definición y Configuración de la App
app = rx.App(
    stylesheets=GOOGLE_FONT_STYLESHEET,
    style={"font_family": FONT_FAMILY},
    theme=rx.theme(
        accent_color=PRIMARY_COLOR_SCHEME,
        gray_color="slate",
        radius="medium",
        scaling="100%",
    ),
)
rx.Config.static_dir = "assets"
rx.Config.title = "Smart Student | Aprende, Crea y Destaca"
rx.Config.favicon = "/favicon.ico"

@app.add_page
def index() -> rx.Component:
    return rx.fragment(
        rx.script(
            "document.title = 'Smart Student | Aprende, Crea y Destaca'"
        ),
        rx.html('<link rel="icon" type="image/x-icon" href="/smartstudent_icon.ico">'),
        rx.cond(AppState.is_logged_in, main_dashboard(), login_page()),
    )