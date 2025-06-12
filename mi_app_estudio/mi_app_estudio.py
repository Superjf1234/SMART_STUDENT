"""
Aplicación SMART_STUDENT - Versión Optimizada y Depurada.

Script principal de la interfaz web con Reflex.
"""

import reflex as rx
import sys, os, datetime, traceback, re
from typing import Dict, List, Optional, Set, Union, Any

from .evaluaciones import EvaluationState
# Importar el módulo CuestionarioState para cuestionarios
from .cuestionario import CuestionarioState, cuestionario_tab_content
# Importar componentes optimizados para mensajes de revisión
from .review_components import mensaje_respuesta_correcta, mensaje_respuesta_incorrecta

from .state import AppState, PRIMARY_COLOR_SCHEME, ACCENT_COLOR_SCHEME, GOOGLE_FONT_STYLESHEET, FONT_FAMILY, error_callout # Importa AppState y constantes/helpers necesarios desde state.py

# --- AÑADIMOS LA FUNCIÓN PARA MOSTRAR LAS PREGUNTAS ACTIVAS ---
def vista_pregunta_activa():
    """Componente que muestra la pregunta activa durante la evaluación, accediendo directo al estado y con estructura corregida."""

    # Usamos rx.cond para manejar el caso inicial donde la pregunta puede no estar lista
    return rx.card(
        rx.vstack(
            # Encabezado (Progreso y Tiempo)
            rx.hstack(
                rx.text(f"{AppState.question_text} {EvaluationState.eval_current_idx + 1} {AppState.of_text} {EvaluationState.eval_total_q}"),
                rx.spacer(),
                rx.text(EvaluationState.eval_time_formatted, font_weight="bold", color=EvaluationState.eval_time_color),
                justify="between", width="100%", mb="1em"
            ),
            rx.progress(value=EvaluationState.eval_progress, width="100%", size="2", color_scheme=PRIMARY_COLOR_SCHEME, mb="1.5em"),

            # --- Contenido Condicional ---
            # Verifica si el índice actual es válido para la lista de preguntas Y la lista no está vacía
            rx.cond(
                (EvaluationState.eval_current_idx >= 0) & (EvaluationState.eval_preguntas.length() > EvaluationState.eval_current_idx),

                # --- SI EL ÍNDICE ES VÁLIDO Y LA PREGUNTA EXISTE ---
                rx.vstack(
                    # Usamos .get() con default por si acaso la clave falta
                    rx.heading(
                        EvaluationState.eval_preguntas[EvaluationState.eval_current_idx].get("pregunta", "Error al cargar pregunta"),
                        size="5", mb="1.5em", text_align="left", width="100%"
                    ),

                    # Opciones - CORREGIDO para manejar verdadero_falso con un grupo de radio vertical
                    rx.cond(
                        # Usamos .get() también para el tipo
                        EvaluationState.eval_preguntas[EvaluationState.eval_current_idx].get("tipo") == "verdadero_falso",
                          # SI ES VERDADERO/FALSO, usamos radio_group con orientación vertical (column)
                        rx.vstack(
                            rx.radio_group(
                                ["Verdadero", "Falso"],  # Los items como lista directamente
                                value=EvaluationState.current_radio_group_value,
                                on_change=lambda value: EvaluationState.set_eval_answer(value.lower()),
                                size="2",                                width="100%",
                                # Usamos 'column' en lugar de 'vertical'
                                direction="column", 
                                spacing="3",  # Espaciado entre opciones
                                is_disabled=EvaluationState.is_reviewing_eval,  # Deshabilitar en modo revisión
                            ),
                            # Mostrar resultado en modo revisión
                            rx.cond(
                                EvaluationState.is_reviewing_eval,
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.cond(
                                                EvaluationState.is_current_question_correct_in_review,
                                                rx.icon(
                                                    "check-circle",
                                                    color="green.500", 
                                                    size=18
                                                ),
                                                rx.icon(
                                                    "x-circle",
                                                    color="red.500", 
                                                    size=18
                                                )
                                            ),
                                            rx.cond(
                                                EvaluationState.is_current_question_correct_in_review,
                                                mensaje_respuesta_correcta(),
                                                mensaje_respuesta_incorrecta()
                                            ),
                                            spacing="2",
                                        ),
                                        rx.cond(
                                            ~EvaluationState.is_current_question_correct_in_review,
                                            rx.text(
                                                f"{AppState.correct_answers_text}: {EvaluationState.get_correct_answer_text}",
                                                color="gray.700", 
                                                font_style="italic",
                                                mt="0.5em"
                                            ),
                                        ),
                                        width="100%",
                                        align_items="flex_start",
                                        mt="1em",
                                        spacing="1",
                                    ),
                                    width="100%",
                                ),
                            ),
                            # Sección de Explicación (en modo revisión)
                            rx.cond(
                                EvaluationState.is_reviewing_eval & (EvaluationState.get_current_explanation != ""),
                                rx.box(
                                    rx.vstack(
                                        rx.heading(
                                            "Explicación:",
                                            size="4",
                                            color="gray.700",
                                            mb="0.5em",
                                            font_style="italic"  # Agregamos cursiva al título
                                        ),
                                        rx.text(
                                            EvaluationState.get_current_explanation,
                                            color="gray.700",
                                            line_height="1.6",
                                            font_style="italic"  # Agregamos cursiva al texto de explicación
                                        ),
                                        width="100%",
                                        align_items="flex_start",
                                        spacing="2",
                                        padding="1em",
                                        margin_top="1.5em",
                                        border="1px solid var(--gray-4)",
                                        border_radius="lg",
                                        bg="var(--gray-1)",
                                    ),
                                    width="100%",
                                    mb="1.5em",
                                ),
                            ),
                            width="100%",
                            spacing="2",
                            align_items="flex_start",
                            mb="1em",
                        ),
                        
                        # SI NO ES VERDADERO/FALSO, mantenemos el comportamiento original para otras opciones
                        rx.cond(
                            (EvaluationState.eval_preguntas[EvaluationState.eval_current_idx].get("tipo") == "opcion_multiple") |
                            (EvaluationState.eval_preguntas[EvaluationState.eval_current_idx].get("tipo") == "alternativas"),                            # --- CORRECCIÓN: Cambiamos cómo se crean las opciones de radio ---
                            rx.vstack(
                                rx.radio_group(
                                    # Definimos las opciones como una lista para radio_group
                                    EvaluationState.get_current_question_options_texts,
                                    value=EvaluationState.current_radio_group_value,
                                    on_change=lambda value: EvaluationState.set_eval_answer_by_text(value),
                                    size="2",
                                    width="100%",
                                    direction="column",
                                    spacing="3",
                                    is_disabled=EvaluationState.is_reviewing_eval,
                                ),
                                # Mostrar resultado en modo revisión
                                rx.cond(
                                    EvaluationState.is_reviewing_eval,
                                    rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.cond(
                                                EvaluationState.is_current_question_correct_in_review,
                                                rx.icon(
                                                    "check-circle",
                                                    color="green.500", 
                                                    size=18
                                                ),
                                                rx.icon(
                                                    "x-circle",
                                                    color="red.500", 
                                                    size=18
                                                )
                                            ),
                                                rx.cond(
                                                EvaluationState.is_current_question_correct_in_review,
                                                mensaje_respuesta_correcta(),
                                                mensaje_respuesta_incorrecta()
                                            ),
                                                spacing="2",
                                            ),
                                            rx.cond(
                                                ~EvaluationState.is_current_question_correct_in_review,
                                                rx.text(
                                                    f"{AppState.correct_answers_text}: {EvaluationState.get_correct_answer_text}",
                                                    color="gray.700", 
                                                    font_style="italic",
                                                    mt="0.5em"
                                                ),
                                            ),
                                            width="100%",
                                            align_items="flex_start",
                                            mt="1em",
                                            spacing="1",
                                        ),
                                        width="100%",
                                    ),
                                ),
                                # Sección de Explicación (en modo revisión)
                                rx.cond(
                                    EvaluationState.is_reviewing_eval & (EvaluationState.get_current_explanation != ""),
                                    rx.box(
                                        rx.vstack(
                                            rx.heading(
                                                "Explicación:",
                                                size="4",
                                                color="gray.700",
                                                mb="0.5em",
                                                font_style="italic"  # Agregamos cursiva al título
                                            ),
                                            rx.text(
                                                EvaluationState.get_current_explanation,
                                                color="gray.700",
                                                line_height="1.6",
                                                font_style="italic"  # Agregamos cursiva al texto de explicación
                                            ),
                                            width="100%",
                                            align_items="flex_start",
                                            spacing="2",
                                            padding="1em",
                                            margin_top="1.5em",
                                            border="1px solid var(--gray-4)",
                                            border_radius="lg",
                                            bg="var(--gray-1)",
                                        ),
                                        width="100%",
                                        mb="1.5em",
                                    ),
                                ),
                                width="100%",
                                spacing="2",
                                align_items="flex_start",
                                mb="1em"
                            ),

                            # IMPLEMENTACIÓN PARA SELECCIÓN MÚLTIPLE
                            rx.cond(
                                EvaluationState.eval_preguntas[EvaluationState.eval_current_idx].get("tipo") == "seleccion_multiple",
                                  # Implementación para selección múltiple (varias respuestas posibles)
                                rx.vstack(
                                    rx.text(
                                        "Selecciona todas las opciones correctas:",
                                        font_weight="bold",
                                        mb="0.5em",
                                        color="var(--purple-9)",
                                    ),
                                    rx.foreach(
                                        EvaluationState.get_current_question_options,
                                        lambda opcion: rx.hstack(
                                            rx.checkbox(
                                                # Corrección para evitar que las opciones aparezcan preseleccionadas
                                                # Solo marcar como checked si el ID específicamente está en el conjunto de respuestas
                                                is_checked=rx.cond(
                                                    # Primero verificar si hay una respuesta guardada y es un conjunto (set)
                                                    (EvaluationState.eval_user_answers.get(EvaluationState.eval_current_idx) != None),
                                                    # Si hay respuesta, verificar si este ID específico está en el conjunto mediante un método seguro
                                                    EvaluationState.check_if_option_selected(EvaluationState.eval_current_idx, opcion["id"]),
                                                    # Si no hay respuesta, siempre devolver False (no seleccionado)
                                                    False
                                                ),
                                                on_change=lambda selected=None, opt_id=opcion["id"]: EvaluationState.toggle_multiple_answer(opt_id),
                                                size="2",
                                                is_disabled=EvaluationState.is_reviewing_eval,
                                            ),
                                            rx.text(opcion["texto"], font_size="1rem", ml="0.5em"),
                                            my="0.5em",
                                            width="100%",
                                            align_items="center",
                                        )
                                    ),
                                    # Mostrar resultado en modo revisión
                                    rx.cond(
                                        EvaluationState.is_reviewing_eval,
                                        rx.box(
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.cond(
                                                EvaluationState.is_current_question_correct_in_review,
                                                rx.icon(
                                                    "check-circle",
                                                    color="green.500", 
                                                    size=18
                                                ),
                                                rx.icon(
                                                    "x-circle",
                                                    color="red.500", 
                                                    size=18
                                                )
                                            ),
                                                    rx.cond(
                                                EvaluationState.is_current_question_correct_in_review,
                                                mensaje_respuesta_correcta(),
                                                mensaje_respuesta_incorrecta()
                                            ),
                                                    spacing="2",
                                                ),
                                                rx.cond(
                                                    ~EvaluationState.is_current_question_correct_in_review,
                                                    rx.text(
                                                        f"Respuestas correctas: {EvaluationState.get_correct_answer_text}",
                                                        color="gray.700", 
                                                        font_style="italic",
                                                        mt="0.5em"
                                                    ),
                                                ),
                                                width="100%",
                                                align_items="flex_start",
                                                mt="1em",
                                                spacing="1",
                                            ),
                                            width="100%",
                                        ),
                                    ),
                                    # Sección de Explicación (en modo revisión)
                                    rx.cond(
                                        EvaluationState.is_reviewing_eval & (EvaluationState.get_current_explanation != ""),
                                        rx.box(
                                            rx.vstack(
                                                rx.heading(
                                                    rx.cond(
                                                        AppState.current_language == "es",
                                                        "Explicación:",
                                                        "Explanation:"
                                                    ),
                                                    size="4",
                                                    color="gray.700",
                                                    mb="0.5em",
                                                    font_style="italic"  # Agregamos cursiva al título
                                                ),
                                                rx.text(
                                                    EvaluationState.get_current_explanation,
                                                    color="gray.700",
                                                    line_height="1.6",
                                                    font_style="italic"  # Agregamos cursiva al texto de explicación
                                                ),
                                                width="100%",
                                                align_items="flex_start",
                                                spacing="2",
                                                padding="1em",
                                                margin_top="1.5em",
                                                border="1px solid var(--gray-4)",
                                                border_radius="lg",
                                                bg="var(--gray-1)",
                                            ),
                                            width="100%",
                                            mb="1.5em",
                                        ),
                                    ),
                                    width="100%",
                                    spacing="2",
                                    align_items="flex_start",
                                    mb="1em"
                                ),
                                
                                # Mensaje para otros tipos de pregunta no implementados
                                rx.text(
                                    f"UI para tipo '{EvaluationState.eval_preguntas[EvaluationState.eval_current_idx].get('tipo', 'desconocido')}' no implementada.",
                                    color="gray"
                                )
                            )
                        )
                    ),
                    spacing="4",
                    width="100%",
                    align_items="flex_start"
                ),

                # --- SI EL ÍNDICE NO ES VÁLIDO (o lista vacía inicialmente) ---
                rx.center(rx.spinner(size="3"), height="200px")  # Muestra spinner
            ),
            # --- Fin Contenido Condicional ---            # Botones de Navegación
            rx.hstack(
                rx.button(
                    AppState.previous_button_text,
                    on_click=EvaluationState.prev_eval_question,
                    is_disabled=EvaluationState.is_first_eval_question,
                    variant="outline"
                ),
                rx.spacer(),
                rx.cond(
                    EvaluationState.is_reviewing_eval,
                    # En modo revisión
                    rx.cond(
                        EvaluationState.is_last_eval_question,
                        rx.button(
                            AppState.finish_review_button_text,
                            on_click=EvaluationState.restart_evaluation,  # Volver al inicio
                            color_scheme="blue"
                        ),
                        rx.button(
                            AppState.next_button_text,
                            on_click=EvaluationState.next_eval_question
                        )
                    ),                    # En modo normal
                    rx.cond(
                        EvaluationState.is_last_eval_question,
                        rx.button(
                            AppState.finish_evaluation_button_text,
                            on_click=EvaluationState.calculate_eval_score,
                            color_scheme="green"
                        ),
                        rx.button(
                            AppState.next_button_text,
                            on_click=EvaluationState.next_eval_question
                        )
                    )
                ),
                margin_top="2em",
                width="100%"
            ),
            # Mensaje de error
            error_callout(EvaluationState.eval_error_message),

            # --- Modal de Resultados ---
            rx.dialog.root(
                rx.dialog.content(
                    rx.center(  # Envolvemos todo el contenido en un center para centrar todo
                        rx.vstack(
                            # Título y encabezado
                            rx.box(
                                rx.vstack(
                                    rx.heading(
                                        "🏆 " + AppState.evaluation_completed_text,
                                        size="5",
                                        text_align="center",
                                        mb="0.5em",
                                    ),
                                    # Título personalizado basado en la puntuación
                                    rx.heading(
                                        EvaluationState.eval_titulo_resultado,
                                        size="4",
                                        text_align="center",
                                        color=rx.cond(
                                            EvaluationState.eval_score < 40, "var(--orange-9)",
                                            rx.cond(
                                                EvaluationState.eval_score < 60, "var(--amber-9)",
                                                rx.cond(
                                                    EvaluationState.eval_score < 80, "var(--green-9)",
                                                    "var(--teal-9)"
                                                )
                                            )
                                        ),
                                    ),
                                    align_items="center",
                                    width="100%",
                                ),
                                width="100%",
                                mb="1.5em",
                                animation="fadeIn 0.5s ease-in-out",
                            ),
                            # Círculo con porcentaje grande
                            rx.center(
                                rx.box(
                                    rx.vstack(
                                        rx.heading(
                                            rx.cond(
                                                EvaluationState.eval_score == None,
                                                "0%",
                                                f"{EvaluationState.eval_score}%"
                                            ),
                                            size="1",
                                            color=rx.cond(
                                                EvaluationState.eval_score < 40, "var(--red-9)",
                                                rx.cond(
                                                    EvaluationState.eval_score < 60, "var(--orange-9)",
                                                    rx.cond(
                                                        EvaluationState.eval_score < 80, "var(--amber-9)",
                                                        rx.cond(
                                                            EvaluationState.eval_score < 90, "var(--green-9)",
                                                            "var(--teal-9)"
                                                        )
                                                    )
                                                )
                                            ),
                                            text_align="center",
                                        ),
                                        rx.text(
                                            AppState.completed_text,
                                            font_size="0.9em",
                                            color="gray",
                                            mt="-0.5em",
                                            text_align="center",
                                        ),
                                        align_items="center",
                                        justify_content="center",
                                        width="100%",
                                    ),
                                    width="150px",
                                    height="150px",
                                    border_radius="50%",
                                    display="flex",
                                    align_items="center",
                                    justify_content="center",
                                    bg=rx.cond(
                                        EvaluationState.eval_score < 40, "var(--red-2)",
                                        rx.cond(
                                            EvaluationState.eval_score < 60, "var(--orange-2)",
                                            rx.cond(
                                                EvaluationState.eval_score < 80, "var(--amber-2)",
                                                rx.cond(
                                                    EvaluationState.eval_score < 90, "var(--green-2)",
                                                    "var(--teal-2)"
                                                )
                                            )
                                        )
                                    ),
                                    border="3px solid",
                                    border_color=rx.cond(
                                        EvaluationState.eval_score < 40, "var(--red-6)",
                                        rx.cond(
                                            EvaluationState.eval_score < 60, "var(--orange-6)",
                                            rx.cond(
                                                EvaluationState.eval_score < 80, "var(--amber-6)",
                                                rx.cond(
                                                    EvaluationState.eval_score < 90, "var(--green-6)",
                                                    "var(--teal-6)"
                                                )
                                            )
                                        )
                                    ),
                                    shadow="lg",
                                ),
                                width="100%",
                                mb="1.5em",
                                animation="bounceIn 0.8s ease-out",
                            ),
                            # Texto de aciertos
                            rx.center(
                                rx.text(
                                    f"{AppState.correct_answers_text} {EvaluationState.eval_correct_count} {AppState.of_questions_text} {EvaluationState.eval_total_q} {AppState.questions_text}",
                                    font_weight="medium",
                                    text_align="center",
                                    margin_bottom="1em",
                                ),
                                width="100%",
                            ),
                            # Mensaje motivacional en dos líneas simétricas (MODIFICADO Y CENTRADO)
                            rx.center(
                                rx.vstack(
                                    rx.text(
                                        AppState.motivation_text_1,
                                        font_style="italic",
                                        font_weight="medium",
                                        text_align="center",  # Asegura centrado del texto
                                        color=rx.cond(
                                            EvaluationState.eval_score >= 80, "var(--teal-9)",
                                            rx.cond(
                                                EvaluationState.eval_score >= 60, "var(--green-9)",
                                                "var(--gray-9)"
                                            )
                                        ),
                                        font_size="1.1em",
                                    ),
                                    rx.text(
                                        AppState.motivation_text_2,
                                        font_style="italic",
                                        font_weight="medium",
                                        text_align="center",  # Asegura centrado del texto
                                        color=rx.cond(
                                            EvaluationState.eval_score >= 80, "var(--teal-9)",
                                            rx.cond(
                                                EvaluationState.eval_score >= 60, "var(--green-9)",
                                                "var(--gray-9)"
                                            )
                                        ),
                                        font_size="1.1em",
                                    ),
                                    spacing="0",
                                    width="100%",
                                    align_items="center",  # Centra los elementos hijos (textos) 
                                ),
                                width="100%",
                                margin_bottom="1.5em",
                                padding="0 10px",
                                justify_content="center",  # Asegura centrado horizontal
                                align_items="center",      # Asegura centrado vertical
                            ),
                            # Botones con diferentes colores de fondo pero mismo color de texto (ÁREA AGRANDADA)
                            rx.center(
                                rx.hstack(
                                    rx.button(
                                        AppState.new_evaluation_button_text,
                                        on_click=EvaluationState.restart_evaluation,
                                        color="white",
                                        background_color="var(--amber-9)",
                                        size="3",
                                        width="33%",
                                        height="64px",  # Doble altura normal
                                    ),
                                    rx.button(
                                        AppState.review_button_text,
                                        on_click=EvaluationState.review_evaluation,
                                        color="white",
                                        background_color="var(--blue-9)",
                                        size="3",
                                        width="33%",
                                        height="64px",  # Doble altura normal
                                    ),
                                    spacing="3",
                                    justify_content="center",
                                    width="70%",
                                ),
                                width="100%",
                            ),
                            spacing="4",
                            align_items="center",
                            justify_content="center",
                            padding="1.5em",
                            width="100%",
                            max_width="450px",
                            text_align="center",
                        ),
                        width="100%",  # El center ocupa todo el ancho disponible
                    ),
                    # Estilos adicionales para el modal
                    style={"--dialog-overlay-opacity": "0.8"},
                    animation="zoomIn 0.3s"
                ),
                open=EvaluationState.show_result_modal,
            ),
            # --- Fin Modal de Resultados ---

            spacing="4",
            width="100%",
            max_width="700px",
            align_items="center"
        ),
        padding="2em",
        width="100%",
        max_width="800px"
    )

