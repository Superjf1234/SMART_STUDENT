# Archivo: mi_app_estudio/evaluaciones.py

import reflex as rx
from typing import Dict, List, Set, Union, Any, Optional
# Importaciones relativas (asegúrate que sean correctas)
from .state import AppState, BACKEND_AVAILABLE, config_logic, eval_logic, db_logic, error_callout, PRIMARY_COLOR_SCHEME, ACCENT_COLOR_SCHEME
import asyncio # Necesario para sleep
import traceback
import random

# --- Constantes ---
MAX_QUESTIONS = 15 # Límite de preguntas
EVALUATION_TIME = 120 # Tiempo en segundos
# ------------------

# --- REEMPLAZA LA CLASE EvaluationState COMPLETA CON ESTO ---
class EvaluationState(AppState):
    """Estado específico para la funcionalidad de evaluaciones (Simplificado para Alternativas)."""

    is_eval_active: bool = False
    # is_reviewing_eval: bool = False # Eliminado
    eval_preguntas: List[Dict[str, Any]] = []
    eval_current_idx: int = 0
    eval_user_answers: Dict[int, Optional[str]] = {} # Simplificado
    eval_score: Optional[float] = None # Porcentaje 0-100
    eval_correct_count: int = 0
    eval_total_q: int = 0
    is_generation_in_progress: bool = False
    eval_error_message: str = ""
    eval_timer_active: bool = False
    eval_timer_paused: bool = False
    eval_timer_seconds: int = EVALUATION_TIME
    # eval_nota: Optional[float] = None # Eliminado
    show_result_modal: bool = False # Controla visibilidad del modal

    # --- Computed Vars ---
    @rx.var
    def current_eval_question(self) -> Optional[Dict[str, Any]]:
        """Devuelve el diccionario de la pregunta actual."""
        idx = self.eval_current_idx
        if self.eval_preguntas and 0 <= idx < len(self.eval_preguntas):
            q = self.eval_preguntas[idx]
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
        """Determina el color del timer."""
        return "red.500" if self.eval_timer_seconds <= 30 else "inherit"

    @rx.var
    def eval_progress(self) -> int:
        """Calcula el progreso de la evaluación."""
        total = len(self.eval_preguntas)
        if total == 0: return 0
        return int(min(100, max(0, ((self.eval_current_idx + 1) / total) * 100)))
        
    # Método normal (no variable computada) para verificar si una opción está seleccionada
    def check_if_option_selected(self, question_idx: int, option_id: str) -> bool:
        """
        Verifica si una opción específica está seleccionada en una pregunta de selección múltiple.
        
        Args:
            question_idx: Índice de la pregunta
            option_id: ID de la opción a verificar
            
        Returns:
            True si la opción está seleccionada, False en caso contrario
        """
        # Verificar si la pregunta existe en las respuestas del usuario
        if question_idx not in self.eval_user_answers:
            return False
            
        # Obtener la respuesta del usuario para esta pregunta
        answer = self.eval_user_answers.get(question_idx)
        
        # Si la respuesta es un conjunto (para selección múltiple)
        if isinstance(answer, set):
            return option_id in answer
            
        # Si la respuesta es una cadena (para otras preguntas)
        if isinstance(answer, str):
            return answer == option_id
            
        return False

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

    @rx.var
    def get_current_question_options_texts(self) -> List[str]:
        """Obtiene solo los textos de las opciones para usar directamente en rx.radio_group."""
        opciones = self.get_current_question_options
        return [opt["texto"] for opt in opciones]

    @rx.var
    def current_radio_group_value(self) -> str:
        """Devuelve la respuesta actual como string para radio_group."""
        idx = self.eval_current_idx
        if not (0 <= idx < len(self.eval_preguntas)):
            return ""
            
        answer = self.eval_user_answers.get(idx)
        current_q = self.eval_preguntas[idx] if idx < len(self.eval_preguntas) else None
        
        # Si no hay respuesta o pregunta actual, retornar cadena vacía
        if answer is None or not current_q:
            return ""
            
        # Si la respuesta es un conjunto (para selección múltiple), devolver cadena vacía
        # ya que los radio_group no se usan para preguntas de selección múltiple
        if isinstance(answer, set):
            return ""
            
        # Para preguntas de tipo verdadero/falso
        tipo_pregunta = current_q.get("tipo")
        if tipo_pregunta == "verdadero_falso" and isinstance(answer, str):
            if answer.lower() == "verdadero":
                return "Verdadero"
            elif answer.lower() == "falso":
                return "Falso"
            return answer
        
        # Para preguntas de opción múltiple/alternativas
        elif tipo_pregunta in ["opcion_multiple", "alternativas"]:
            # Buscar el texto de la opción seleccionada
            for opcion in current_q.get("alternativas", []):
                if isinstance(opcion, dict) and opcion.get("letra", opcion.get("id", "")) == answer:
                    return opcion.get("texto", "")
        
        # En cualquier otro caso inesperado
        return ""

    @rx.var
    def eval_mensaje_resultado(self) -> str:
        """Devuelve un mensaje motivacional basado en el score."""
        if self.eval_score is None: 
            return ""
            
        score = float(self.eval_score)
        import random
        
        # Mensajes categorizados por nivel de puntuación
        mensajes = {
            "bajo": [
                "¡Ánimo! Cada error es una oportunidad para aprender algo nuevo.",
                "La perseverancia es la clave del éxito. ¡Sigue intentándolo!",
                "No te desanimes. Edison falló miles de veces antes de inventar la bombilla.",
                "Recuerda que el proceso de aprendizaje es un camino, no un destino.",
                "El conocimiento se construye paso a paso. ¡Sigue adelante!"
            ],
            "medio_bajo": [
                "¡Vas por buen camino! Continúa practicando y verás resultados.",
                "Buen esfuerzo. Estás progresando con cada intento.",
                "Estás construyendo una base sólida. ¡Sigue así!",
                "Tus habilidades están creciendo. ¡Continúa con ese impulso!",
                "El aprendizaje es un proceso gradual. ¡Cada paso cuenta!"
            ],
            "medio_alto": [
                "¡Muy bien! Estás demostrando un dominio considerable del tema.",
                "¡Excelente trabajo! Tu dedicación está dando frutos.",
                "Tus conocimientos son sólidos. ¡Sigue perfeccionándolos!",
                "Estás cerca de la excelencia. ¡Un poco más de práctica te llevará allí!",
                "¡Gran desempeño! Tu esfuerzo está claramente visible."
            ],
            "alto": [
                "¡Impresionante dominio del tema! Has demostrado un gran conocimiento.",
                "¡Sobresaliente! Estás en el camino hacia la maestría.",
                "¡Excelente resultado! Tu comprensión del tema es realmente notable.",
                "¡Gran trabajo! Estás destacando con tu conocimiento y dedicación.",
                "¡Felicitaciones! Este resultado refleja tu dedicación al aprendizaje."
            ],
            "excelente": [
                "¡Perfección! Has demostrado un dominio excepcional del tema.",
                "¡Extraordinario! Tu comprensión del tema es realmente impresionante.",
                "¡Brillante! Has alcanzado la excelencia académica en este tema.",
                "¡Fenomenal! Este resultado muestra tu profunda comprensión y dedicación.",
                "¡Magnífico! Has alcanzado el nivel más alto de maestría en este tema."
            ]
        }
        
        # Seleccionar categoría según la puntuación
        if 0.0 <= score < 40.0:
            categoria = "bajo"
        elif 40.0 <= score < 60.0:
            categoria = "medio_bajo"
        elif 60.0 <= score < 80.0:
            categoria = "medio_alto" 
        elif 80.0 <= score < 90.0:
            categoria = "alto"
        else:
            categoria = "excelente"
            
        # Seleccionar un mensaje aleatorio de la categoría
        mensaje = random.choice(mensajes[categoria])
        return mensaje

    @rx.var
    def eval_titulo_resultado(self) -> str:
        """Genera un título divertido basado en el score obtenido."""
        if self.eval_score is None:
            return "Resultados"
            
        score = float(self.eval_score)
        
        # Títulos divertidos por categoría de puntuación
        titulos = {
            "bajo": [
                "¡Oops! ¡Houston, tenemos un problema! 🚀",
                "Mmm... ¿Necesitamos un Plan B? 🤔",
                "Modo Explorador: ¡Aún descubriendo el tema! 🔍",
                "El Aprendiz del Saber 🌱",
                "Proyecto en Construcción 🚧"
            ],
            "medio_bajo": [
                "¡En Marcha! Despegando... 🚀",
                "Aprendiz Prometedor 🌟",
                "Progresando a Ritmo Constante 🚶",
                "¡Cada Vez Más Cerca! 🎯",
                "Modo Estudiante: ¡Activado! 📚"
            ],
            "medio_alto": [
                "¡Cerebrito en Potencia! 🧠",
                "¡Buen Trabajo, Padawan! ⚔️",
                "Experto en Formación 🌟",
                "¡Casi un Maestro! 🎓",
                "¡Wow! ¡Nada mal! 👏"
            ],
            "alto": [
                "¡Super Cerebro! 🧠✨",
                "¡Maestro del Conocimiento! 🏆",
                "¡Einstein Estaría Orgulloso! 👨‍🔬",
                "¡Mente Brillante! 💡",
                "¡Sabiduría Level 9000! 🔝"
            ],
            "excelente": [
                "¡Genio Intergaláctico! 🌌🧠",
                "¡Súper Mega Ultra Cerebrito! 🤓✨",
                "¡Nivel: Leyenda Académica! 👑",
                "¡WOW! ¿Eres Profesor? 🎓🔥",
                "¡Cerebro en Modo Supernova! 💥🧠"
            ]
        }
        
        # Seleccionar categoría según la puntuación
        if 0.0 <= score < 40.0:
            categoria = "bajo"
        elif 40.0 <= score < 60.0:
            categoria = "medio_bajo"
        elif 60.0 <= score < 80.0:
            categoria = "medio_alto" 
        elif 80.0 <= score < 90.0:
            categoria = "alto"
        else:
            categoria = "excelente"
            
        # Seleccionar un título aleatorio de la categoría
        import random
        titulo = random.choice(titulos[categoria])
        return titulo

    # --- Timer Methods ---
    async def update_timer(self):
        """Actualiza el timer cada segundo si está activo."""
        if not self.eval_timer_active or self.eval_timer_paused: 
            return
            
        if self.eval_timer_seconds > 0:
            await asyncio.sleep(1)
            if not self.eval_timer_active or self.eval_timer_paused: 
                return
                
            self.eval_timer_seconds -= 1
            
            if self.eval_timer_seconds > 0:
                return EvaluationState.update_timer
            else:
                # CORREGIDO: Devolver referencia al método en lugar de yield directo
                print("DEBUG: ¡Tiempo agotado! (Detectado en update_timer)")
                self.eval_timer_seconds = 0
                self.eval_timer_active = False
                return EvaluationState.calculate_eval_score
        else:
            self.eval_timer_active = False
            return

    async def start_eval_timer(self):
        """Inicia el ciclo del timer."""
        print("DEBUG: Preparando e iniciando timer (start_eval_timer)...")
        self.eval_timer_seconds = EVALUATION_TIME
        self.eval_timer_active = True
        self.eval_timer_paused = False
        yield EvaluationState.update_timer

    async def pause_resume_timer(self):
        """Pausa o reanuda el timer."""
        if not self.eval_timer_active: return
        self.eval_timer_paused = not self.eval_timer_paused
        print(f"DEBUG: Timer pausado: {self.eval_timer_paused}")
        if not self.eval_timer_paused: yield EvaluationState.update_timer
        else: yield

    # ---> CORRECCIÓN: _stop_timer_async ahora es una corutina normal (sin yield) <---
    async def _stop_timer_async(self):
        """Detiene el timer (marcando flags). No necesita yield."""
        print("DEBUG: Deteniendo timer (flags)...")
        self.eval_timer_active = False
        self.eval_timer_paused = False
        # No hay yield aquí. La actualización la maneja calculate_eval_score
    # --------------------------------------------------------------------------------

    # --- Evaluation Flow Methods ---
    async def restart_evaluation(self):
        """Reinicia la evaluación."""
        print("DEBUG: Reiniciando evaluación...")
        await self._stop_timer_async() # Ahora se puede usar await
        self.eval_current_idx = 0; self.eval_user_answers = {}
        self.eval_score = None; self.eval_correct_count = 0;
        self.show_result_modal = False; self.eval_error_message = "";
        if not self.selected_curso or not self.selected_libro or not self.selected_tema:
             self.eval_error_message = "Selecciona Curso, Libro y Tema."; print(f"WARN: Faltan selecciones"); yield; return
        print("DEBUG: Generando nuevas preguntas...");
        yield EvaluationState.generate_evaluation # Llama a generar

    def close_result_modal(self):
        """Cierra el modal de resultados y resetea para nueva evaluación."""
        print("DEBUG: Cerrando modal y reseteando estado de evaluación...")
        self.show_result_modal = False
        self.is_eval_active = False
        self.eval_preguntas = []
        self.eval_user_answers = {}
        self.eval_current_idx = 0
        self.eval_score = None
        self.eval_correct_count = 0
        self.eval_total_q = 0
        self.eval_error_message = ""
        yield # Actualiza UI

    async def reset_evaluation_state(self):
        """Resetea completamente el estado de la evaluación al cambiar de pestaña."""
        print("DEBUG: Ejecutando reset_evaluation_state...")
        await self._stop_timer_async() # Detener timer si está activo
        self.is_eval_active = False
        self.eval_preguntas = []
        self.eval_current_idx = 0
        self.eval_user_answers = {}
        self.eval_score = None
        self.eval_correct_count = 0
        self.eval_total_q = 0
        self.is_generation_in_progress = False
        self.eval_error_message = ""
        self.eval_timer_active = False
        self.eval_timer_paused = False
        self.eval_timer_seconds = EVALUATION_TIME
        self.show_result_modal = False
        # También reseteamos la selección de AppState que usa esta pestaña
        self.selected_curso = ""
        self.selected_libro = ""
        self.selected_tema = ""
        print("DEBUG: Estado de EvaluationState reseteado.")
        yield # Asegura la actualización de la UI

    def set_eval_answer(self, answer_id: str):
        """Establece la respuesta (siempre selección única ahora)."""
        if not self.is_eval_active: return
        idx = self.eval_current_idx
        if not (0 <= idx < len(self.eval_preguntas)): return
        if isinstance(answer_id, str):
            self.eval_user_answers[idx] = answer_id
            print(f"DEBUG (set_eval_answer): Respuesta {idx} establecida a ID: {answer_id}")
        else:
            print(f"WARN: Valor inesperado para opción única: {answer_id}")
            self.eval_user_answers[idx] = ""
        yield # Actualiza UI

    def set_eval_answer_by_text(self, text: str):
        """Establece la respuesta basada en el texto seleccionado (para radio_group)."""
        if not self.is_eval_active or not text: 
            return
            
        idx = self.eval_current_idx
        if not (0 <= idx < len(self.eval_preguntas)): 
            return
            
        # Buscar el ID correspondiente al texto seleccionado
        opciones = self.get_current_question_options
        for opcion in opciones:
            if opcion["texto"] == text:
                self.eval_user_answers[idx] = opcion["id"]
                print(f"DEBUG (set_eval_answer_by_text): Respuesta {idx} establecida a ID: {opcion['id']} por texto: {text}")
                break
                
        yield # Actualiza UI

    def toggle_multiple_answer(self, option_id: str):
        """
        Agrega o elimina una opción de la selección múltiple (para preguntas que permiten varias respuestas).
        Para las preguntas de selección múltiple, guardamos un conjunto (set) de IDs seleccionados.
        """
        if not self.is_eval_active: return
        idx = self.eval_current_idx
        if not (0 <= idx < len(self.eval_preguntas)): return
        
        # Verificar que sea una pregunta de tipo selección múltiple
        current_q = self.eval_preguntas[idx] if idx < len(self.eval_preguntas) else None
        if not current_q or current_q.get("tipo") != "seleccion_multiple": 
            print(f"WARN: Intento de toggle_multiple en pregunta no múltiple")
            return
        
        # Inicializa como conjunto si aún no existe o no es un conjunto
        if idx not in self.eval_user_answers or not isinstance(self.eval_user_answers[idx], set):
            self.eval_user_answers[idx] = set()
        
        # Agrega o elimina la opción seleccionada
        current_selections = self.eval_user_answers[idx]
        if option_id in current_selections:
            current_selections.remove(option_id)
            print(f"DEBUG: Opción {option_id} eliminada del conjunto para pregunta {idx}")
        else:
            current_selections.add(option_id)
            print(f"DEBUG: Opción {option_id} añadida al conjunto para pregunta {idx}")
            
        yield # Actualiza la UI

    def next_eval_question(self):
        """Avanza a la siguiente pregunta."""
        idx = self.eval_current_idx; user_answer = self.eval_user_answers.get(idx)
        if user_answer is None or user_answer == "":
            self.eval_error_message = "Por favor, selecciona una respuesta."
            yield; return
        self.eval_error_message = ""
        if self.eval_preguntas and self.eval_current_idx < len(self.eval_preguntas) - 1:
            self.eval_current_idx += 1
            
            # Verificar el tipo de pregunta a la que estamos avanzando
            next_idx = self.eval_current_idx
            if next_idx < len(self.eval_preguntas):
                next_q = self.eval_preguntas[next_idx]
                # Si es de selección múltiple y no tiene respuesta previa, inicializar como conjunto vacío
                if isinstance(next_q, dict) and next_q.get("tipo") == "seleccion_multiple":
                    if next_idx not in self.eval_user_answers:
                        self.eval_user_answers[next_idx] = set()
                    # Si no es un conjunto (set), reiniciarlo como conjunto vacío
                    elif not isinstance(self.eval_user_answers[next_idx], set):
                        self.eval_user_answers[next_idx] = set()
                    
                    print(f"DEBUG: Inicializando respuesta vacía para pregunta de selección múltiple {next_idx}")
        
        yield # Actualiza UI

    def prev_eval_question(self):
        """Retrocede a la pregunta anterior."""
        if self.eval_current_idx > 0:
            self.eval_current_idx -= 1
            
            # Verificar el tipo de pregunta a la que estamos retrocediendo
            prev_idx = self.eval_current_idx
            if prev_idx >= 0 and prev_idx < len(self.eval_preguntas):
                prev_q = self.eval_preguntas[prev_idx]
                # Si es de selección múltiple y no tiene respuesta previa, inicializar como conjunto vacío
                if isinstance(prev_q, dict) and prev_q.get("tipo") == "seleccion_multiple":
                    if prev_idx not in self.eval_user_answers:
                        self.eval_user_answers[prev_idx] = set()
                    # Si no es un conjunto (set), reiniciarlo como conjunto vacío
                    elif not isinstance(self.eval_user_answers[prev_idx], set):
                        self.eval_user_answers[prev_idx] = set()
                    
                    print(f"DEBUG: Inicializando respuesta vacía para pregunta de selección múltiple {prev_idx}")
        
        yield # Actualiza UI

    # --- Cálculo de Score y Guardado ---
    def calculate_eval_score_sync(self):
        """Calcula el score (lógica síncrona simplificada). NO LLEVA YIELD."""
        print("DEBUG: Iniciando calculate_eval_score_sync...")
        if not self.eval_preguntas: self.eval_error_message = "No hay preguntas para evaluar."; return
        total = len(self.eval_preguntas);
        if total == 0: self.eval_error_message = "No hay preguntas válidas."; return
        correct = 0
        try:
            for i, q_dict in enumerate(self.eval_preguntas):
                if not isinstance(q_dict, dict): continue
                
                # Obtener respuesta del usuario y tipo de pregunta
                u_ans = self.eval_user_answers.get(i)
                tipo_pregunta = q_dict.get("tipo")
                
                # Para preguntas de selección múltiple (varias respuestas correctas)
                if tipo_pregunta == "seleccion_multiple":
                    # Respuestas correctas están en 'correctas' como una lista
                    c_ans_multiple = q_dict.get("correctas", q_dict.get("respuestas_correctas", []))
                    
                    # Convertimos respuesta a set si no lo es ya
                    u_ans_set = u_ans if isinstance(u_ans, set) else set()
                    c_ans_set = set(c_ans_multiple) if isinstance(c_ans_multiple, list) else set()
                    
                    # Verificamos si las respuestas coinciden exactamente
                    if u_ans_set == c_ans_set and len(u_ans_set) > 0:
                        print(f"DEBUG: Respuesta correcta (selección múltiple) para pregunta {i}")
                        correct += 1
                
                # Para preguntas de verdadero/falso y alternativas (una sola respuesta correcta)
                else:
                    c_ans_single = q_dict.get("correcta", q_dict.get("respuesta_correcta"))
                    # Manejo especial para booleanos de V/F si vinieran así
                    if isinstance(c_ans_single, bool):
                        c_ans_single = "verdadero" if c_ans_single else "falso"

                    # Comparación insensible a mayúsculas/minúsculas y espacios
                    if u_ans is not None and c_ans_single is not None:
                        if str(u_ans).strip().lower() == str(c_ans_single).strip().lower():
                            print(f"DEBUG: Respuesta correcta (opción única) para pregunta {i}")
                            correct += 1
            
            self.eval_correct_count = correct
            self.eval_score = round((correct / total) * 100.0, 1) if total > 0 else 0.0 # Redondea a 1 decimal
            print(f"DEBUG: Score calculado: {self.eval_score}%")
            self.is_eval_active = False
            self.eval_timer_active = False; self.eval_timer_paused = False
            self.show_result_modal = True # Muestra el modal
            self.eval_error_message = ""
            self._guardar_resultado_en_bd()
        except Exception as calc_e:
            print(f"ERROR cálculo score: {calc_e}\n{traceback.format_exc()}")
            self.eval_error_message = f"Error al calcular puntaje."
            self.is_eval_active = False; self.eval_timer_active = False; self.show_result_modal = False

    async def calculate_eval_score(self):
        """Wrapper async para calcular score y detener timer."""
        print("DEBUG: calculate_eval_score (async wrapper) llamado.")
        await self._stop_timer_async() # Llama a la corutina corregida
        self.calculate_eval_score_sync() # Calcula y actualiza estado
        yield # Actualiza UI para mostrar modal

    def handle_finish_evaluation(self): 
        """Handler para el botón 'Terminar Evaluación'."""
        print("DEBUG: handle_finish_evaluation llamado.")
        # CORREGIDO: Devolver una referencia al método de clase en lugar de llamar al método
        return EvaluationState.calculate_eval_score

    def _guardar_resultado_en_bd(self):
        """Guarda el resultado en BD (síncrono). NO LLEVA YIELD."""
        if not self.logged_in_username: print("WARN: Usuario no logueado"); return
        if not BACKEND_AVAILABLE or not hasattr(db_logic, "guardar_resultado_evaluacion"): print("WARN: DB no disponible"); return
        try:
            print(f"DEBUG: Guardando resultado para {self.logged_in_username}...")
            db_logic.guardar_resultado_evaluacion(
                 self.logged_in_username, self.selected_curso or "N/A",
                 self.selected_libro or "N/A", self.selected_tema or "Evaluación",
                 self.eval_score if self.eval_score is not None else 0.0, # Guarda el score %
                 self.eval_correct_count, len(self.eval_preguntas)
             )
            print("DEBUG: Resultado guardado en BD.")
        except Exception as db_e:
            print(f"ERROR guardando en BD: {db_e}\n{traceback.format_exc()}")

    async def generate_evaluation(self):
        """Genera una nueva evaluación con una distribución específica: 5 V/F, 5 alternativas, 5 selección múltiple."""
        print("DEBUG: Iniciando generate_evaluation con distribución específica...")
        curso = self.selected_curso; libro = self.selected_libro; tema = self.selected_tema
        if not curso or not libro or not tema:
            self.eval_error_message = "Selecciona Curso, Libro y Tema."; print(f"WARN: Falta selección"); yield; return

        self.is_generation_in_progress = True; self.eval_error_message = ""
        self.eval_preguntas = []; self.eval_user_answers = {}; self.eval_score = None
        # Aseguramos que el modal de resultados esté cerrado al iniciar una nueva evaluación
        self.show_result_modal = False  
        self.is_eval_active = False
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
                    # Clasificar preguntas por tipo
                    vf_preguntas = []
                    alt_preguntas = []
                    sm_preguntas = []
                    
                    for p in preguntas_recibidas:
                        if not isinstance(p, dict): 
                            continue
                        tipo = p.get("tipo")
                        if tipo == "verdadero_falso":
                            vf_preguntas.append(p)
                        elif tipo == "alternativas" or tipo == "opcion_multiple": 
                            alt_preguntas.append(p)
                        elif tipo == "seleccion_multiple":
                            sm_preguntas.append(p)
                    
                    # Limitar a 5 de cada tipo
                    random.shuffle(vf_preguntas)
                    random.shuffle(alt_preguntas)
                    random.shuffle(sm_preguntas)
                    
                    vf_final = vf_preguntas[:5]  # 5 preguntas V/F
                    alt_final = alt_preguntas[:5]  # 5 preguntas alternativas
                    sm_final = sm_preguntas[:5]  # 5 preguntas selección múltiple
                    
                    # Combinar todas las preguntas
                    todas_preguntas = []
                    todas_preguntas.extend(vf_final)
                    todas_preguntas.extend(alt_final)
                    todas_preguntas.extend(sm_final)
                    
                    # Verificar que tengamos suficientes preguntas
                    if len(todas_preguntas) < 15:
                        print(f"WARN: Solo se generaron {len(todas_preguntas)} preguntas")
                        print(f"DEBUG: V/F: {len(vf_final)}, Alt: {len(alt_final)}, SM: {len(sm_final)}")
                        # Si faltan preguntas de algún tipo, rellenar con otras
                        deficit = 15 - len(todas_preguntas)
                        if deficit > 0:
                            extras = []
                            # Priorizar rellenar con las que tengamos más
                            todas_originales = vf_preguntas[5:] + alt_preguntas[5:] + sm_preguntas[5:]
                            random.shuffle(todas_originales)
                            extras = todas_originales[:deficit]
                            todas_preguntas.extend(extras)
                            print(f"DEBUG: Añadidas {len(extras)} preguntas adicionales para llegar a 15")
                    
                    # Mezclar todas las preguntas
                    random.shuffle(todas_preguntas)
                    
                    # Limitar a MAX_QUESTIONS
                    self.eval_preguntas = todas_preguntas[:MAX_QUESTIONS]
                    self.eval_user_answers = {i: "" for i in range(len(self.eval_preguntas))}
                    self.is_eval_active = True
                    self.eval_total_q = len(self.eval_preguntas)
                    self.eval_current_idx = 0
                    print(f"DEBUG: Evaluación activada con {self.eval_total_q} preguntas distribuidas")
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
            if not self.eval_timer_active: yield # Asegura yield si no se inició timer

    # Handler para el botón 'Crear Evaluación'
    def handle_generate_evaluation(self):
        print("DEBUG: handle_generate_evaluation llamado.")
        # Llama a la función async generate_evaluation
        # Reflex maneja la llamada a funciones async desde handlers sync
        return EvaluationState.generate_evaluation

# --- Fin Clase EvaluationState ---
