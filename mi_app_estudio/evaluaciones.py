"""
Módulo para la pestaña de evaluaciones de SMART_STUDENT.

Este módulo contiene la funcionalidad completa de evaluaciones, incluyendo
la interfaz de usuario, el temporizador, y la lógica de generación/revisión.
"""

import reflex as rx
from typing import Dict, List, Set, Union, Any, Optional
# Asegúrate que las importaciones sean correctas según tu estructura
from .state import AppState, BACKEND_AVAILABLE, config_logic, eval_logic, db_logic, error_callout, PRIMARY_COLOR_SCHEME, ACCENT_COLOR_SCHEME
import asyncio # Necesario para el timer async/await
import traceback # Para imprimir errores detallados
import random  # Para mezclar las preguntas

# --- Constantes (ASEGÚRATE QUE ESTÉN AQUÍ) ---
MAX_QUESTIONS = 15
EVALUATION_TIME = 120  # Tiempo en segundos (2 minutos = 120 segundos)
MIN_RESUMEN_LENGTH = 50
# ---------------------------------------------

class EvaluationState(AppState):
    """Estado específico para la funcionalidad de evaluaciones, hereda de AppState."""

    is_eval_active: bool = False
    is_reviewing_eval: bool = False
    eval_preguntas: List[Dict[str, Any]] = []
    eval_current_idx: int = 0
    eval_user_answers: Dict[int, Union[str, Set[str]]] = {}
    eval_score: Optional[float] = None
    eval_correct_count: int = 0
    eval_total_q: int = 0
    is_generation_in_progress: bool = False
    eval_error_message: str = ""
    eval_timer_active: bool = False
    eval_timer_paused: bool = False
    # Usa la constante definida arriba
    eval_timer_seconds: int = EVALUATION_TIME
    # Tipo corregido a Optional[str]
    eval_timer_id: Optional[str] = None
    eval_nota: Optional[float] = None
    show_result_modal: bool = False
    
    # Para mostrar explicaciones en revisión
    show_explanation: bool = False
    
    # Para mostrar la confirmación antes de continuar
    show_confirmation: bool = False
    # Almacena temporalmente el índice de la siguiente pregunta
    next_question_idx: Optional[int] = None

    # --- Computed Vars ---
    @rx.var
    def current_eval_question(self) -> Optional[Dict[str, Any]]:
        """Devuelve el diccionario de la pregunta actual."""
        if self.eval_preguntas and 0 <= self.eval_current_idx < len(self.eval_preguntas):
            q = self.eval_preguntas[self.eval_current_idx]
            return q if isinstance(q, dict) else None
        return None

    @rx.var
    def is_last_eval_question(self) -> bool:
        """Verifica si es la última pregunta."""
        return len(self.eval_preguntas) > 0 and self.eval_current_idx >= len(self.eval_preguntas) - 1

    @rx.var
    def is_first_eval_question(self) -> bool:
        """Verifica si es la primera pregunta."""
        return self.eval_current_idx <= 0

    @rx.var
    def eval_time_formatted(self) -> str:
        """Formatea el tiempo restante."""
        minutes = self.eval_timer_seconds // 60
        seconds = self.eval_timer_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    @rx.var
    def eval_time_color(self) -> str:
        """Devuelve el color para el temporizador."""
        if self.eval_timer_seconds <= 30:
            return "red.500"
        return "gray.800"

    @rx.var
    def eval_nota_formateada(self) -> str:
        """Calcula y formatea la nota en escala 1.0 a 7.0."""
        if self.eval_nota is None or self.eval_nota < 0:
            return "1,0"
        nota = 1.0 + (max(0.0, min(100.0, self.eval_nota)) / 100.0) * 6.0
        return f"{nota:.1f}".replace('.', ',')

    @rx.var
    def eval_progress(self) -> int:
        """Calcula el progreso como entero 0-100."""
        total = len(self.eval_preguntas)
        if total == 0:
            return 0
        return int(min(100, max(0, ((self.eval_current_idx + 1) / total) * 100)))

    @rx.var
    def get_current_question_options(self) -> List[Dict[str, str]]:
        """Obtiene las opciones de la pregunta actual formateadas."""
        current_q = self.current_eval_question
        if not current_q:
            return []
        opciones = current_q.get("opciones", [])
        if not isinstance(opciones, list):
            print(f"WARN: Opciones no es una lista para pregunta {self.eval_current_idx}: {opciones}")
            return []

        formatted_options = []
        for i, opt in enumerate(opciones):
             if isinstance(opt, dict):
                opt_id = opt.get("id", f"opt_{i}")
                opt_text = opt.get("texto", f"Opción {opt_id}")
                formatted_options.append({"id": str(opt_id), "texto": str(opt_text)})
             else:
                print(f"WARN: Opción inválida encontrada en pregunta {self.eval_current_idx}: {opt}")
                formatted_options.append({"id": f"opt_{i}", "texto": str(opt)})
        return formatted_options

    @rx.var
    def eval_mensaje_resultado(self) -> str:
        """Devuelve un mensaje motivacional según la nota obtenida."""
        if self.eval_nota is None:
            return ""
        
        nota_float = float(self.eval_nota)
        if 0.0 <= nota_float <= 39.9:
            return "¡Ánimo! Sigue practicando para mejorar tu resultado."
        elif 40.0 <= nota_float <= 59.9:
            return "¡Buen esfuerzo! Sigue así para alcanzar un mejor resultado."
        elif 60.0 <= nota_float <= 89.9:
            return "¡Muy bien! Estás muy cerca de la excelencia."
        else:
            return "¡Excelente! Has alcanzado un resultado sobresaliente."

    # --- Option Status Methods ---
    def get_option_status(self, option_id: str) -> Dict[str, Any]:
        """Determina el estado visual de cada opción durante la revisión."""
        if not self.is_reviewing_eval:
            return {"color": "gray.800", "suffix": ""}
            
        current_q = self.current_eval_question
        if not current_q:
            return {"color": "gray.800", "suffix": ""}
            
        # Obtener respuesta del usuario y respuesta correcta
        user_answer = self.eval_user_answers.get(self.eval_current_idx, "")
        correct_answer = current_q.get("respuesta_correcta", "")
        q_type = current_q.get("tipo", "opcion_multiple")
        
        if q_type in ["opcion_multiple", "verdadero_falso"]:
            # Para preguntas de opción única
            if option_id == user_answer and option_id == correct_answer:
                return {"color": "green.500", "suffix": " (Tu selección - Correcta)"}
            elif option_id == user_answer:
                return {"color": "red.500", "suffix": " (Tu selección - Incorrecta)"}
            elif option_id == correct_answer:
                return {"color": "green.500", "suffix": " (Correcta)"}
            else:
                return {"color": "gray.800", "suffix": ""}
        else:
            # Para preguntas de selección múltiple
            user_selected = isinstance(user_answer, set) and option_id in user_answer
            is_correct = isinstance(correct_answer, list) and option_id in correct_answer
            
            if user_selected and is_correct:
                return {"color": "green.500", "suffix": " (Tu selección - Correcta)"}
            elif user_selected and not is_correct:
                return {"color": "red.500", "suffix": " (Tu selección - Incorrecta)"}
            elif not user_selected and is_correct:
                return {"color": "green.500", "suffix": " (Correcta)"}
            else:
                return {"color": "gray.800", "suffix": ""}

    # --- Timer Methods ---
    async def _stop_timer_async(self):
        """Helper interno para detener el intervalo (si existe)."""
        self.eval_timer_id = None # Borrar el ID es suficiente señal
        self.eval_timer_active = False
        self.eval_timer_paused = False

    async def start_eval_timer(self):
        """Inicia el temporizador de la evaluación."""
        print("DEBUG: Iniciando timer...")
        await self._stop_timer_async() # Asegura que no haya timers previos
        self.eval_timer_seconds = EVALUATION_TIME
        self.eval_timer_active = True
        self.eval_timer_paused = False
        return EvaluationState.update_timer # Devuelve el método a ejecutar

    async def pause_resume_timer(self):
        """Pausa o reanuda el temporizador."""
        if not self.eval_timer_active:
            return
        self.eval_timer_paused = not self.eval_timer_paused
        print(f"DEBUG: Timer pausado: {self.eval_timer_paused}")
        if not self.eval_timer_paused:
            return EvaluationState.update_timer
        else:
            return None

    async def update_timer(self):
        """Actualiza el contador del temporizador cada segundo."""
        if not self.eval_timer_active or self.eval_timer_paused:
            return None

        if self.eval_timer_seconds > 0:
            # --- AÑADIR ESTA LÍNEA ---
            await asyncio.sleep(1) # Forza una pausa de 1 segundo
            # -------------------------
            self.eval_timer_seconds -= 1
            # Llama recursivamente para el siguiente segundo
            return EvaluationState.update_timer
        else:
            # Tiempo agotado
            print("DEBUG: ¡Tiempo agotado!")
            self.eval_timer_seconds = 0
            self.calculate_eval_score_sync() # Calcula el score automáticamente
            await self._stop_timer_async()   # Detiene el timer
            return None

    # --- Evaluation Flow Methods ---
    async def restart_evaluation(self):
        """Reinicia la evaluación, generando nuevas preguntas si es necesario."""
        print("DEBUG: Reiniciando evaluación...")
        await self._stop_timer_async()
        self.is_reviewing_eval = False
        self.eval_current_idx = 0
        self.eval_user_answers = {}
        self.eval_score = None
        self.eval_correct_count = 0
        self.eval_nota = None
        self.show_result_modal = False
        self.eval_error_message = ""
        self.show_explanation = False

        # Verificar que curso, libro y tema estén seleccionados
        if not self.selected_curso or not self.selected_libro or not self.selected_tema:
            self.eval_error_message = "Por favor, selecciona Curso, Libro y Tema antes de generar la evaluación."
            print(f"WARN: No se puede generar evaluación, faltan selecciones: C={self.selected_curso}, L={self.selected_libro}, T={self.selected_tema}")
            return None

        if not self.eval_preguntas:
            print("DEBUG: No hay preguntas, generando nuevas...")
            return EvaluationState.generate_evaluation
        else:
            print("DEBUG: Usando preguntas existentes, iniciando timer...")
            self.is_eval_active = True
            self.eval_total_q = len(self.eval_preguntas)
            return EvaluationState.start_eval_timer

    def close_result_modal(self):
        """Cierra el modal de resultados."""
        self.show_result_modal = False

    def set_show_result_modal(self, is_open: bool):
        """Actualiza el estado de visibilidad del modal."""
        self.show_result_modal = is_open

    def toggle_explanation(self):
        """Muestra u oculta la explicación durante la revisión."""
        if self.is_reviewing_eval:
            self.show_explanation = not self.show_explanation

    def set_eval_answer(self, answer_value: Union[str, List[str]]):
        """Establece la respuesta para la pregunta actual (opción múltiple)."""
        if not self.is_eval_active or self.is_reviewing_eval:
            return
        idx = self.eval_current_idx
        current_q = self.current_eval_question
        if not current_q or not (0 <= idx < len(self.eval_preguntas)):
            return
        q_type = current_q.get("tipo")
        if q_type in ["opcion_multiple", "verdadero_falso"] and isinstance(answer_value, str):
            self.eval_user_answers[idx] = answer_value

    def update_multiple_answer(self, option_id: str, checked: bool):
        """Actualiza la respuesta para preguntas de selección múltiple (checkbox)."""
        if not self.is_eval_active or self.is_reviewing_eval:
            return
        idx = self.eval_current_idx
        current_q = self.current_eval_question
        if not current_q or not (0 <= idx < len(self.eval_preguntas)):
            return
        q_type = current_q.get("tipo")
        if q_type == "seleccion_multiple":
            if not isinstance(self.eval_user_answers.get(idx), set):
                self.eval_user_answers[idx] = set()
            current_set = self.eval_user_answers[idx]
            if checked:
                current_set.add(str(option_id))
            else:
                current_set.discard(str(option_id))

    def next_eval_question(self):
        """Avanza a la siguiente pregunta."""
        # Si estamos en modo revisión, siempre permitir avanzar
        if self.is_reviewing_eval:
            if self.eval_preguntas and self.eval_current_idx < len(self.eval_preguntas) - 1:
                self.eval_current_idx += 1
                self.show_explanation = False  # Ocultar explicación al cambiar de pregunta
            return

        # Verificar respuesta en modo evaluación
        current_q = self.current_eval_question
        if not current_q:
            return
            
        idx = self.eval_current_idx
        q_type = current_q.get("tipo", "opcion_multiple")
        
        # Validar que haya seleccionado una respuesta
        if q_type == "seleccion_multiple":
            seleccion = self.eval_user_answers.get(idx, set())
            if not seleccion:
                self.eval_error_message = "Por favor, selecciona al menos una opción antes de continuar."
                return
        else:
            if not self.eval_user_answers.get(idx):
                self.eval_error_message = "Por favor, selecciona una respuesta antes de continuar."
                return
                
        # Limpiar mensaje de error
        self.eval_error_message = ""
        
        # Verificar si hay más preguntas
        if self.eval_preguntas and self.eval_current_idx < len(self.eval_preguntas) - 1:
            # Guardamos el índice de la siguiente pregunta
            self.next_question_idx = self.eval_current_idx + 1
            # Mostrar confirmación
            self.show_confirmation = True
        else:
            # Si es la última pregunta, no hay necesidad de confirmar
            self.eval_current_idx += 1

    def prev_eval_question(self):
        """Retrocede a la pregunta anterior."""
        if self.eval_current_idx > 0:
            self.eval_current_idx -= 1
            # En modo revisión, ocultar explicación al cambiar de pregunta
            if self.is_reviewing_eval:
                self.show_explanation = False

    def confirm_and_continue(self):
        """Confirma y avanza a la siguiente pregunta después de la confirmación."""
        if self.next_question_idx is not None and self.show_confirmation:
            # Avanzar a la siguiente pregunta
            self.eval_current_idx = self.next_question_idx
            # Limpiar el estado
            self.next_question_idx = None
            self.show_confirmation = False

    def cancel_continue(self):
        """Cancela la acción de avanzar y mantiene la pregunta actual."""
        # Limpiar el estado sin cambiar la pregunta actual
        self.next_question_idx = None
        self.show_confirmation = False

    def calculate_eval_score_sync(self):
        """Calcula el puntaje final de la evaluación (versión síncrona)."""
        print("DEBUG: Calculando score...")
        if not self.eval_preguntas:
            self.eval_error_message = "No hay preguntas para evaluar."
            print(f"ERROR: {self.eval_error_message}")
            return

        total = len(self.eval_preguntas)
        if total == 0:
            self.eval_error_message = "No hay preguntas válidas para evaluar."
            print(f"ERROR: {self.eval_error_message}")
            return

        # Validar que la última pregunta tenga respuesta
        if not self.is_reviewing_eval:  # Solo validar si no estamos en modo revisión
            idx = self.eval_current_idx
            current_q = self.current_eval_question
            if current_q:
                q_type = current_q.get("tipo", "opcion_multiple")
                if q_type == "seleccion_multiple":
                    seleccion = self.eval_user_answers.get(idx, set())
                    if not seleccion:
                        self.eval_error_message = "Por favor, selecciona al menos una opción para la última pregunta."
                        return
                else:
                    if not self.eval_user_answers.get(idx):
                        self.eval_error_message = "Por favor, selecciona una respuesta para la última pregunta."
                        return

        correct = 0
        try:
            for i, q_dict in enumerate(self.eval_preguntas):
                if not isinstance(q_dict, dict):
                    print(f"WARN: Pregunta {i} no es un diccionario, saltando.")
                    continue

                u_ans = self.eval_user_answers.get(i)
                c_ans = q_dict.get("respuesta_correcta")
                q_type = q_dict.get("tipo")
                correct_inc = 0

                if q_type in ["opcion_multiple", "verdadero_falso"]:
                    if isinstance(u_ans, str) and u_ans == str(c_ans):
                        correct_inc = 1
                elif q_type == "seleccion_multiple":
                    c_set = set(map(str, c_ans)) if isinstance(c_ans, list) else set()
                    u_set = u_ans if isinstance(u_ans, set) else set()
                    if u_set and c_set and u_set == c_set:
                        correct_inc = 1
                correct += correct_inc

            self.eval_correct_count = correct
            self.eval_score = (correct / total) * 100.0 if total > 0 else 0.0
            self.eval_nota = self.eval_score
            print(f"DEBUG: Score calculado: {self.eval_score}, Nota base: {self.eval_nota}")

            self.is_reviewing_eval = True
            self.is_eval_active = False
            self.eval_current_idx = 0
            self.show_result_modal = True
            self.eval_error_message = ""
            self._guardar_resultado_en_bd()

        except Exception as calc_e:
            print(f"ERROR cálculo score: {calc_e}\n{traceback.format_exc()}")
            self.eval_error_message = "Error al calcular el puntaje. Inténtalo nuevamente."
            self.is_reviewing_eval = False
            self.is_eval_active = False

    async def calculate_eval_score(self):
        """Función async wrapper para calcular el score y detener el timer."""
        print("DEBUG: calculate_eval_score (async wrapper) llamado.")
        await self._stop_timer_async()
        self.calculate_eval_score_sync()

    def _guardar_resultado_en_bd(self):
        """Guarda el resultado de la evaluación en la base de datos (síncrono)."""
        if not self.logged_in_username:
            print("WARN: Usuario no logueado, no se guarda resultado.")
            return
        if not BACKEND_AVAILABLE or not hasattr(db_logic, "guardar_resultado_evaluacion"):
            print("WARN: Backend DB no disponible o función 'guardar_resultado_evaluacion' no encontrada.")
            return
        try:
            print(f"DEBUG: Guardando resultado para {self.logged_in_username}...")
            db_logic.guardar_resultado_evaluacion(
                self.logged_in_username,
                self.selected_curso or "N/A",
                self.selected_libro or "N/A",
                self.selected_tema or "Evaluación General",
                self.eval_nota if self.eval_nota is not None else 0.0,
                self.eval_correct_count,
                len(self.eval_preguntas)
            )
            print("DEBUG: Resultado guardado en BD.")
        except Exception as db_e:
            print(f"ERROR guardando resultado en BD: {db_e}\n{traceback.format_exc()}")

    def _parse_preguntas(self, preguntas_texto, tema, libro):
        """Parsea y valida las preguntas desde el formato de texto."""
        if not isinstance(preguntas_texto, dict) or not preguntas_texto:
            print("ERROR: El formato de preguntas no es un diccionario válido.")
            return []
            
        preguntas_final = []
        
        # Procesar cada tipo de pregunta
        for tipo, texto in preguntas_texto.items():
            if not texto or not isinstance(texto, str) or "Pregunta" not in texto:
                print(f"WARN: Texto de preguntas inválido para tipo '{tipo}'")
                continue
                
            lineas = texto.split("\n")
            i = 0
            while i < len(lineas):
                if lineas[i].strip().startswith("Pregunta"):
                    try:
                        # Extraer el texto de la pregunta
                        if ": " not in lineas[i]:
                            i += 1
                            continue
                        pregunta_text = lineas[i].split(": ", 1)[1].strip()
                        alternativas = []
                        correcta = ""
                        correctas = []
                        explicacion = ""
                        j = i + 1

                        # Extraer las alternativas según el tipo
                        if tipo == "verdadero_falso":
                            while j < len(lineas) and len(alternativas) < 2:
                                linea = lineas[j].strip()
                                if not linea or linea.startswith("Pregunta") or linea.startswith("Explicación"):
                                    break
                                if linea.startswith(("a)", "b)")):
                                    id_opt = linea.split(")")[0].strip().lower()
                                    texto_opt = linea.replace(") ", "").replace("(correcta)", "").strip()
                                    alternativas.append({"id": id_opt, "texto": texto_opt})
                                    if "(correcta)" in linea.lower():
                                        correcta = id_opt
                                j += 1
                        else:
                            while j < len(lineas) and len(alternativas) < 4:
                                linea = lineas[j].strip()
                                if not linea or linea.startswith("Pregunta") or linea.startswith("Explicación"):
                                    break
                                if linea.startswith(("a)", "b)", "c)", "d)")):
                                    id_opt = linea.split(")")[0].strip().lower()
                                    texto_opt = linea.replace(") ", "").replace("(correcta)", "").strip()
                                    alternativas.append({"id": id_opt, "texto": texto_opt})
                                    if "(correcta)" in linea.lower():
                                        if tipo == "seleccion_multiple":
                                            correctas.append(id_opt)
                                        else:
                                            correcta = id_opt
                                j += 1

                        # Extraer la explicación
                        if j < len(lineas) and lineas[j].strip().startswith("Explicación"):
                            if ": " in lineas[j]:
                                explicacion = lineas[j].split(": ", 1)[1].strip()
                            else:
                                explicacion = lineas[j].replace("Explicación", "").strip()
                            j += 1

                        # Validar y agregar la pregunta al resultado
                        if tipo == "verdadero_falso" and len(alternativas) == 2 and correcta:
                            preguntas_final.append({
                                "tipo": "verdadero_falso",
                                "pregunta": pregunta_text,
                                "opciones": alternativas,
                                "respuesta_correcta": correcta,
                                "explicacion": explicacion,
                                "tema": tema,
                                "libro": libro
                            })
                        elif tipo == "alternativas" and len(alternativas) == 4 and correcta:
                            preguntas_final.append({
                                "tipo": "opcion_multiple",
                                "pregunta": pregunta_text,
                                "opciones": alternativas,
                                "respuesta_correcta": correcta,
                                "explicacion": explicacion,
                                "tema": tema,
                                "libro": libro
                            })
                        elif tipo == "seleccion_multiple" and len(alternativas) == 4 and correctas:
                            preguntas_final.append({
                                "tipo": "seleccion_multiple",
                                "pregunta": pregunta_text,
                                "opciones": alternativas,
                                "respuesta_correcta": correctas,
                                "explicacion": explicacion,
                                "tema": tema,
                                "libro": libro
                            })
                        else:
                            print(f"WARN: Pregunta inválida en línea {i}: formato incorrecto o falta respuesta correcta")
                        i = j
                    except Exception as e:
                        print(f"ERROR al parsear pregunta en línea {i}: {e}")
                        i += 1
                else:
                    i += 1
                    
        return preguntas_final

    def generate_evaluation(self):
        """Genera una nueva evaluación basada en el curso, libro y tema seleccionados."""
        print("DEBUG: Iniciando generate_evaluation...")
        # Accede directamente a las variables heredadas de AppState vía self
        # (No es necesario reasignarlas a variables locales aquí si no las necesitas para lógica compleja)
        print(f"DEBUG (generate_evaluation): Usando (desde self) -> Curso='{self.selected_curso}', Libro='{self.selected_libro}', Tema='{self.selected_tema}'")

        # Validación de parámetros requeridos (usando self directamente)
        if not self.selected_curso:
            self.eval_error_message = "Por favor, selecciona un Curso antes de generar la evaluación."
            self.is_generation_in_progress = False
            print("ERROR: Curso no seleccionado en self.")
            yield # Importante para mostrar el mensaje de error
            return
        if not self.selected_libro:
            self.eval_error_message = "Por favor, selecciona un Libro antes de generar la evaluación."
            self.is_generation_in_progress = False
            print("ERROR: Libro no seleccionado en self.")
            yield # Importante para mostrar el mensaje de error
            return
        if not self.selected_tema:
            self.eval_error_message = "Por favor, selecciona un Tema antes de generar la evaluación."
            self.is_generation_in_progress = False
            print("ERROR: Tema no seleccionado en self.")
            yield # Importante para mostrar el mensaje de error
            return

        # Inicia proceso (variables locales no necesarias aquí)
        try:
            self.is_generation_in_progress = True
            self.eval_error_message = ""
            self.eval_preguntas = []
            self.eval_user_answers = {}
            self.eval_score = None
            self.eval_nota = None
            yield # Permite que la UI se actualice (mostrar loading)

            # Bloque para llamar al backend
            try:
                # --- CORRECCIÓN AQUÍ ---
                # Usa self.selected_... directamente en el print y en la llamada
                print(f"DEBUG: Llamando a eval_logic con C='{self.selected_curso}', L='{self.selected_libro}', T='{self.selected_tema}'")

                resultado_logica = eval_logic.generar_evaluacion_logica(
                    self.selected_curso, self.selected_libro, self.selected_tema
                )
                print(f"DEBUG: Resultado de eval_logic: {resultado_logica}")
                # --- FIN CORRECCIÓN ---

                # Procesar resultado (sin cambios aquí)
                if resultado_logica and resultado_logica.get("status") == "EXITO":
                    preguntas_recibidas = resultado_logica.get("preguntas", [])
                    print(f"DEBUG: Preguntas recibidas del backend: {len(preguntas_recibidas)}")

                    if not preguntas_recibidas:
                        self.eval_error_message = "No se pudieron generar preguntas para este tema."
                        print("WARN: Backend devolvió EXITO pero sin preguntas.")
                        # No retornamos el timer si no hay preguntas
                    else:
                        self.eval_preguntas = preguntas_recibidas
                        self.eval_user_answers = {i: None for i in range(len(self.eval_preguntas))}
                        self.is_eval_active = True # Marcar evaluación como activa
                        self.eval_total_q = len(self.eval_preguntas)
                        self.eval_current_idx = 0 # Empezar en la primera pregunta
                        print(f"DEBUG: Evaluación activada con {self.eval_total_q} preguntas. Índice actual: {self.eval_current_idx}")
                        # Iniciar el temporizador
                        return EvaluationState.start_eval_timer # Devuelve el método del timer para ejecutar
                else:
                    error_msg = resultado_logica.get("message", "Error desconocido del backend.")
                    self.eval_error_message = f"Error al generar: {error_msg}"
                    print(f"ERROR: Falla en eval_logic: {error_msg}")

            except Exception as e_backend:
                 print(f"ERROR: Excepción durante llamada a eval_logic: {e_backend}\n{traceback.format_exc()}")
                 self.eval_error_message = f"Error crítico llamando al backend: {e_backend}"

        except Exception as e_general:
             print(f"ERROR: Excepción general en generate_evaluation: {e_general}\n{traceback.format_exc()}")
             self.eval_error_message = f"Error inesperado: {e_general}"
        finally:
            # Este bloque se ejecuta siempre (después del try o después de un error)
            self.is_generation_in_progress = False
            print("DEBUG: Finalizado bloque generate_evaluation (finally).")
            # Yield final para asegurar que la UI refleje el estado final (loading=False, posible mensaje de error)
            yield

