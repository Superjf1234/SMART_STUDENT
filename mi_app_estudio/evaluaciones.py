"""
Módulo para la pestaña de evaluaciones de SMART_STUDENT.

Este módulo contiene todo el código relacionado con la funcionalidad
de evaluaciones, incluyendo la interfaz de usuario y los manejadores de eventos.
"""

import reflex as rx
from typing import Dict, List, Set, Union, Any, Optional

# Constantes
PRIMARY_COLOR_SCHEME = "blue"
ACCENT_COLOR_SCHEME = "amber"
EVALUATION_TIME = 2000  # Tiempo de evaluación en segundos (33 minutos)

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

class EvaluationState(rx.State):
    """Estado específico para la funcionalidad de evaluaciones."""
    
    # Variables para evaluación
    is_eval_active: bool = False
    is_reviewing_eval: bool = False
    eval_preguntas: List[Dict[str, Any]] = []
    eval_current_idx: int = 0
    eval_user_answers: Dict[int, Union[str, Set[str]]] = {}
    eval_score: Optional[float] = None
    eval_correct_count: int = 0
    eval_total_q: int = 0
    is_generating_eval: bool = False
    error_message_ui: str = ""
    
    # Variables para el temporizador
    eval_timer_active: bool = False
    eval_timer_seconds: int = EVALUATION_TIME
    eval_timer_id: Optional[str] = None
    eval_nota: Optional[float] = None
    show_result_modal: bool = False
    
    # Contenido del resumen (necesario para generar evaluación)
    resumen_content: str = ""
    puntos_content: str = ""
    include_puntos: bool = False
    
    # Contexto del contenido
    selected_curso: str = ""
    selected_libro: str = ""
    selected_tema: str = ""
    logged_in_username: str = ""
    
    @rx.var
    def current_eval_question(self) -> Optional[Dict[str, Any]]:
        """Devuelve la pregunta actual o None si no hay preguntas válidas."""
        if self.eval_preguntas and 0 <= self.eval_current_idx < self.eval_total_q:
            q = self.eval_preguntas[self.eval_current_idx]
            return q if isinstance(q, dict) else None
        return None

    @rx.var
    def is_last_eval_question(self) -> bool:
        """Indica si estamos en la última pregunta."""
        return self.eval_total_q > 0 and self.eval_current_idx >= self.eval_total_q - 1

    @rx.var
    def is_first_eval_question(self) -> bool:
        """Indica si estamos en la primera pregunta."""
        return self.eval_current_idx <= 0
    
    @rx.var
    def eval_time_formatted(self) -> str:
        """Devuelve el tiempo restante en formato MM:SS."""
        minutes = self.eval_timer_seconds // 60
        seconds = self.eval_timer_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    @rx.var
    def eval_nota_formateada(self) -> str:
        """Convierte el puntaje (0-100) a nota escala chilena (1.0-7.0)."""
        if self.eval_nota is None:
            return "0,0"
        # Conversión de porcentaje (0-100) a nota (1.0-7.0)
        nota = 1.0 + (self.eval_nota / 100) * 6.0
        # Formatear con un decimal y coma en lugar de punto (estilo español/chileno)
        return f"{nota:.1f}".replace('.', ',')
        
    @rx.var
    def get_current_question_options(self) -> List[Dict[str, str]]:
        """Devuelve las opciones de la pregunta actual con sus textos correctos."""
        if not self.current_eval_question:
            return []
        opciones = self.current_eval_question.get("opciones", [])
        if not isinstance(opciones, list):
            return []
        # Asegurar que cada opción tenga un id y texto válidos
        return [
            {"id": opt.get("id", ""), "texto": opt.get("texto", "Opción sin texto")}
            for opt in opciones if isinstance(opt, dict)
        ]

    def start_eval_timer(self):
        """Inicia el temporizador de evaluación."""
        if self.eval_timer_active:
            return
        
        self.eval_timer_active = True
        self.eval_timer_seconds = EVALUATION_TIME
        self.update_timer()
        yield
        
    def update_timer(self):
        """Actualiza el temporizador cada segundo."""
        if not self.eval_timer_active:
            return
            
        self.eval_timer_seconds -= 1
        
        if self.eval_timer_seconds <= 0:
            self.eval_timer_active = False
            self.calculate_eval_score()
            return
            
        self.eval_timer_id = self.set_timeout(1, self.update_timer)
        
    def restart_evaluation(self):
        """Reinicia la evaluación actual o genera una nueva."""
        # Detener el temporizador si está activo
        self.eval_timer_active = False
        if self.eval_timer_id:
            self.clear_timeout(self.eval_timer_id)
            self.eval_timer_id = None
            
        # Reiniciar estados de evaluación
        self.is_reviewing_eval = False
        self.eval_current_idx = 0
        self.eval_user_answers = {}
        self.eval_score = None
        self.eval_correct_count = 0
        self.eval_nota = None
        self.show_result_modal = False
        
        # Si ya teníamos preguntas, simplemente reiniciamos la evaluación
        if self.eval_preguntas:
            self.is_eval_active = True
            self.start_eval_timer()
        else:
            # Si no hay preguntas, iniciamos el proceso de generación
            self.generate_evaluation()
        
        yield
    
    def close_result_modal(self):
        """Cierra el modal de resultados."""
        self.show_result_modal = False
        yield
    
    def set_eval_answer(self, answer_value: Union[str, List[str]]):
        """Establece la respuesta del usuario para la pregunta actual."""
        if not self.is_eval_active or self.is_reviewing_eval or not self.eval_preguntas:
            return
        idx = self.eval_current_idx
        if not (0 <= idx < len(self.eval_preguntas)):
            return
        try:
            q = self.eval_preguntas[idx]
            if not isinstance(q, dict):
                return
            q_type = q.get("tipo", "")
            if q_type == "opcion_multiple":
                if isinstance(answer_value, str):
                    self.eval_user_answers[idx] = answer_value
            elif q_type == "seleccion_multiple":
                if isinstance(answer_value, list):
                    self.eval_user_answers[idx] = set(str(v) for v in answer_value)
        except Exception as e:
            print(f"Error set_eval_answer idx {idx}: {e}")
        yield

    def update_multiple_answer(self, option_id: str, checked: bool):
        """Actualiza las respuestas de selección múltiple."""
        idx = self.eval_current_idx
        if not (0 <= idx < len(self.eval_preguntas)):
            return
        if not isinstance(self.eval_user_answers.get(idx), set):
            self.eval_user_answers[idx] = set()
        if checked:
            self.eval_user_answers[idx].add(option_id)
        else:
            self.eval_user_answers[idx].discard(option_id)
        yield

    def next_eval_question(self):
        """Avanza a la siguiente pregunta."""
        if self.eval_preguntas and self.eval_current_idx < self.eval_total_q - 1:
            self.eval_current_idx += 1
            yield

    def prev_eval_question(self):
        """Retrocede a la pregunta anterior."""
        if self.eval_current_idx > 0:
            self.eval_current_idx -= 1
            yield

    def calculate_eval_score(self):
        """Calcula la puntuación de la evaluación actual."""
        if not self.eval_preguntas:
            self.error_message_ui = "No hay preguntas para evaluar."
            yield
            return
        try:
            # Detener el temporizador si está activo
            self.eval_timer_active = False
            if self.eval_timer_id:
                self.clear_timeout(self.eval_timer_id)
                self.eval_timer_id = None
                
            correct = 0
            total = self.eval_total_q
            if total == 0:
                self.error_message_ui = "No hay preguntas válidas para evaluar."
                yield
                return
                
            for i, q_dict in enumerate(self.eval_preguntas):
                if not isinstance(q_dict, dict):
                    continue
                u_ans = self.eval_user_answers.get(i)
                c_ans = q_dict.get("respuesta_correcta")
                q_type = q_dict.get("tipo")
                correct_inc = 0
                
                if q_type == "opcion_multiple" and isinstance(u_ans, str) and u_ans == c_ans:
                    correct_inc = 1
                elif q_type == "seleccion_multiple":
                    c_set = set(c_ans) if isinstance(c_ans, list) else set()
                    u_set = u_ans if isinstance(u_ans, set) else set()
                    if u_set and c_set and u_set == c_set:
                        correct_inc = 1
                        
                correct += correct_inc
                
            self.eval_correct_count = correct
            self.eval_score = (correct / total) * 100.0
            self.eval_nota = self.eval_score  # Para el cálculo de la nota
            self.is_reviewing_eval = True
            self.is_eval_active = False
            self.eval_current_idx = 0
            self.show_result_modal = True  # Mostrar el modal con la nota
            
            # Guardar resultado en la base de datos (si está disponible)
            self._guardar_resultado_en_bd()
        except Exception as calc_e:
            print(f"Error cálculo score: {calc_e}")
            self.error_message_ui = "Error al calcular el puntaje. Inténtalo nuevamente."
            self.is_reviewing_eval = False
            self.is_eval_active = True
        yield
    
    def _guardar_resultado_en_bd(self):
        """Método interno para guardar el resultado en la base de datos."""
        from mi_app_estudio.mi_app_estudio import BACKEND_AVAILABLE
        if (
            self.logged_in_username and 
            BACKEND_AVAILABLE and 
            hasattr(__import__("backend.db_logic", fromlist=["db_logic"]), "guardar_evaluacion")
        ):
            try:
                db_logic = __import__("backend.db_logic", fromlist=["db_logic"])
                db_logic.guardar_evaluacion(
                    self.logged_in_username,
                    self.selected_curso or "N/A",
                    self.selected_libro or "N/A",
                    self.selected_tema or "N/A",
                    self.eval_nota if self.eval_nota is not None else 0.0,
                )
            except Exception as db_e:
                print(f"Error guardando resultado en BD: {db_e}")

    async def generate_evaluation(self):
        """Genera una evaluación basada en el resumen."""
        if not self.resumen_content:
            self.error_message_ui = "Debes generar un resumen primero para poder evaluarte."
            yield
            return
            
        # Verificar disponibilidad del backend
        from mi_app_estudio.mi_app_estudio import BACKEND_AVAILABLE
        if not BACKEND_AVAILABLE:
            self.error_message_ui = "El servicio de evaluación no está disponible en este momento."
            yield
            return

        self.is_generating_eval = True
        self.error_message_ui = ""
        self.is_eval_active = False
        self.is_reviewing_eval = False
        self.eval_preguntas = []
        self.eval_current_idx = 0
        self.eval_correct_count = 0
        self.eval_total_q = 0
        self.eval_user_answers = {}
        self.eval_score = None
        self.eval_nota = None
        self.show_result_modal = False
        self.eval_timer_active = False
        
        if self.eval_timer_id:
            self.clear_timeout(self.eval_timer_id)
            self.eval_timer_id = None
            
        yield
        
        try:
            eval_logic = __import__("backend.eval_logic", fromlist=["eval_logic"])
            if not hasattr(eval_logic, "generar_evaluacion_funcional"):
                raise AttributeError("El módulo de evaluación no está correctamente configurado.")
                
            result = eval_logic.generar_evaluacion_funcional(
                self.selected_curso,
                self.selected_libro,
                self.selected_tema,
                "opcion_multiple"  # Tipo de evaluación por defecto
            )
            
            if isinstance(result, dict) and result.get("status") == "EXITO":
                preguntas = result.get("preguntas")
                if isinstance(preguntas, list) and preguntas:
                    # Limitar a 15 preguntas como máximo
                    self.eval_preguntas = [
                        p for p in preguntas[:15] if isinstance(p, dict) and "pregunta" in p
                    ]
                    if not self.eval_preguntas:
                        self.error_message_ui = "No se pudieron generar preguntas válidas."
                        self.is_eval_active = False
                    else:
                        self.eval_total_q = len(self.eval_preguntas)
                        self.is_eval_active = True
                        # Iniciar el temporizador
                        self.start_eval_timer()
                else:
                    self.error_message_ui = "No se pudieron generar preguntas para esta evaluación."
                    self.is_eval_active = False
            else:
                self.error_message_ui = (
                    result.get("message", "Ocurrió un error al generar la evaluación.")
                    if isinstance(result, dict)
                    else "Error en la respuesta del servidor."
                )
        except AttributeError as ae:
            self.error_message_ui = "El sistema de evaluación no está disponible en este momento."
            print(f"ERROR: {ae}")
        except Exception as e:
            import traceback
            self.error_message_ui = "Ocurrió un error inesperado al generar la evaluación."
            print(f"ERROR G-EVAL: {traceback.format_exc()}")
        finally:
            self.is_generating_eval = False
            yield

