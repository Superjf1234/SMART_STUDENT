# Archivo: mi_app_estudio/evaluaciones.py

import reflex as rx
from typing import Dict, List, Set, Union, Any, Optional
# Importaciones relativas (asegúrate que sean correctas)
from .state import AppState, BACKEND_AVAILABLE, config_logic, eval_logic, db_logic, error_callout, PRIMARY_COLOR_SCHEME, ACCENT_COLOR_SCHEME
import asyncio # Necesario para sleep
import traceback
import random

# --- Constantes ---
MAX_QUESTIONS = 15
EVALUATION_TIME = 120
MIN_RESUMEN_LENGTH = 50
# ------------------

# --- REEMPLAZA LA CLASE EvaluationState COMPLETA CON ESTO ---
class EvaluationState(AppState):
    """Estado específico para la funcionalidad de evaluaciones."""

    is_eval_active: bool = False
    is_reviewing_eval: bool = False
    eval_preguntas: List[Dict[str, Any]] = []
    eval_current_idx: int = 0
    eval_user_answers: Dict[int, Union[str, Set[str], None]] = {} # Permitir None inicial
    eval_score: Optional[float] = None
    eval_correct_count: int = 0
    eval_total_q: int = 0
    is_generation_in_progress: bool = False
    eval_error_message: str = ""
    eval_timer_active: bool = False
    eval_timer_paused: bool = False
    eval_timer_seconds: int = EVALUATION_TIME
    eval_nota: Optional[float] = None
    show_result_modal: bool = False
    show_explanation: bool = False
    show_confirmation: bool = False
    next_question_idx: Optional[int] = None

    # --- Computed Vars ---
    @rx.var
    def current_eval_question(self) -> Optional[Dict[str, Any]]:
        """Devuelve el diccionario de la pregunta actual."""
        idx = self.eval_current_idx
        preguntas_actuales = self.eval_preguntas if self.eval_preguntas else []
        total_preguntas = len(preguntas_actuales)
        if preguntas_actuales and 0 <= idx < total_preguntas:
            q = preguntas_actuales[idx]
            return q if isinstance(q, dict) else None
        return None

    @rx.var
    def is_last_eval_question(self) -> bool:
        return len(self.eval_preguntas) > 0 and self.eval_current_idx >= len(self.eval_preguntas) - 1

    @rx.var
    def is_first_eval_question(self) -> bool:
        return self.eval_current_idx <= 0

    @rx.var
    def eval_time_formatted(self) -> str:
        minutes = self.eval_timer_seconds // 60
        seconds = self.eval_timer_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    @rx.var
    def eval_time_color(self) -> str:
        return "red.500" if self.eval_timer_seconds <= 30 else "inherit"

    @rx.var
    def eval_nota_formateada(self) -> str:
        if self.eval_nota is None or self.eval_nota < 0: return "1,0"
        nota = 1.0 + (max(0.0, min(100.0, self.eval_nota)) / 100.0) * 6.0
        return f"{nota:.1f}".replace('.', ',')

    @rx.var
    def eval_progress(self) -> int:
        total = len(self.eval_preguntas)
        if total == 0: return 0
        return int(min(100, max(0, ((self.eval_current_idx + 1) / total) * 100)))

    @rx.var
    def get_current_question_options(self) -> List[Dict[str, str]]:
        """Obtiene y formatea las opciones para la pregunta actual."""
        current_q = self.current_eval_question
        if not current_q: return []
        opciones = current_q.get("alternativas", current_q.get("opciones", []))
        if not isinstance(opciones, list): print(f"WARN: Opciones no es lista: {opciones}"); return []
        formatted = []
        for i, opt in enumerate(opciones):
            if isinstance(opt, dict):
                opt_id = opt.get("letra", opt.get("id", f"opt_{i}"))
                opt_text = opt.get("texto", f"Opción {opt_id}")
                formatted.append({"id": str(opt_id), "texto": str(opt_text)})
            else: formatted.append({"id": str(opt).lower(), "texto": str(opt)})
        return formatted

    # ---> NUEVA VAR COMPUTADA <---
    @rx.var
    def get_current_question_option_texts(self) -> List[str]:
        """Devuelve solo los textos de las opciones actuales para usar con 'items'."""
        options_dicts = self.get_current_question_options
        return [opt.get("texto", "") for opt in options_dicts]
    # ----------------------------

    @rx.var
    def eval_mensaje_resultado(self) -> str:
        if self.eval_nota is None: return ""
        nota_float = float(self.eval_nota)
        if 0.0 <= nota_float <= 39.9: return "¡Ánimo! Sigue practicando."
        elif 40.0 <= nota_float <= 59.9: return "¡Buen esfuerzo! Sigue así."
        elif 60.0 <= nota_float <= 89.9: return "¡Muy bien! Cerca de la excelencia."
        else: return "¡Excelente! Resultado sobresaliente."

    # --- Option Status Methods ---
    def get_option_status(self, option_id: str) -> Dict[str, Any]:
        # ... (sin cambios) ...
        if not self.is_reviewing_eval: return {"color": "inherit", "suffix": ""}
        current_q = self.current_eval_question;
        if not current_q: return {"color": "inherit", "suffix": ""}
        user_answer = self.eval_user_answers.get(self.eval_current_idx); q_type = current_q.get("tipo")
        is_correct_option = False
        if q_type == "seleccion_multiple":
            correct_answers = current_q.get("correctas", [])
            is_correct_option = str(option_id) in [str(c) for c in correct_answers]
        else:
            correct_answer = current_q.get("correcta", current_q.get("respuesta_correcta"))
            is_correct_option = str(option_id) == str(correct_answer)
        user_selected_this = False
        if q_type == "seleccion_multiple":
            user_selected_this = isinstance(user_answer, set) and str(option_id) in user_answer
        else:
            user_selected_this = str(option_id) == str(user_answer)
        if user_selected_this and is_correct_option: return {"color": "green.500", "suffix": " ✔ (Correcta)"}
        elif user_selected_this and not is_correct_option: return {"color": "red.500", "suffix": " ✘ (Incorrecta)"}
        elif not user_selected_this and is_correct_option: return {"color": "green.500", "suffix": " (Correcta)"}
        else: return {"color": "inherit", "suffix": ""}

    # --- Timer Methods ---
    # ... (start_eval_timer, update_timer, pause_resume_timer, _stop_timer_async sin cambios) ...
    async def update_timer(self):
        if not self.eval_timer_active or self.eval_timer_paused: return
        if self.eval_timer_seconds > 0:
            await asyncio.sleep(1)
            if not self.eval_timer_active or self.eval_timer_paused: return
            self.eval_timer_seconds -= 1
            if self.eval_timer_seconds > 0: yield EvaluationState.update_timer
            else:
                 print("DEBUG: ¡Tiempo agotado! (Detectado en update_timer)")
                 self.eval_timer_seconds = 0; self.eval_timer_active = False
                 yield self.calculate_eval_score()
        else: self.eval_timer_active = False; yield

    async def start_eval_timer(self):
        print("DEBUG: Preparando e iniciando timer (start_eval_timer)...")
        self.eval_timer_seconds = EVALUATION_TIME
        self.eval_timer_active = True
        self.eval_timer_paused = False
        yield EvaluationState.update_timer

    async def pause_resume_timer(self):
        if not self.eval_timer_active: return
        self.eval_timer_paused = not self.eval_timer_paused
        print(f"DEBUG: Timer pausado: {self.eval_timer_paused}")
        if not self.eval_timer_paused: yield EvaluationState.update_timer
        else: yield

    async def _stop_timer_async(self):
         print("DEBUG: Deteniendo timer (flags)...")
         self.eval_timer_active = False
         self.eval_timer_paused = False
         yield

    # --- Evaluation Flow Methods ---
    # ... (restart_evaluation, close_result_modal, set_show_result_modal, toggle_explanation sin cambios) ...
    async def restart_evaluation(self):
        print("DEBUG: Reiniciando evaluación...")
        await self._stop_timer_async()
        self.is_reviewing_eval = False; self.eval_current_idx = 0; self.eval_user_answers = {}
        self.eval_score = None; self.eval_correct_count = 0; self.eval_nota = None
        self.show_result_modal = False; self.eval_error_message = ""; self.show_explanation = False
        if not self.selected_curso or not self.selected_libro or not self.selected_tema:
             self.eval_error_message = "Selecciona Curso, Libro y Tema."; print(f"WARN: Faltan selecciones"); yield; return
        if not self.eval_preguntas: print("DEBUG: No hay preguntas, generando nuevas..."); yield EvaluationState.generate_evaluation
        else:
             print("DEBUG: Usando preguntas existentes, iniciando timer..."); self.is_eval_active = True
             self.eval_total_q = len(self.eval_preguntas)
             self.eval_user_answers = {
                 i: set() if p.get("tipo") == "seleccion_multiple" else ""
                 for i, p in enumerate(self.eval_preguntas)
             }
             yield EvaluationState.start_eval_timer

    def close_result_modal(self): self.show_result_modal = False; yield
    def set_show_result_modal(self, is_open: bool): self.show_result_modal = is_open; yield
    def toggle_explanation(self):
         if self.is_reviewing_eval: self.show_explanation = not self.show_explanation; yield

    # ---> MODIFICADO set_eval_answer <---
    def set_eval_answer(self, answer_text: str): # Ahora recibe el TEXTO
        """Establece la respuesta buscando el ID correspondiente al texto."""
        if not self.is_eval_active or self.is_reviewing_eval: return
        idx = self.eval_current_idx
        current_q = self.current_eval_question
        if not current_q or not (0 <= idx < len(self.eval_preguntas)): return

        q_type = current_q.get("tipo")
        if q_type != "seleccion_multiple": # Para opción única/V&F/alternativas
            # Buscar el ID que corresponde al texto seleccionado
            option_id = ""
            options_list = self.get_current_question_options # Obtiene [{'id': 'a', 'texto': '...'}]
            for opt in options_list:
                if opt.get("texto") == answer_text:
                    option_id = opt.get("id", "")
                    break

            if option_id:
                self.eval_user_answers[idx] = option_id # Guardar el ID encontrado
                print(f"DEBUG: Respuesta {idx} establecida a ID: {option_id} (basado en texto: '{answer_text}')")
            else:
                # Si no se encuentra ID (raro, pero posible si el texto tiene caracteres especiales)
                # Guardamos el texto como fallback, aunque puede fallar la corrección
                print(f"WARN: No se encontró ID para el texto de respuesta: '{answer_text}'. Guardando texto.")
                self.eval_user_answers[idx] = answer_text
        else:
             # La lógica para seleccion_multiple (checkboxes) necesita otra función on_change
             print(f"WARN: set_eval_answer llamado para tipo {q_type}. Usar handler de checkbox.")

        yield # Actualiza UI
    # ------------------------------------

    def next_eval_question(self):
        # ... (sin cambios, pero ya tenía yield) ...
        if self.is_reviewing_eval:
            if self.eval_preguntas and self.eval_current_idx < len(self.eval_preguntas) - 1: self.eval_current_idx += 1; self.show_explanation = False
            yield; return
        idx = self.eval_current_idx; user_answer = self.eval_user_answers.get(idx)
        current_q = self.current_eval_question;
        if not current_q: yield; return
        q_type = current_q.get("tipo", "opcion_multiple")
        is_answered = False
        if q_type == "seleccion_multiple": is_answered = isinstance(user_answer, set) and bool(user_answer)
        else: is_answered = user_answer is not None and user_answer != ""
        if not is_answered: self.eval_error_message = "Por favor, selecciona una respuesta."; yield; return
        self.eval_error_message = ""
        if self.eval_preguntas and self.eval_current_idx < len(self.eval_preguntas) - 1: self.eval_current_idx += 1
        yield

    def prev_eval_question(self):
        # ... (sin cambios, pero ya tenía yield) ...
        if self.eval_current_idx > 0:
            self.eval_current_idx -= 1
            if self.is_reviewing_eval: self.show_explanation = False
        yield

    # --- Cálculo de Score y Guardado ---
    # ... (calculate_eval_score_sync, calculate_eval_score, _guardar_resultado_en_bd sin cambios) ...
    def calculate_eval_score_sync(self):
        print("DEBUG: Iniciando calculate_eval_score_sync...")
        if not self.eval_preguntas: self.eval_error_message = "No hay preguntas para evaluar."; return
        total = len(self.eval_preguntas);
        if total == 0: self.eval_error_message = "No hay preguntas válidas."; return
        correct = 0
        try:
            for i, q_dict in enumerate(self.eval_preguntas):
                if not isinstance(q_dict, dict): continue
                u_ans = self.eval_user_answers.get(i)
                q_type = q_dict.get("tipo")
                correct_inc = 0
                if q_type == "seleccion_multiple":
                    c_ans_list = q_dict.get("correctas", q_dict.get("respuesta_correcta", []))
                    c_set = set(map(str, c_ans_list)) if isinstance(c_ans_list, list) else set()
                    u_set = u_ans if isinstance(u_ans, set) else set()
                    if u_set == c_set: correct_inc = 1
                else:
                    c_ans_single = q_dict.get("correcta", q_dict.get("respuesta_correcta"))
                    # Comparamos el ID guardado (u_ans) con el ID correcto (c_ans_single)
                    if isinstance(u_ans, str) and u_ans == str(c_ans_single): correct_inc = 1
                correct += correct_inc
            self.eval_correct_count = correct
            self.eval_score = (correct / total) * 100.0 if total > 0 else 0.0
            self.eval_nota = self.eval_score
            print(f"DEBUG: Score calculado: {self.eval_score}, Nota base: {self.eval_nota}")
            self.is_reviewing_eval = True; self.is_eval_active = False
            self.eval_timer_active = False; self.eval_timer_paused = False
            self.eval_current_idx = 0; self.show_result_modal = True
            self.eval_error_message = ""; self._guardar_resultado_en_bd()
        except Exception as calc_e:
            print(f"ERROR cálculo score: {calc_e}\n{traceback.format_exc()}")
            self.eval_error_message = "Error al calcular puntaje."
            self.is_reviewing_eval = False; self.is_eval_active = False
            self.eval_timer_active = False; self.show_result_modal = False

    async def calculate_eval_score(self):
        print("DEBUG: calculate_eval_score (async wrapper) llamado.")
        await self._stop_timer_async()
        self.calculate_eval_score_sync()
        yield

    def _guardar_resultado_en_bd(self):
        if not self.logged_in_username: print("WARN: Usuario no logueado"); return
        if not BACKEND_AVAILABLE or not hasattr(db_logic, "guardar_resultado_evaluacion"): print("WARN: DB no disponible"); return
        try:
            print(f"DEBUG: Guardando resultado para {self.logged_in_username}...")
            db_logic.guardar_resultado_evaluacion(
                 self.logged_in_username, self.selected_curso or "N/A",
                 self.selected_libro or "N/A", self.selected_tema or "Evaluación",
                 self.eval_nota if self.eval_nota is not None else 0.0,
                 self.eval_correct_count, len(self.eval_preguntas)
             )
            print("DEBUG: Resultado guardado en BD.")
        except Exception as db_e:
            print(f"ERROR guardando en BD: {db_e}\n{traceback.format_exc()}")

    # ... (generate_evaluation sin cambios respecto a la versión anterior) ...
    async def generate_evaluation(self):
        print("DEBUG: Iniciando generate_evaluation...")
        curso = self.selected_curso; libro = self.selected_libro; tema = self.selected_tema
        if not curso or not libro or not tema:
            self.eval_error_message = "Selecciona Curso, Libro y Tema."; print(f"WARN: Falta selección"); yield; return
        self.is_generation_in_progress = True; self.eval_error_message = ""
        self.eval_preguntas = []; self.eval_user_answers = {}; self.eval_score = None
        self.eval_nota = None; self.is_eval_active = False; self.is_reviewing_eval = False
        yield # Mostrar loading
        try:
            print(f"DEBUG: Llamando a eval_logic con C='{curso}', L='{libro}', T='{tema}'")
            resultado_logica = eval_logic.generar_evaluacion_logica(curso, libro, tema)
            print(f"DEBUG: Resultado de lógica backend: {resultado_logica}")
            if resultado_logica and resultado_logica.get("status") == "EXITO":
                preguntas_recibidas = resultado_logica.get("preguntas", [])
                if not preguntas_recibidas:
                    self.eval_error_message = "No se pudieron generar preguntas."; print("WARN: No se generaron preguntas.")
                else:
                    random.shuffle(preguntas_recibidas)
                    self.eval_preguntas = preguntas_recibidas[:MAX_QUESTIONS]
                    self.eval_user_answers = {
                        i: set() if p.get("tipo") == "seleccion_multiple" else ""
                        for i, p in enumerate(self.eval_preguntas) if isinstance(p, dict)
                    }
                    self.is_eval_active = True
                    self.eval_total_q = len(self.eval_preguntas)
                    self.eval_current_idx = 0
                    print(f"DEBUG: Evaluación activada con {self.eval_total_q} preguntas.")
                    yield EvaluationState.start_eval_timer
            else:
                error_msg = resultado_logica.get("message", "Error backend.")
                self.eval_error_message = f"Error al generar: {error_msg}"
                print(f"ERROR: Falla en eval_logic: {error_msg}")
        except Exception as e:
            print(f"ERROR: Excepción en generate_evaluation: {e}\n{traceback.format_exc()}")
            self.eval_error_message = f"Error inesperado: {e}"
        finally:
            self.is_generation_in_progress = False
            yield

# --- Fin Clase EvaluationState ---