# --- Interfaz de Usuario (UI) ---

def create_confirmation_dialog():
    """Crea un diálogo de confirmación para preguntar si desea continuar con la siguiente pregunta."""
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header("Confirmación", font_size="lg", font_weight="bold"),
                rx.modal_body(
                    rx.text("¿Desea continuar con la iteración?", font_size="md")
                ),
                rx.modal_footer(
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            on_click=EvaluationState.cancel_continue,
                            color_scheme="gray",
                            size="sm",
                        ),
                        rx.button(
                            "Continuar",
                            on_click=EvaluationState.confirm_and_continue,
                            color_scheme=PRIMARY_COLOR_SCHEME,
                            size="sm",
                            ml=2,
                        ),
                    ),
                    justify="end",
                ),
                background="white",
                border_radius="md",
                box_shadow="lg",
            )
        ),
        is_open=EvaluationState.show_confirmation,
        size="sm",
    )

def parse_preguntas(texto_raw, tipo_evaluacion):
    """Parsea el texto crudo de preguntas de la API en una lista de diccionarios estructurados."""
    preguntas = []
    # Corrección: Usar 'or' en lugar de 'o'
    if (
        not texto_raw
        or "Pregunta" not in texto_raw
        or "Error:" in texto_raw
        or "Error " in texto_raw
    ):
        print(
            f"WARN (parse): Texto vacío, erróneo o sin 'Pregunta' para parsear tipo {tipo_evaluacion}: {texto_raw[:100]}...",
            file=sys.stderr,
        )
        return preguntas # Devuelve lista vacía si el texto de entrada ya indica error

    # ... resto de la función sin cambios ...