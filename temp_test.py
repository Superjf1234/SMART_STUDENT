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
            rx.progress(value=rx.cond(EvaluationState.eval_progress is not None, EvaluationState.eval_progress, 0), width="100%", size="2", color_scheme=PRIMARY_COLOR_SCHEME, mb="1.5em"),

            # --- Contenido Condicional ---
            # Verifica si el índice actual es válido para la lista de preguntas Y la lista no está vacía
            rx.cond(
                (EvaluationState.eval_current_idx >= 0) & (len(EvaluationState.eval_preguntas) > EvaluationState.eval_current_idx),

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
                                on_change=EvaluationState.set_eval_answer,
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
                                    on_change=EvaluationState.set_eval_answer_by_text,
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
                                                # Solo marcar como checked si el ID específicamente está en el conjunto de respuestas                                                is_checked=EvaluationState.check_if_option_selected(
                                                    EvaluationState.eval_current_idx, 
                                                    opcion["id"]
                                                ),
                                                on_change=lambda option_id: EvaluationState.toggle_multiple_answer(opcion["id"]),
                                                size="2",
                                                is_disabled=EvaluationState.is_reviewing_eval,
                                            ),
                                            rx.text(opcion["texto"]),
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
                            on_click=lambda: EvaluationState.prev_eval_question(),
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
                            on_click=lambda: EvaluationState.restart_evaluation,  # Volver al inicio
                            color_scheme="blue"                        ),
                        rx.button(
                            AppState.next_button_text,
                            on_click=lambda: EvaluationState.next_eval_question()
                        )
                    ),                    # En modo normal
                    rx.cond(
                        EvaluationState.is_last_eval_question,
                        rx.button(
                            AppState.finish_evaluation_button_text,
                            on_click=lambda: EvaluationState.calculate_eval_score(),
                            color_scheme="green"
                        ),                        rx.button(
                            AppState.next_button_text,
                            on_click=lambda: EvaluationState.next_eval_question()
                        )
                    )
                ),
                margin_top="2em",
                width="100%"
            ),
            # Mensaje de error
            error_callout(rx.Var.create(EvaluationState.eval_error_message)),

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
                                    ),                                    # Título personalizado basado en la puntuación
                                    rx.heading(
                                        EvaluationState.eval_titulo_resultado,
                                        size="4",
                                        text_align="center",
                                        color=rx.cond(
                                                (EvaluationState.eval_score != None) & (EvaluationState.eval_score < 40), "var(--orange-9)",
                                                rx.cond(
                                                    (EvaluationState.eval_score != None) & (EvaluationState.eval_score < 60), "var(--amber-9)",
                                                    rx.cond(
                                                        (EvaluationState.eval_score != None) & (EvaluationState.eval_score < 80), "var(--green-9)",
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
                                            size="1",                                            color=rx.cond(
                                                (EvaluationState.eval_score != None) & (EvaluationState.eval_score < 40), "var(--red-9)",
                                                rx.cond(
                                                    (EvaluationState.eval_score != None) & (EvaluationState.eval_score < 60), "var(--orange-9)",
                                                    rx.cond(
                                                        (EvaluationState.eval_score != None) & (EvaluationState.eval_score < 80), "var(--amber-9)",
                                                        rx.cond(
                                                            (EvaluationState.eval_score != None) & (EvaluationState.eval_score < 90), "var(--green-9)",
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
                                        on_click=lambda: EvaluationState.restart_evaluation(),
                                        color="white",
                                        background_color="var(--amber-9)",
                                        size="3",
                                        width="33%",
                                        height="64px",  # Doble altura normal
                                    ),
                                    rx.button(
                                        AppState.review_button_text,
                                        on_click=lambda: EvaluationState.review_evaluation(),
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
                open=EvaluationState.show_result_modal,            ),
            # --- Fin Modal de Resultados ---

            spacing="4",
            width="100%",
            max_width="700px",
            align_items="center"
        ),
        ),
        padding="2em",
        width="100%",
        max_width="800px"
    )