# --- FIN DE LA FUNCIÓN PARA MOSTRAR LAS PREGUNTAS ACTIVAS ---

# Definimos la función de evaluación directamente aquí para evitar problemas de importación
def evaluacion_tab():
    """Contenido de la pestaña de evaluación, muestra formulario o quiz activo."""
    # Print de debug para renderizado
    print(f"DEBUG (RENDER evaluacion_tab): Estado ACTUAL -> Curso='{AppState.selected_curso}', Libro='{AppState.selected_libro}', Tema='{AppState.selected_tema}', EvalActiva={EvaluationState.is_eval_active}")
    
    # Usamos rx.cond para manejar los valores de repaso
    return rx.vstack(
        # Encabezado con robot
        rx.center(
            rx.hstack(
                rx.heading("📝 " + AppState.evaluation_heading_text, size="6"),
                rx.image(src="/robot_evaluaciones.png", width="80px", height="80px", ml="3em"),
                width="auto",
                justify="center",
                align_items="center",
                mb="2em",
            ),
        ),
        # Texto introductorio (estilo igual a cuestionario_tab)
        rx.text(
            AppState.evaluation_subtitle_text,
            color="gray.500",
            mb="2em",
            text_align="center",
            max_width="600px",
        ),
        # --- LÓGICA CONDICIONAL ---
        rx.cond(
            EvaluationState.is_eval_active,  # SI la evaluación está activa...
            vista_pregunta_activa(),         # ...muestra la vista de la pregunta.
            # SI NO (la evaluación no está activa)...
            rx.vstack(                       # ...muestra el formulario de configuración.
                error_callout(AppState.error_message_ui), # Error general de UI
                rx.card(
                    rx.vstack(
                        rx.select(
                            AppState.cursos_list, 
                            placeholder=AppState.select_course_evaluation_text,
                            value=AppState.selected_curso, 
                            on_change=AppState.handle_curso_change,
                            size="3", 
                            color_scheme=PRIMARY_COLOR_SCHEME, 
                            width="100%",
                        ),
                        rx.select(
                            AppState.libros_para_curso, 
                            placeholder=AppState.select_book_evaluation_text,
                            value=AppState.selected_libro, 
                            on_change=AppState.handle_libro_change,
                            size="3", 
                            color_scheme=PRIMARY_COLOR_SCHEME, 
                            width="100%",
                            is_disabled=rx.cond(AppState.selected_curso == "", True, False), 
                        ),
                        rx.text_area(
                            placeholder=AppState.evaluation_topic_placeholder_text,
                            value=AppState.selected_tema, 
                            on_change=AppState.set_selected_tema,
                            size="3", 
                            min_height="100px", 
                            width="100%",
                            is_disabled=rx.cond(AppState.selected_libro == "", True, False), 
                        ),
                        rx.button(
                            rx.cond(
                                EvaluationState.is_generation_in_progress, 
                                rx.hstack(rx.spinner(size="2"), rx.text(AppState.generating_evaluation_text)),
                                rx.hstack(rx.icon("clipboard-check"), rx.text(AppState.generate_evaluation_button_text))
                            ),
                            on_click=EvaluationState.generate_evaluation,
                            size="3", 
                            color_scheme="purple", 
                            width="100%", 
                            margin_top="1em",
                            is_disabled=rx.cond(
                                (AppState.selected_tema == "") | EvaluationState.is_generation_in_progress,
                                True, False
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
                # Layout del formulario
                width="100%", 
                spacing="4", 
                align_items="center", 
                padding="1em"
            )
        ),
        # --- FIN LÓGICA CONDICIONAL ---
        # Layout general de la pestaña (igual a cuestionario_tab)
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="5em", # Margen igual a cuestionario_tab
        padding_bottom="5em", # Agregar padding en la parte inferior
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
        on_click=lambda tab=tab_name: AppState.set_active_tab(tab),
        variant=rx.cond(active_tab == tab_name, "solid", "ghost"),
        color_scheme=rx.cond(active_tab == tab_name, PRIMARY_COLOR_SCHEME, "gray"),
        size="2",
    )

# Definición de Páginas/Pestañas
def login_page():
    # Añadimos los botones de idioma y modo oscuro en la parte superior derecha
    header_buttons = rx.hstack(
        rx.button(
            rx.cond(AppState.current_language == "es", "ES", "EN"),
            variant="soft",
            size="2",
            on_click=AppState.toggle_language,
            aria_label=AppState.switch_language_text,
        ),
        rx.color_mode.switch(size="2"),
        spacing="2",
        position="absolute",
        top="1em",
        right="1em",
        z_index="5",
    )
    
    return rx.box(
        header_buttons,
        rx.center(
            rx.vstack(
                rx.hstack(
                    rx.icon("graduation-cap", size=36, color_scheme=PRIMARY_COLOR_SCHEME),
                    rx.vstack(
                        rx.heading(
                            AppState.header_title_text, size="8", weight="bold", text_align="center"
                        ),
                        rx.spacer(height="0.5em"),
                        rx.text(
                            AppState.app_tagline_text,
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
                        rx.heading(AppState.login_title_text, size="6", text_align="center"),
                        rx.text(
                            AppState.login_subtitle_text,
                            margin_bottom="1.5em",
                            color_scheme="gray",
                            text_align="center",
                        ),
                        rx.input(
                            placeholder=AppState.username_placeholder_text,
                            id="username",
                            on_change=AppState.set_username_input,
                            value=AppState.username_input,
                            size="3",
                            width="100%",
                            required=True,
                            auto_focus=True,
                        ),
                        rx.input(
                            placeholder=AppState.password_placeholder_text,
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
                                AppState.login_error_text,
                                color="red",
                                size="2",
                                mt="0.5em",
                                text_align="center",
                            ),
                        ),
                        rx.button(
                            AppState.login_button_text,
                            type="submit",
                            width="100%",
                            color_scheme=PRIMARY_COLOR_SCHEME,
                            size="3",
                            margin_top="1em",
                        ),
                        rx.link(
                            AppState.forgot_password_text,
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
                        width="100%",                    ),
                    on_submit=AppState.handle_login,
                    reset_on_submit=False,
                ),                width="400px",
                max_width="90%",
            ),
        ),  # <- Cierre de rx.vstack
        spacing="4",
        width="100%",
        height="100vh",
        padding="2em",
        align="center",
        justify="center",
        ),
        width="100%",
        height="100%",
        position="relative",
    )

def inicio_tab():
    """Contenido de la pestaña de inicio."""
    return rx.vstack(
        # Encabezado con robot más alejado hacia la derecha
        rx.center(
            rx.hstack(
                rx.heading(AppState.welcome_text, size="6"),
                rx.image(src="/robot_turquesa.png", width="80px", height="80px", ml="3em"),
                width="auto",
                justify="center",
                align_items="center",
                mb="2em",
            ),
        ),
        
        rx.text(
            AppState.welcome_subtitle_text,
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
                            AppState.digital_books_title,
                            "book",
                            AppState.digital_books_desc,
                            AppState.view_books_text,
                            lambda: AppState.set_active_tab("libros"),
                            "green",
                        ),
                        create_card(
                            AppState.intelligent_summaries_title,
                            "file-text",
                            AppState.intelligent_summaries_desc,
                            AppState.create_summary_text,
                            lambda: AppState.set_active_tab("resumen"),
                            PRIMARY_COLOR_SCHEME,
                        ),
                        create_card(
                            AppState.concept_maps_title,
                            "git-branch",
                            AppState.concept_maps_desc,
                            AppState.create_map_text,
                            lambda: AppState.set_active_tab("mapa"),
                            ACCENT_COLOR_SCHEME,
                        ),
                        create_card(
                            AppState.questionnaires_title,
                            "file-question",
                            AppState.questionnaires_desc,
                            AppState.create_questionnaire_text,
                            lambda: AppState.set_active_tab("cuestionario"),
                            "cyan",
                        ),
                        create_card(
                            AppState.assessments_title,
                            "clipboard-check",
                            AppState.assessments_desc,
                            AppState.create_assessment_text,
                            lambda: AppState.set_active_tab("evaluacion"),
                            "purple",
                        ),
                        columns="3",
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
                        AppState.popular_resources_text, size="5", mb="1em", text_align="center", color="var(--gray-12)"
                    ),
                    rx.hstack(
                        rx.foreach(
                            [AppState.mathematics_text, AppState.science_text, AppState.history_text, AppState.language_text],
                    lambda c: rx.cond(
                        AppState.cursos_list.contains(c),
                        rx.button(
                            c,
                            # --- CORRECCIÓN AQUÍ ---
                            # Pasamos la referencia al método y el argumento capturado 'c'
                            on_click=lambda curso=c: AppState.go_to_curso_and_resumen(curso),
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
        ),        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="1em",
    )

def resumen_tab():
    """
    Contenido de la pestaña de resúmenes.
    """
    
    return rx.vstack(
        # Encabezado con robot
        rx.center(
            rx.hstack(
                rx.heading(
                    "📄 " + rx.cond(
                        AppState.current_language == "es",
                        "Genera Resúmenes Inteligentes",
                        "Generate Smart Summaries"
                    ), 
                    size="6"
                ),
                rx.image(src="/robot_resumen.png", width="80px", height="80px", ml="3em"),
                width="auto",
                justify="center",
                align_items="center",
                mb="2em",
            ),
        ),
        
        rx.text(
            rx.cond(
                AppState.current_language == "es",
                "Simplifica temas complejos con resúmenes generados por IA para facilitar tu comprensión y estudio.",
                "Simplify complex topics with AI-generated summaries to enhance your understanding and study."
            ),
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
                    placeholder=rx.cond(
                        AppState.current_language == "es",
                        "Tema específico a resumir...",
                        "Specific topic to summarize..."
                    ),
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
                        rx.text(
                            rx.cond(
                                AppState.current_language == "es",
                                "Incluir puntos clave",
                                "Include key points"
                            ), 
                            size="2", 
                            ml="0.5em"
                        ),
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
                        rx.hstack(
                            rx.spinner(size="2"), 
                            rx.cond(
                                AppState.current_language == "es",
                                rx.text("Generando resumen..."),
                                rx.text("Generating summary...")
                            )
                        ),
                        rx.cond(
                            AppState.current_language == "es",
                            rx.text("Generar Resumen"),
                            rx.text("Generate Summary")
                        )
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
        ),        # Espacio para mostrar el resumen generado
        rx.cond(
            (AppState.resumen_content != "") | (AppState.puntos_content != ""),
            rx.card(
                rx.vstack(
                    rx.heading(
                        rx.cond(
                            AppState.current_language == "es",
                            f"RESUMEN - {AppState.selected_tema.upper()}",
                            f"SUMMARY - {AppState.selected_tema.upper()}"
                        ),
                        size="5", mb="1em", text_align="center", width="100%"
                    ),
                    rx.cond(
                        AppState.resumen_content != "",
                        rx.vstack(
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
                            align_items="flex_start",
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
                            align_items="flex_start",
                            spacing="2",
                        ),
                    ),                    rx.hstack(                        rx.button(
                            rx.icon("download", mr="0.2em"),
                            "Descargar PDF",
                            on_click=AppState.download_pdf,
                            variant="soft",
                            size="2",
                            color_scheme="green",
                        ),
                        # Omitimos el botón "Crear Resumen" porque estamos en la pestaña de resumen
                        rx.button(
                            rx.icon("git-branch", mr="0.2em"),
                            "Crear Mapa",
                            on_click=lambda: AppState.set_active_tab("mapa"),
                            variant="soft",
                            size="2",
                            color_scheme="amber",
                        ),
                        rx.button(
                            rx.icon("book-open", mr="0.2em"),
                            "Crear Cuestionario",
                            on_click=lambda: AppState.set_active_tab("cuestionario"),
                            variant="soft",
                            size="2",
                            color_scheme="cyan",
                        ),
                        rx.button(
                            rx.icon("clipboard-check", mr="0.2em"),
                            "Crear Evaluación",
                            on_click=lambda: AppState.set_active_tab("evaluacion"),
                            variant="soft",
                            size="2",
                            color_scheme="purple",                        ),
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
        # Encabezado con robot
        rx.center(
            rx.hstack(
                rx.heading(
                    "🧠 " + rx.cond(
                        AppState.current_language == "es",
                        "Crea Mapas Conceptuales", 
                        "Create Mind Maps"
                    ), 
                    size="6"
                ),
                rx.image(src="/robot_mapas.png", width="80px", height="80px", ml="3em"),
                width="auto",
                justify="center",
                align_items="center",
                mb="2em",
            ),
        ),
        
        rx.text(
            rx.cond(
                AppState.current_language == "es",
                "Visualiza relaciones entre conceptos y fortalece tu comprensión con mapas conceptuales personalizados.",
                "Visualize relationships between concepts and strengthen your understanding with personalized mind maps."
            ),
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
                        rx.hstack(rx.spinner(size="2"), rx.text("Generando mapa...")),
                        rx.text("Generar Mapa")
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
                    rx.heading(
                        f"MAPA CONCEPTUAL - {AppState.selected_tema.upper()}", 
                        size="5", 
                        mb="1em", 
                        text_align="center",
                        width="100%"
                    ),
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
                    ),                    rx.hstack(                        rx.button(
                            rx.icon("download", mr="0.2em"),
                            "Descargar PDF",
                            on_click=AppState.download_pdf,  # Cambiado de download_map_pdf a download_pdf
                            variant="soft",
                            size="2",
                            color_scheme="green",
                        ),
                        rx.button(
                            rx.icon("file-text", mr="0.2em"),
                            "Crear Resumen",
                            on_click=lambda: AppState.set_active_tab("resumen"),
                            variant="soft",
                            size="2",
                            color_scheme="blue",
                        ),
                        # Omitimos el botón "Crear Mapa" porque estamos en la pestaña de mapa
                        rx.button(
                            rx.icon("book-open", mr="0.2em"),
                            "Crear Cuestionario",
                            on_click=lambda: AppState.set_active_tab("cuestionario"),
                            variant="soft",
                            size="2",
                            color_scheme="cyan",
                        ),
                        rx.button(
                            rx.icon("clipboard-check", mr="0.2em"),
                            "Crear Evaluación",
                            on_click=lambda: AppState.set_active_tab("evaluacion"),
                            variant="soft",
                            size="2",
                            color_scheme="purple",                        ),
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
    """Contenido de la pestaña de perfil y progreso."""
    return rx.vstack(
        # Diálogo de confirmación (modal)
        rx.cond(
            AppState.mostrar_dialogo_confirmacion,
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title(
                        rx.cond(
                            AppState.current_language == "es",
                            "Confirmar acción",
                            "Confirm action"
                        ),
                        color="var(--gray-12)"
                    ),
                    rx.dialog.description(AppState.mensaje_confirmacion, color="var(--gray-11)"),
                    rx.flex(
                        rx.button(
                            rx.cond(
                                AppState.current_language == "es",
                                "Cancelar",
                                "Cancel"
                            ),
                            variant="soft",
                            color_scheme="gray",
                            on_click=AppState.cancelar_accion,
                            size="2",
                        ),
                        rx.button(
                            rx.cond(
                                AppState.current_language == "es",
                                "Confirmar",
                                "Confirm"
                            ),
                            variant="solid",
                            color_scheme="red",
                            on_click=AppState.confirmar_accion,
                            size="2",
                        ),
                        justify="end",
                        gap="3",
                        margin_top="4",
                    ),
                    width="400px",
                ),
                open=AppState.mostrar_dialogo_confirmacion,
            ),
        ),
        # Encabezado principal con robot
        rx.center(
            rx.hstack(
                rx.heading(
                    rx.cond(
                        AppState.current_language == "es",
                        "👤 Perfil Personal", 
                        "👤 Personal Profile"
                    ),
                    size="6", 
                    color="var(--gray-12)"
                ),
                rx.image(src="/robot_perfil.png", width="80px", height="80px", ml="3em"),
                width="auto",
                justify="center",
                align_items="center",
                mb="2em",
            ),
        ),
        
        rx.text(
            rx.cond(
                AppState.current_language == "es",
                "Aquí puedes ver tu progreso y gestionar tu cuenta.",
                "Here you can view your progress and manage your account."
            ),
            color="var(--gray-9)",
            mb="2em",
            text_align="center",
            max_width="600px",
        ),
        
        # Tarjeta de perfil con ancho controlado - AUMENTADO max_width de 500px a 700px
        rx.card(
            rx.vstack(
                rx.hstack(
                    # Avatar/Imagen del perfil
                    rx.avatar(
                        fallback="F",
                        src="/assets/favicon.ico",
                        size="9",
                        border="2px solid var(--accent-6)",
                        margin_right="1em",
                    ),
                    
                    # Información del perfil
                    rx.vstack(
                        # Lista de información del usuario en formato horizontal
                        rx.vstack(
                            # Nombre
                            rx.hstack(
                                rx.text("Nombre:", font_weight="bold", width="150px", color_scheme="gray"),
                                rx.text("felipe", color="var(--gray-12)"),  # gray-12 es un color oscuro que se adapta al tema
                                width="100%",
                                justify="start",
                            ),
                            # Nivel
                            rx.hstack(
                                rx.text("Nivel:", font_weight="bold", width="150px", color_scheme="gray"),
                                rx.text("Estudiante Avanzado", color="var(--gray-12)"),
                                width="100%",
                                justify="start",
                            ),
                            # Curso Activo
                            rx.hstack(
                                rx.text("Curso Activo:", font_weight="bold", width="150px", color_scheme="gray"),
                                rx.text("8vo Básico", color="var(--gray-12)"),
                                width="100%",
                                justify="start",
                            ),
                            
                            # Asignaturas
                            rx.hstack(
                                rx.text("Asignaturas:", font_weight="bold", width="150px", color_scheme="gray"),
                                rx.hstack(
                                    rx.badge("MAT", color_scheme="blue"),
                                    rx.badge("CIEN", color_scheme="green"),
                                    rx.badge("HIS", color_scheme="amber"),
                                    rx.badge("LEN", color_scheme="purple"),
                                    spacing="2",
                                    wrap="nowrap",
                                    overflow_x="auto",
                                ),
                                width="100%",
                                justify="start",
                                align_items="center",
                            ),                            # Evaluaciones Completadas
                            rx.hstack(
                                rx.text("Evaluaciones Completadas:", font_weight="bold", width="150px", color_scheme="gray"),
                                rx.text(AppState.stats_history.length(), color="var(--gray-12)"),
                                width="100%",
                                justify="start",
                            ),
                            
                            spacing="2",
                            width="100%",
                        ),
                        width="100%",
                        align_items="flex_start",
                    ),
                    spacing="4", 
                    width="100%",
                    align_items="flex-start",                ),
                
                # Botones de acción
                rx.hstack(
                    rx.button(
                        rx.icon("user-cog", mr="0.2em"),
                        "Cambiar Contraseña",
                        variant="soft",
                        size="2",
                        color_scheme=PRIMARY_COLOR_SCHEME,
                    ),                    rx.button(
                        rx.icon("download", mr="0.2em"),
                        "Descargar Historial",
                        variant="soft",
                        size="2",
                        color_scheme=ACCENT_COLOR_SCHEME,
                        on_click=AppState.descargar_historial,
                    ),
                    rx.button(
                        rx.icon("trash", mr="0.2em"),
                        "Borrar Historial",
                        variant="soft",
                        size="2",
                        color_scheme="red",
                        on_click=AppState.mostrar_confirmacion_eliminar_historial,
                    ),
                    justify="center",
                    spacing="4",
                    mt="1.5em",
                    width="100%",
                ),
                
                width="100%",
                spacing="4",
                padding="2em",
            ),
            variant="surface",
            width="100%",
            max_width="1000px",
        ),
        
        # Tarjeta de estadísticas con estilo horizontal y colores distintos
        rx.card(
            rx.vstack(                    rx.center(
                        rx.hstack(
                            rx.icon("bar-chart", color="#4F46E5"),
                            rx.heading(
                                rx.cond(
                                    AppState.current_language == "es",
                                    "📊 Estadísticas de Aprendizaje", 
                                    "📊 Learning Statistics"
                                ), 
                                size="5", 
                                color="var(--gray-12)"
                            ),
                            spacing="2",
                        ),
                        width="100%"
                    ),
                
                # MODIFICADO: Progreso por materia - Barras de progreso alineadas
                rx.vstack(
                    rx.center(
                        rx.heading(
                            rx.cond(
                                AppState.current_language == "es",
                                "Progreso por Materia", 
                                "Progress by Subject"
                            ), 
                            size="4", 
                            mb="1em", 
                            color="var(--gray-12)"
                        ),
                        width="100%",
                    ),
                    
                    # Contenedor para las barras de progreso
                    rx.vstack(
                        # Matemáticas - Con ancho fijo para el texto
                        rx.hstack(
                            rx.box(
                                rx.text(
                                    rx.cond(
                                        AppState.current_language == "es",
                                        "Matemáticas", 
                                        "Mathematics"
                                    ), 
                                    align_self="center", 
                                    color="var(--gray-12)"
                                ),
                                width="150px", 
                                min_width="150px",
                            ),
                            rx.box(
                                rx.progress(
                                    value=AppState.matematicas_progress, # Valor dinámico basado en historial
                                    width="100%",
                                    height="20px",
                                    color_scheme="blue",
                                ),
                                width="100%",
                            ),
                            rx.text(f"{AppState.matematicas_progress}%", min_width="50px", text_align="right", color="var(--gray-12)"),
                            width="100%",
                            align_items="center",
                            spacing="3",
                        ),
                        
                        # Ciencias - Con ancho fijo para el texto
                        rx.hstack(
                            rx.box(
                                rx.text("Ciencias", align_self="center", color="var(--gray-12)"),
                                width="150px", 
                                min_width="150px",
                            ),
                            rx.box(
                                rx.progress(
                                    value=AppState.ciencias_progress, # Valor dinámico basado en historial
                                    width="100%",
                                    height="20px",
                                    color_scheme="green",
                                ),
                                width="100%",
                            ),
                            rx.text(f"{AppState.ciencias_progress}%", min_width="50px", text_align="right", color="var(--gray-12)"),
                            width="100%",
                            align_items="center",
                            spacing="3",
                        ),
                        
                        # Historia - Con ancho fijo para el texto
                        rx.hstack(
                            rx.box(
                                rx.text("Historia", align_self="center", color="var(--gray-12)"),
                                width="150px", 
                                min_width="150px",
                            ),
                            rx.box(
                                rx.progress(
                                    value=AppState.historia_progress, # Valor dinámico basado en historial
                                    width="100%",
                                    height="20px",
                                    color_scheme="amber",
                                ),
                                width="100%",
                            ),
                            rx.text(f"{AppState.historia_progress}%", min_width="50px", text_align="right", color="var(--gray-12)"),
                            width="100%",
                            align_items="center",
                            spacing="3",
                        ),
                        
                        # Lenguaje - Con ancho fijo para el texto
                        rx.hstack(
                            rx.box(
                                rx.text("Lenguaje", align_self="center", color="var(--gray-12)"),
                                width="150px", 
                                min_width="150px",
                            ),
                            rx.box(
                                rx.progress(
                                    value=AppState.lenguaje_progress, # Valor dinámico basado en historial
                                    width="100%",
                                    height="20px",
                                    color_scheme="purple",
                                ),
                                width="100%",
                            ),
                            rx.text(f"{AppState.lenguaje_progress}%", min_width="50px", text_align="right", color="var(--gray-12)"),
                            width="100%",
                            align_items="center",
                            spacing="3",
                        ),
                        
                        spacing="3",
                        width="100%",
                    ),
                    
                    width="100%",
                    padding_top="0.5em",
                    padding_bottom="1em",
                ),
                
                rx.divider(margin_y="1em"),
                
                # Estadísticas en diseño horizontal con colores diferentes
                rx.hstack(                    # Evaluaciones completadas - Azul
                    rx.box(
                        rx.vstack(
                            rx.heading(AppState.stats_history.length(), size="3", color="white", font_size="2em", mb="0"),
                            rx.text("Evaluaciones", font_size="sm", color="white", text_align="center"),
                            rx.text("Completadas", font_size="sm", color="white", text_align="center"),
                            align_items="center",
                            justify_content="center",
                            width="100%",
                            height="100%",
                        ),
                        background="linear-gradient(135deg, #4299E1, #3182CE)",
                        border_radius="lg",
                        padding="1em",
                        width="100%",
                        height="140px",
                        box_shadow="md",
                    ),                      # Promedio de puntuación - Verde
                    rx.box(
                        rx.vstack(
                            rx.heading(f"{AppState.promedio_calificaciones}%", size="3", color="white", font_size="2em", mb="0"),
                            rx.text("Promedio", font_size="sm", color="white", text_align="center"),
                            rx.text("Puntuación", font_size="sm", color="white", text_align="center"),
                            align_items="center",
                            justify_content="center",
                            width="100%",
                            height="100%",
                        ),
                        background="linear-gradient(135deg, #48BB78, #38A169)",
                        border_radius="lg",
                        padding="1em",
                        width="100%",
                        height="140px",
                        box_shadow="md",
                    ),
                      # Mapas creados - Amber
                    rx.box(
                        rx.vstack(
                            rx.heading(AppState.contar_mapas_creados, size="3", color="white", font_size="2em", mb="0"),
                            rx.text("Mapas", font_size="sm", color="white", text_align="center"),
                            rx.text("Creados", font_size="sm", color="white", text_align="center"),
                            align_items="center",
                            justify_content="center",
                            width="100%",
                            height="100%",
                        ),
                        background="linear-gradient(135deg, #F6AD55, #ED8936)",
                        border_radius="lg",
                        padding="1em",
                        width="100%",
                        height="140px",
                        box_shadow="md",
                    ),
                      # Resúmenes generados - Púrpura
                    rx.box(
                        rx.vstack(
                            rx.heading(AppState.contar_resumenes_generados, size="3", color="white", font_size="2em", mb="0"),
                            rx.text("Resúmenes", font_size="sm", color="white", text_align="center"),
                            rx.text("Generados", font_size="sm", color="white", text_align="center"),
                            align_items="center",
                            justify_content="center",
                            width="100%",
                            height="100%",
                        ),
                        background="linear-gradient(135deg, #9F7AEA, #805AD5)",
                        border_radius="lg",
                        padding="1em",
                        width="100%",
                        height="140px",
                        box_shadow="md",
                    ),
                    
                    width="100%",
                    spacing="4",
                    align_items="stretch",
                ),
                
                width="100%",
                spacing="4",
                padding="2em",
            ),
            variant="surface",
            width="100%",
            max_width="1000px",
            margin_top="2em",
        ),
        
        # Nueva tarjeta para el historial de evaluaciones
        rx.card(
            rx.vstack(
                rx.center(
                    rx.vstack(
                        rx.heading("📚 Historial de Evaluaciones", size="4", mb="1em", color="var(--gray-12)"),
                        rx.text(
                            "¡Mira tu progreso! Cada evaluación te hace más fuerte 💪",
                            color="var(--gray-9)",
                            mb="2em",
                            text_align="center",
                        ),
                        width="100%"
                    ),
                    width="100%",
                ),
                # Contenedor con scroll horizontal si es necesario
                rx.box(
                    rx.vstack(
                        # Encabezado de la tabla
                        rx.hstack(
                            rx.text("📅 Fecha", font_weight="bold", width="20%", text_align="center", white_space="nowrap", color="var(--gray-12)"),
                            rx.text("📖 Libro", font_weight="bold", width="25%", text_align="center", white_space="nowrap", color="var(--gray-12)"),
                            rx.text("📝 Tema", font_weight="bold", width="25%", text_align="center", white_space="nowrap", color="var(--gray-12)"),                            rx.box(
                                rx.text("📝 Nota", font_weight="bold", white_space="nowrap", color="var(--gray-12)"),
                                width="15%",
                                display="flex",
                                justify_content="center",
                                padding_right="1em",
                            ),
                            rx.box(
                                rx.text("🏅 Pts", font_weight="bold", white_space="nowrap", color="var(--gray-12)"),
                                width="10%",
                                display="flex",
                                justify_content="center",
                                padding_right="1em",
                            ),
                            rx.text("", width="5%", color="var(--gray-12)"),
                            width="100%",
                            padding="1em",
                            border_bottom="1px solid var(--gray-4)",
                        ),                        # Lista de evaluaciones (paginado)
                        rx.foreach(
                            AppState.historial_evaluaciones_paginado,
                            lambda evaluacion, i: rx.hstack(
                                rx.text(evaluacion.get("fecha", ""), width="20%", text_align="center", white_space="nowrap", color="var(--gray-12)"),
                                rx.text(evaluacion.get("libro", ""), width="25%", text_align="center", white_space="nowrap", color="var(--gray-12)"),
                                rx.text(evaluacion.get("tema", ""), width="25%", text_align="center", white_space="nowrap", color="var(--gray-12)"),                                rx.box(
                                    rx.hstack(
                                        rx.text(f"{evaluacion.get('calificacion', 0)}%", color="var(--gray-12)"),
                                        rx.icon("star", color="var(--yellow-9)"),
                                        spacing="2",
                                    ),
                                    width="15%",
                                    display="flex",
                                    justify_content="center",
                                    padding_right="1em",
                                ),
                                rx.box(
                                    rx.text(
                                        f"{evaluacion.get('respuestas_correctas', 0)}/{evaluacion.get('total_preguntas', 0)}",
                                        color="var(--green-10)",
                                    ),
                                    width="10%",
                                    display="flex",
                                    justify_content="center",
                                    padding_right="1em",
                                ),rx.box(
                                    rx.button(
                                        "Repasar",
                                        color_scheme="blue",
                                        size="2",
                                        on_click=lambda curso=evaluacion.get("curso", ""), libro=evaluacion.get("libro", ""), tema=evaluacion.get("tema", ""): AppState.repasar_evaluacion_y_ir(curso, libro, tema),
                                    ),
                                    width="5%", display="flex", justify_content="center", margin_right="1em"
                                ),                                width="100%",
                                padding="1em",
                                border_bottom="1px solid var(--gray-3)",
                                margin_bottom="0.8em",  # Aumentado espacio entre registros
                                align_items="center",
                                background=rx.cond(i % 2 == 0, "var(--gray-1)", "var(--gray-2)"),  # Alternar colores adaptados al tema
                                border_radius="md",  # Bordes redondeados
                                transition="all 0.2s ease",  # Transición suave
                                _hover={"background": "var(--accent-1)"},  # Efecto hover
                            ),
                        ),                        # Contenedor de paginación centrado
                        rx.box(
                            rx.hstack(
                                rx.button(
                                    rx.hstack(rx.icon("arrow-left", size=14), rx.text("Anterior")),
                                    on_click=AppState.pagina_anterior, 
                                    is_disabled=~AppState.tiene_pagina_anterior,
                                    variant="soft",
                                    color_scheme=PRIMARY_COLOR_SCHEME,
                                    size="2",
                                ),                                rx.text(
                                    rx.cond(
                                        AppState.total_paginas_historial > 1,
                                        f"Página {AppState.historial_evaluaciones_pagina_actual}/{AppState.total_paginas_historial}",
                                        f"Página {AppState.historial_evaluaciones_pagina_actual}"
                                    ),
                                    font_weight="medium",
                                    padding="0 1em",
                                    color="var(--gray-12)",  # Color del texto adaptado al tema
                                ),
                                rx.button(
                                    rx.hstack(rx.text("Siguiente"), rx.icon("arrow-right", size=14)),
                                    on_click=AppState.pagina_siguiente, 
                                    is_disabled=~AppState.tiene_siguiente_pagina,
                                    variant="soft",
                                    color_scheme=PRIMARY_COLOR_SCHEME,
                                    size="2",
                                ),
                                justify="center", 
                                spacing="4", 
                                mt="1.5em",
                                mb="0.5em",
                            ),
                            width="100%",
                            display="flex",
                            justify_content="center",  # Centra horizontalmente el contenido
                            padding="0.5em 0 1em 0",  # Añade padding vertical
                        ),
                        width="100%",
                        spacing="0",
                        border="1px solid var(--gray-4)",
                        border_radius="lg",
                    ),
                    width="100%",
                    overflow_x="auto",
                ),
            ),
            variant="surface",
            width="100%",
            max_width="1000px",
            margin_top="2em",
        ),
        
        # Estilo general igual que en mapas
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="5em",
    )

def ayuda_tab():
    """Contenido de la pestaña de ayuda con diseño moderno y centrado, similar a la pestaña de evaluaciones."""
    return rx.vstack(
        # Encabezado principal centrado con robot
        rx.center(
            rx.hstack(
                rx.heading(AppState.help_center_text, size="6"),
                rx.image(src="/robot_ayuda.png", width="80px", height="80px", ml="3em"),
                width="auto",
                justify="center",
                align_items="center",
                mb="2em",
            ),
        ),
        
        # Texto introductorio centrado
        rx.text(
            AppState.help_subtitle_text,
            color="gray.500",
            mb="2em",
            text_align="center",
            max_width="600px",
        ),
        
        # Tarjeta principal que contiene las preguntas frecuentes
        rx.card(
            rx.vstack(
                # Título de la sección
                rx.hstack(
                    rx.icon("lightbulb", size=16, color="var(--orange-9)"),
                    rx.heading(AppState.frequent_questions_text, size="5", mb="1em"),
                    spacing="2",
                    width="100%",
                    justify="center",
                    align_items="center",
                    padding_y="0.5em",
                ),
                
                rx.divider(),
                
                # Lista de preguntas con funcionalidad para mostrar/ocultar respuestas
                rx.foreach(
                    AppState.ayuda_preguntas_respuestas,
                    lambda pregunta, i: rx.vstack(
                        # Pregunta clickeable para mostrar/ocultar respuesta
                        rx.box(
                            rx.hstack(
                                rx.icon("question-mark", size=16, color="var(--gray-12)"),
                                rx.text(pregunta["pregunta"], font_weight="medium"),
                                rx.spacer(),
                                rx.icon(
                                    rx.cond(
                                        AppState.ayuda_pregunta_abierta == i,
                                        "chevron-down",
                                        "chevron-right"
                                    ), 
                                    size=16, 
                                    color="var(--gray-11)"
                                ),
                                width="100%",
                                align_items="center",
                            ),
                            padding="0.8em 1em",
                            border_radius="md",
                            _hover={"bg": "rgba(255, 123, 66, 0.1)", "cursor": "pointer"},
                            width="100%",
                            on_click=lambda index=i: AppState.toggle_pregunta(index),
                        ),
                        
                        # Respuesta que se muestra/oculta
                        rx.cond(
                            AppState.ayuda_pregunta_abierta == i,
                            rx.box(
                                rx.text(
                                    pregunta["respuesta"],
                                    color="var(--gray-12)",
                                ),
                                padding="0 1em 1em 2.5em",
                                border_left="2px solid var(--accent-6)",
                                margin_left="0.5em",
                                background="var(--gray-1)",
                                transition="all 0.3s ease-in-out",
                                animation="fadeIn 0.4s ease-in-out",
                            ),
                        ),
                        width="100%",
                        align_items="flex_start",
                        spacing="0",
                        margin_bottom="0.5em",
                    ),
                ),
                
                # Separador antes del formulario de contacto
                rx.divider(margin_y="1.5em"),
                
                # Sección para contacto adicional
                rx.vstack(
                    rx.heading(AppState.not_found_help_text, size="5", mb="1em", text_align="center"),
                    rx.button(
                        rx.hstack(
                            rx.icon("mail", size=16),
                            rx.text(AppState.contact_us_text),
                        ),
                        on_click=AppState.open_contact_form,
                        variant="soft",
                        color_scheme=PRIMARY_COLOR_SCHEME,
                        size="3",
                        width="auto",
                    ),
                    width="100%",
                    align_items="center",
                    spacing="3",
                ),
                
                width="100%",
                spacing="2",
                padding="2em",
            ),
            variant="surface",
            width="100%",
            max_width="800px",
        ),
        
        # Estilo general
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="5em",
    )

def libros_tab():
    """Contenido de la pestaña de libros digitales."""
    return rx.vstack(
        # Encabezado con robot sosteniendo tableta
        rx.center(
            rx.hstack(
                rx.heading("📚 " + AppState.digital_library_title, size="6"),
                rx.image(src="/robot_libros.png", width="80px", height="80px", ml="3em"),
                width="auto",
                justify="center",
                align_items="center",
                mb="2em",
            ),
        ),
        
        rx.text(
            AppState.digital_library_desc,
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
                    placeholder=AppState.select_course_placeholder,
                    value=AppState.selected_curso,
                    on_change=AppState.handle_libros_curso_change,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                ),
                rx.select(
                    AppState.libros_para_curso,
                    placeholder=AppState.select_book_placeholder,
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
                    rx.center(
                        rx.vstack(
                            rx.heading("INFORMACIÓN DEL LIBRO", size="5", mb="1em", text_align="center"),
                            rx.center(
                                rx.heading(AppState.selected_libro, size="4", mb="0.5em", text_align="center"),
                                width="100%",
                            ),
                            rx.center(
                                rx.text(
                                    f"Curso: {AppState.selected_curso}",
                                    color="gray.500",
                                    mb="0.5em",
                                    text_align="center",
                                ),
                                width="100%",
                            ),
                        ),
                        width="100%"
                    ),
                    rx.box(
                        rx.vstack(
                            rx.center(
                                rx.text(
                                    "Este libro contiene material educativo importante para tu aprendizaje.",
                                    mb="1em",
                                    text_align="center",
                                ),
                                width="100%",
                            ),                            
                            # Centrar los botones usando vstack con hstack anidados (2x2)
                            rx.vstack(
                                # Primera fila de botones
                                rx.hstack(
                                    # Botón 1: Crear Resumen
                                    rx.link(
                                        rx.button(
                                            rx.vstack(
                                                rx.icon("file-text", mb="0.3em"),
                                                rx.text("Crear", font_size="0.9em"),
                                                rx.text("Resumen", font_size="0.9em"),
                                                spacing="0",
                                                justify="center",
                                                align_items="center",
                                                width="100%",
                                            ),
                                            variant="surface",
                                            size="3",
                                            color_scheme="blue",  # Color azul para Resúmenes
                                            width="100%",
                                            height="70px",
                                        ),
                                        on_click=lambda: AppState.set_active_tab("resumen"),
                                        text_decoration="none",
                                        width="50%",
                                    ),
                                    
                                    # Botón 2: Crear Mapa
                                    rx.link(
                                        rx.button(
                                            rx.vstack(
                                                rx.icon("map", mb="0.3em"),
                                                rx.text("Crear", font_size="0.9em"),
                                                rx.text("Mapa", font_size="0.9em"),
                                                spacing="0",
                                                justify="center",
                                                align_items="center",
                                                width="100%",
                                            ),
                                            variant="surface",
                                            size="3",
                                            color_scheme=ACCENT_COLOR_SCHEME,  # Color amarillo para Mapas
                                            width="100%",
                                            height="70px",
                                        ),
                                        on_click=lambda: AppState.set_active_tab("mapa"),
                                        text_decoration="none",
                                        width="50%",
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                
                                # Segunda fila de botones
                                rx.hstack(
                                    # Botón 3: Crear Cuestionario
                                    rx.link(
                                        rx.button(
                                            rx.vstack(
                                                rx.icon("list-checks", mb="0.3em"),
                                                rx.text("Crear", font_size="0.9em"),
                                                rx.text("Cuestionario", font_size="0.9em"),
                                                spacing="0",
                                                justify="center",
                                                align_items="center",
                                                width="100%",
                                            ),
                                            variant="surface",
                                            size="3",
                                            color_scheme="cyan",  # Color azul pálido para Cuestionarios
                                            width="100%",
                                            height="70px",
                                        ),
                                        on_click=lambda: AppState.set_active_tab("cuestionario"),
                                        text_decoration="none",
                                        width="50%",
                                    ),
                                    
                                    # Botón 4: Crear Evaluación
                                    rx.link(
                                        rx.button(
                                            rx.vstack(
                                                rx.icon("clipboard-check", mb="0.3em"),
                                                rx.text("Crear", font_size="0.9em"),
                                                rx.text("Evaluación", font_size="0.9em"),
                                                spacing="0",
                                                justify="center",
                                                align_items="center",
                                                width="100%",
                                            ),
                                            variant="surface",
                                            size="3",
                                            color_scheme="purple",  # Color morado para Evaluaciones
                                            width="100%",
                                            height="70px",
                                        ),
                                        on_click=lambda: AppState.set_active_tab("evaluacion"),
                                        text_decoration="none",
                                        width="50%",
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                spacing="2",
                                width="100%",
                                align_items="center",
                                justify_content="center",
                            ),
                            width="100%",
                            align_items="flex_start",
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
    # Elementos de navegación fijos
    header = rx.hstack(
        rx.icon("graduation-cap", size=28, color_scheme=PRIMARY_COLOR_SCHEME),
        rx.heading("SMART", size="5", weight="bold"),
        rx.heading("STUDENT", size="5", weight="light", color_scheme="gray"),
        rx.spacer(),
        rx.button(
            rx.cond(AppState.current_language == "es", "ES", "EN"),
            variant="soft",
            size="2",
            on_click=AppState.toggle_language,
            aria_label=AppState.switch_language_text,
            mr="2",
        ),
        rx.color_mode.switch(size="2"),
        rx.tooltip(
            rx.button(
                rx.icon("log-out", size=16),
                on_click=AppState.logout,
                color_scheme="red",
                variant="soft",
                size="2",
            ),
            content=AppState.sign_out_text,
        ),
        p="1.5em 2em", 
        w="100%", 
        bg="var(--gray-1)", 
        border_bottom="1px solid var(--gray-4)",
        position="sticky", 
        top="0", 
        z_index="10", 
        align_items="center", 
        justify="start",
        height="64px",  # Altura fija para el encabezado
    )
    
    # Creamos un contenedor fijo solo para el encabezado
    header_container = rx.box(
        header,
        position="sticky",
        top="0",
        z_index="10",
        w="100%",
        bg="var(--gray-1)",
    )
    
    # Usando correctamente la estructura de Tabs de Radix UI, con todos los componentes anidados adecuadamente
    tabs_section = rx.tabs.root(
        # La barra de navegación con pestañas que se quedará fija bajo el encabezado
        rx.box(
            rx.tabs.list(
                rx.tabs.trigger(AppState.tab_inicio_text, value="inicio", on_click=lambda: AppState.set_active_tab("inicio"), py="0.75em"),
                rx.tabs.trigger(AppState.tab_libros_text, value="libros", on_click=lambda: AppState.set_active_tab("libros"), py="0.75em"),
                rx.tabs.trigger(AppState.tab_resumen_text, value="resumen", on_click=lambda: AppState.set_active_tab("resumen"), py="0.75em"),
                rx.tabs.trigger(AppState.tab_mapa_text, value="mapa", on_click=lambda: AppState.set_active_tab("mapa"), py="0.75em"),
                rx.tabs.trigger(AppState.tab_cuestionario_text, value="cuestionario", on_click=lambda: AppState.set_active_tab("cuestionario"), py="0.75em"),
                rx.tabs.trigger(AppState.tab_evaluacion_text, value="evaluacion", on_click=lambda: AppState.set_active_tab("evaluacion"), py="0.75em"),
                rx.tabs.trigger(AppState.tab_perfil_text, value="perfil", on_click=lambda: AppState.set_active_tab("perfil"), py="0.75em"),
                rx.tabs.trigger(AppState.tab_ayuda_text, value="ayuda", on_click=lambda: AppState.set_active_tab("ayuda"), py="0.75em"),
                size="2", 
                w="100%", 
                justify="center", 
                border_bottom="1px solid var(--gray-6)",
            ),
            position="sticky",
            top="64px",  # Ajustado para coincidir exactamente con la altura del encabezado
            z_index="9",
            bg="var(--gray-1)",
            box_shadow="0 2px 4px rgba(0, 0, 0, 0.1)",
            w="100%",
        ),
        # El contenido de las pestañas, cada uno visible según la pestaña activa
        rx.tabs.content(inicio_tab(), value="inicio"),
        rx.tabs.content(libros_tab(), value="libros"),
        rx.tabs.content(resumen_tab(), value="resumen"),
        rx.tabs.content(mapa_tab(), value="mapa"),
        rx.tabs.content(cuestionario_tab_content(), value="cuestionario"),
        rx.tabs.content(evaluacion_tab(), value="evaluacion"),
        rx.tabs.content(perfil_tab(), value="perfil"),
        rx.tabs.content(ayuda_tab(), value="ayuda"),
        # Valor de la pestaña activa y estilos generales para el componente Tabs
        value=AppState.active_tab,
        w="100%",
    )
    
    # Envolver todo en un vstack con fondo consistente
    return rx.vstack(
        header_container,
        tabs_section,
        w="100%", 
        h="100vh",
        bg="var(--gray-1)",  # Fondo consistente para todo el contenedor 
        align_items="stretch", 
        spacing="0",
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

# En Reflex 0.7.5, no se usa app.add_state(), pero tampoco app.add_page_route
# La forma correcta es asociar el estado con la página en la definición
rx.Config.static_dir = "assets"
rx.Config.title = "Smart Student | Aprende, Crea y Destaca"
rx.Config.favicon = "/favicon.ico"

def index() -> rx.Component:
    """Página principal de la aplicación."""
    return rx.fragment(
        rx.script(
            "document.title = 'Smart Student | Aprende, Crea y Destaca'"
        ),
        rx.html('<link rel="icon" type="image/x-icon" href="/smartstudent_icon.ico">'),
        rx.cond(AppState.is_logged_in, main_dashboard(), login_page()),
    )

# Agregar la página usando la sintaxis moderna de Reflex
app.add_page(index, route="/", title="Smart Student | Aprende, Crea y Destaca")