def evaluacion_tab():
    """Renderiza la pestaña de evaluaciones completa."""
    return rx.vstack(
        rx.cond(
            EvaluationState.is_eval_active | EvaluationState.is_reviewing_eval,
            # --- Vista Evaluación / Revisión ---
            rx.vstack(
                # Encabezado con información sobre la evaluación
                rx.hstack(
                    rx.heading(
                        rx.cond(
                            EvaluationState.is_reviewing_eval,
                            "Revisión de Evaluación",
                            "Evaluación en Curso"
                        ),
                        size="5",
                    ),
                    rx.spacer(),
                    # Timer solo visible durante la prueba activa
                    rx.cond(
                        EvaluationState.is_eval_active,
                        rx.hstack(
                            rx.icon("timer", color="orange.500"),
                            rx.text(
                                EvaluationState.eval_time_formatted,
                                font_size="lg",
                                font_weight="bold",
                                color=rx.cond(
                                    EvaluationState.eval_timer_seconds < 300,
                                    "red.500",
                                    "blue.500"
                                ),
                            ),
                            spacing="2",
                        ),
                    ),
                    # Contador de preguntas
                    rx.text(
                        f"Pregunta {EvaluationState.eval_current_idx + 1} de {EvaluationState.eval_total_q}",
                        font_size="md",
                        color="gray.500",
                    ),
                    w="100%",
                    pb="2",
                    border_bottom="1px solid var(--gray-5)",
                    mb="4",
                ),
                
                # Pregunta actual
                rx.cond(
                    EvaluationState.current_eval_question != None,
                    rx.vstack(
                        # Texto de la pregunta
                        rx.box(
                            rx.markdown(
                                EvaluationState.current_eval_question.get("pregunta", ""),
                                color_scheme="gray",
                                font_size="lg",
                                font_weight="medium",
                                styles={"p": {"marginBottom": "1em"}},
                            ),
                            w="100%", 
                            mb="4",
                        ),
                        
                        # Opciones (diferentes según el tipo de pregunta)
                        rx.cond(
                            EvaluationState.current_eval_question.get("tipo") == "opcion_multiple",
                            # Opciones para selección única - Usando rx.radio_group con conversión de valor
                            rx.radio_group(
                                rx.foreach(
                                    EvaluationState.get_current_question_options,
                                    lambda opcion, i: rx.radio(
                                        opcion.get("texto", f"Opción {opcion.get('id', '')}"),
                                        value=opcion.get("id", ""),
                                        disabled=EvaluationState.is_reviewing_eval,
                                        color_scheme=rx.cond(
                                            EvaluationState.is_reviewing_eval,
                                            rx.cond(
                                                EvaluationState.current_eval_question.get("respuesta_correcta") == opcion.get("id", ""),
                                                "green",
                                                rx.cond(
                                                    EvaluationState.eval_user_answers.get(EvaluationState.eval_current_idx) == opcion.get("id", ""),
                                                    "red",
                                                    "gray"
                                                )
                                            ),
                                            PRIMARY_COLOR_SCHEME
                                        ),
                                        size="2",
                                    )
                                ),
                                # Convertir el valor a lista y ajustar el callback on_change
                                value=rx.var(lambda: [EvaluationState.eval_user_answers.get(EvaluationState.eval_current_idx, "")]),
                                on_change=lambda new_value: EvaluationState.set_eval_answer(new_value[0] if new_value else ""),
                                spacing="3",
                                w="100%",
                                align_items="start",
                            ),
                            # Opciones para selección múltiple - Usando rx.foreach
                            rx.vstack(
                                rx.foreach(
                                    EvaluationState.get_current_question_options,
                                    lambda opcion, i: rx.checkbox(
                                        opcion.get("texto", f"Opción {opcion.get('id', '')}"),
                                        value=opcion.get("id", ""),
                                        checked=rx.cond(
                                            isinstance(EvaluationState.eval_user_answers.get(EvaluationState.eval_current_idx), set),
                                            EvaluationState.eval_user_answers.get(EvaluationState.eval_current_idx, set()).contains(opcion.get("id", "")),
                                            False
                                        ),
                                        on_change=lambda checked, id=opcion.get("id", ""): EvaluationState.update_multiple_answer(id, checked),
                                        disabled=EvaluationState.is_reviewing_eval,
                                        color_scheme=rx.cond(
                                            EvaluationState.is_reviewing_eval,
                                            rx.cond(
                                                EvaluationState.current_eval_question.get("respuesta_correcta", []).contains(opcion.get("id", "")),
                                                "green",
                                                rx.cond(
                                                    EvaluationState.eval_user_answers.get(EvaluationState.eval_current_idx, set()).contains(opcion.get("id", "")),
                                                    "red",
                                                    "gray"
                                                )
                                            ),
                                            PRIMARY_COLOR_SCHEME
                                        ),
                                        size="2",
                                    )
                                ),
                                spacing="3",
                                w="100%",
                                align_items="start",
                            ),
                        ),
                        
                        # Explicación (solo visible en modo revisión)
                        rx.cond(
                            EvaluationState.is_reviewing_eval,
                            rx.box(
                                rx.card(
                                    rx.vstack(
                                        rx.heading("Explicación", size="3", mb="2"),
                                        rx.markdown(
                                            EvaluationState.current_eval_question.get("explicacion", "Sin explicación disponible"),
                                            color_scheme="gray",
                                        ),
                                        align_items="start",
                                        spacing="2",
                                    ),
                                    p="4",
                                    variant="outline",
                                    w="100%",
                                    color_scheme="blue",
                                    mt="4",
                                ),
                                w="100%",
                            ),
                        ),
                        w="100%",
                        spacing="4",
                        align_items="start",
                    ),
                ),
                
                # Botones de navegación
                rx.hstack(
                    # Botón anterior
                    rx.button(
                        "Anterior",
                        on_click=EvaluationState.prev_eval_question,
                        variant="soft",
                        is_disabled=EvaluationState.is_first_eval_question,
                        size="2",
                    ),
                    rx.spacer(),
                    
                    # Botón para terminar/reiniciar
                    rx.cond(
                        EvaluationState.is_reviewing_eval,
                        rx.button(
                            "Reiniciar Evaluación",
                            on_click=EvaluationState.restart_evaluation,
                            color_scheme="purple",
                            size="2",
                        ),
                        rx.button(
                            "Terminar y Calificar",
                            on_click=EvaluationState.calculate_eval_score,
                            color_scheme="green",
                            size="2",
                        ),
                    ),
                    
                    rx.spacer(),
                    # Botón siguiente
                    rx.button(
                        "Siguiente",
                        on_click=EvaluationState.next_eval_question,
                        variant="soft",
                        is_disabled=EvaluationState.is_last_eval_question,
                        size="2",
                    ),
                    w="100%",
                    mt="8",
                ),
                w="100%",
                p="6",
                border="1px solid var(--gray-5)",
                border_radius="large",
                bg="var(--gray-1)",
                spacing="4",
            ),
            
            # --- Vista si NO hay Evaluación ---
            rx.vstack(
                rx.icon("clipboard-check", size="5xl", color="gray.400", mb="4"),
                rx.heading("Prepárate para una Evaluación", size="5", mb="4"),
                rx.text(
                    "Primero debes crear un resumen para generar una evaluación basada en él.",
                    text_align="center",
                    color="gray.500",
                    mb="6",
                    max_width="400px",
                ),
                rx.button(
                    "Ir a Crear Resumen",
                    on_click=lambda: None,  # Se conectará desde el archivo principal
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                ),
                align_items="center",
                justify="center",
                min_h="60vh",
                w="100%",
                p="2em",
                border="1px dashed var(--gray-5)",
                border_radius="large",
                bg="var(--gray-1)",
            ),
        ),
        error_callout(EvaluationState.error_message_ui),
        
        # Modal para mostrar la nota final
        rx.modal(
            rx.modal_overlay(
                rx.modal_content(
                    rx.modal_header("Resultado de la Evaluación"),
                    rx.modal_body(
                        rx.vstack(
                            rx.heading(
                                f"Tu nota es: {EvaluationState.eval_nota_formateada}",
                                size="7",
                                color=rx.cond(
                                    (EvaluationState.eval_nota or 0) >= 60,
                                    "green.500",
                                    "red.500"
                                ),
                                text_align="center",
                                mb="4",
                            ),
                            rx.stat(
                                rx.stat_label("Respuestas Correctas"),
                                rx.stat_number(f"{EvaluationState.eval_correct_count} de {EvaluationState.eval_total_q}"),
                                rx.stat_help_text(
                                    f"{int((EvaluationState.eval_correct_count / (EvaluationState.eval_total_q or 1)) * 100)}% de acierto"
                                ),
                                color_scheme=rx.cond(
                                    (EvaluationState.eval_nota or 0) >= 60,
                                    "green",
                                    "red"
                                ),
                            ),
                            rx.text(
                                "Ahora puedes revisar las preguntas para ver las respuestas correctas y explicaciones.",
                                text_align="center",
                                mt="4",
                            ),
                            w="100%",
                            align_items="center",
                            p="4",
                        )
                    ),
                    rx.modal_footer(
                        rx.button(
                            "Revisar Preguntas",
                            on_click=EvaluationState.close_result_modal,
                            color_scheme=PRIMARY_COLOR_SCHEME,
                        ),
                    ),
                ),
            ),
            is_open=EvaluationState.show_result_modal,
        ),
        
        w="100%",
        max_width="800px",
        margin="0 auto",
        p="2em",
        spacing="4",
    )
