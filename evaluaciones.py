# Archivo: mi_app_estudio/evaluaciones.py

import reflex as rx
from typing import Dict, List, Set, Union, Any, Optional
# Importaciones relativas (asegúrate que sean correctas)
from mi_app_estudio.state import AppState, BACKEND_AVAILABLE, config_logic, eval_logic, db_logic, error_callout, PRIMARY_COLOR_SCHEME, ACCENT_COLOR_SCHEME
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
    is_reviewing_eval: bool = False
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
    
    @rx.var
    def is_current_question_correct_in_review(self) -> bool:
        """Verifica si la pregunta actual es correcta en modo revisión."""
        if not self.is_reviewing_eval or self.eval_current_idx >= len(self.eval_preguntas):
            return False
            
        user_answer = self.eval_user_answers[self.eval_current_idx] if self.eval_current_idx in self.eval_user_answers else None
        correct_answer = self.get_correct_answer_for_current_question()
        
        # Comparar según el tipo de pregunta
        pregunta_actual = self.get_current_question()
        if not pregunta_actual:
            return False
            
        tipo = pregunta_actual.get("tipo")
        
        # Para V/F y alternativas simples
        if tipo in ["verdadero_falso", "alternativas", "opcion_multiple"]:
            return user_answer == correct_answer
        # Para selección múltiple
        elif tipo == "seleccion_multiple":
            if isinstance(user_answer, set) and isinstance(correct_answer, set):
                return user_answer == correct_answer
            return False
        
        return False
    
    @rx.var
    def get_correct_answer_text(self) -> str:
        """Obtiene el texto de la respuesta correcta para la pregunta actual."""
        pregunta_actual = self.get_current_question()
        if not pregunta_actual:
            return ""
            
        tipo = pregunta_actual.get("tipo")
        correct_answer = self.get_correct_answer_for_current_question()
        
        if tipo == "verdadero_falso":
            return "Verdadero" if correct_answer == "verdadero" else "Falso"
        elif tipo in ["alternativas", "opcion_multiple"]:
            # Buscar el texto de la opción correcta
            opciones = pregunta_actual.get("opciones", [])
            for opcion in opciones:
                if isinstance(opcion, dict) and opcion.get("id") == correct_answer:
                    return opcion.get("texto", "")
            return str(correct_answer)
        elif tipo == "seleccion_multiple" and isinstance(correct_answer, set):
            # Convertir el conjunto de IDs en texto
            textos = []
            opciones = pregunta_actual.get("opciones", [])
            for opcion in opciones:
                if isinstance(opcion, dict) and opcion.get("id") in correct_answer:
                    textos.append(opcion.get("texto", ""))
            return ", ".join(textos) if textos else ""
        
        return str(correct_answer)
        
    def get_current_question(self) -> Dict[str, Any]:
        """Obtiene el diccionario de la pregunta actual."""
        idx = self.eval_current_idx
        if self.eval_preguntas and 0 <= idx < len(self.eval_preguntas):
            q = self.eval_preguntas[idx]
            return q if isinstance(q, dict) else None
        return None
        
    @rx.var
    def get_current_explanation(self) -> str:
        """Obtiene la explicación de la pregunta actual."""
        pregunta_actual = self.get_current_question()
        if not pregunta_actual:
            return ""
            
        # Obtener la explicación de la pregunta, con manejo de diferentes nombres de campo posibles
        explicacion = pregunta_actual.get("explicacion", pregunta_actual.get("explanation", ""))
        return explicacion if explicacion else ""
        
    # Método para obtener la respuesta correcta de la pregunta actual
    def get_correct_answer_for_current_question(self):
        """Obtiene la respuesta correcta de la pregunta actual."""
        pregunta_actual = self.get_current_question()
        if not pregunta_actual:
            return None
            
        tipo = pregunta_actual.get("tipo")
        
        if tipo == "seleccion_multiple":
            # Para selección múltiple, la respuesta correcta es un conjunto de IDs
            correctas = set()
            opciones = pregunta_actual.get("opciones", [])
            for opcion in opciones:
                if isinstance(opcion, dict) and opcion.get("correcta", False):
                    correctas.add(opcion.get("id"))
            return correctas
        else:
            # Para V/F y alternativas simples
            return pregunta_actual.get("respuesta")
        
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
            
        # Obtener la respuesta del usuario para esta pregunta si existe
        if question_idx in self.eval_user_answers:
            answer = self.eval_user_answers[question_idx]
            
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
            
        answer = self.eval_user_answers[idx] if idx in self.eval_user_answers else None
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

    @rx.var
    def eval_score_rounded(self) -> int:
        """Devuelve el puntaje redondeado para mostrar en la UI."""
        if self.eval_score is None:
            return 0
        return int(round(self.eval_score))

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
        self.is_reviewing_eval = False;
        if not self.selected_curso or not self.selected_libro or not self.selected_tema:
             self.eval_error_message = "Selecciona Curso, Libro y Tema."; print(f"WARN: Faltan selecciones"); yield; return
        print("DEBUG: Generando nuevas preguntas...");
        yield EvaluationState.generate_evaluation # Llama a generar

    def close_result_modal(self):
        """Cierra el modal de resultados y resetea para nueva evaluación."""
        print("DEBUG: Cerrando modal y reseteando estado de evaluación...")
        self.show_result_modal = False
        self.is_eval_active = False
        self.is_reviewing_eval = False
        self.eval_preguntas = []
        self.eval_user_answers = {}
        self.eval_current_idx = 0
        self.eval_score = None
        self.eval_correct_count = 0
        self.eval_total_q = 0
        self.eval_error_message = ""
        yield # Actualiza UI
        
    def review_evaluation(self):
        """Cierra el modal de resultados y permite revisar la evaluación por pregunta."""
        print("DEBUG: Iniciando revisión de la evaluación...")
        self.show_result_modal = False
        self.is_reviewing_eval = True
        self.eval_current_idx = 0 # Vuelve a la primera pregunta
        yield # Actualiza UI

    async def reset_evaluation_state(self):
        """Resetea completamente el estado de la evaluación al cambiar de pestaña."""
        print("DEBUG: Ejecutando reset_evaluation_state...")
        await self._stop_timer_async() # Detener timer si está activo
        self.is_eval_active = False
        self.is_reviewing_eval = False
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
            # Determinar el tipo de pregunta
            current_q = self.eval_preguntas[idx] if idx < len(self.eval_preguntas) else None
            tipo_pregunta = current_q.get("tipo") if current_q else None
            
            # Para preguntas de tipo verdadero/falso, normalizar a minúsculas
            if tipo_pregunta == "verdadero_falso":
                normalized_answer = answer_id.strip().lower()
                # Asegurar que sea "verdadero" o "falso" (formato estándar)
                if normalized_answer in ["verdadero", "true", "v", "t"]:
                    normalized_answer = "verdadero"
                elif normalized_answer in ["falso", "false", "f"]:
                    normalized_answer = "falso"
                self.eval_user_answers[idx] = normalized_answer
                print(f"DEBUG (set_eval_answer): Respuesta V/F {idx} normalizada a: {normalized_answer}")
            else:
                # Para otros tipos de preguntas, guardar tal cual
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
         
        # Determinar el tipo de pregunta
        current_q = self.eval_preguntas[idx] if idx < len(self.eval_preguntas) else None
        tipo_pregunta = current_q.get("tipo") if current_q else None
            
        # Para preguntas de tipo verdadero/falso, normalizar directamente
        if tipo_pregunta == "verdadero_falso":
            # Manejar directamente las respuestas V/F por texto
            normalized_answer = text.strip().lower()
            # Asegurar que sea "verdadero" o "falso" (formato estándar)
            if normalized_answer in ["verdadero", "true", "v", "t"]:
                normalized_answer = "verdadero"
            elif normalized_answer in ["falso", "false", "f"]:
                normalized_answer = "falso"
            self.eval_user_answers[idx] = normalized_answer
            print(f"DEBUG (set_eval_answer_by_text): Respuesta V/F {idx} normalizada a: {normalized_answer}")
        else:
            # Para otros tipos de preguntas, buscar el ID correspondiente al texto
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
        idx = self.eval_current_idx; user_answer = self.eval_user_answers[idx] if idx in self.eval_user_answers else None
        if user_answer is None or user_answer == "":
            self.eval_error_message = "Por favor, selecciona una respuesta."
            yield; return
        self.eval_error_message = ""
        
        # Verificar si hay preguntas disponibles y avanzar siempre que sea posible
        if self.eval_preguntas:
            # Solo avanzar si hay una siguiente pregunta
            if self.eval_current_idx < len(self.eval_preguntas) - 1:
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
                u_ans = self.eval_user_answers[i] if i in self.eval_user_answers else None
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
                        c_ans_single = "verdadero" if cAns_single else "falso"

                    # Normalización para verdadero/falso
                    if tipo_pregunta == "verdadero_falso":
                        # Normalizar la respuesta del usuario
                        u_ans_normalized = str(u_ans).strip().lower() if u_ans is not None else ""
                        if u_ans_normalized in ["verdadero", "true", "v", "t", "a"]:
                            u_ans_normalized = "verdadero"
                        elif u_ans_normalized in ["falso", "false", "f", "b"]:
                            u_ans_normalized = "falso"
                            
                        # Normalizar la respuesta correcta
                        c_ans_normalized = str(c_ans_single).strip().lower()
                        if c_ans_normalized in ["verdadero", "true", "v", "t", "a"]:
                            c_ans_normalized = "verdadero"
                        elif c_ans_normalized in ["falso", "false", "f", "b"]:
                            c_ans_normalized = "falso"
                            
                        # Comparación de valores normalizados
                        if u_ans_normalized == c_ans_normalized:
                            print(f"DEBUG: Respuesta correcta V/F para pregunta {i} ({u_ans_normalized} == {c_ans_normalized})")
                            correct += 1
                    # Para otras preguntas de opción única
                    elif u_ans is not None and c_ans_single is not None:
                        if str(u_ans).strip().lower() == str(c_ans_single).strip().lower():
                            print(f"DEBUG: Respuesta correcta (opción única) para pregunta {i}")
                            correct += 1
            
            self.eval_correct_count = correct
            # Si no hay respuestas correctas, el score debe ser 0%, de lo contrario calcularlo normalmente
            self.eval_score = 0.0 if correct == 0 else round((correct / total) * 100.0, 1)
            # Asegurarse de que el score esté en el rango 0-100
            self.eval_score = max(0.0, min(100.0, self.eval_score))
            print(f"DEBUG: Score calculado: {self.eval_score}%")
            
            # CORREGIDO: Mantener is_eval_active en True mientras se muestra el modal
            # self.is_eval_active = False  <- Esta línea se comentó
            
            self.eval_timer_active = False; self.eval_timer_paused = False
            self.show_result_modal = True # Muestra el modal
            print(f"DEBUG: show_result_modal set to {self.show_result_modal}")
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
        print("DEBUG: Después de calculate_eval_score_sync, show_result_modal =", self.show_result_modal)
        # Añadimos un paso adicional para forzar la actualización del UI
        self.show_result_modal = True
        print("DEBUG: Forzado show_result_modal =", self.show_result_modal)
        yield # Actualiza UI para mostrar modal
        
        # Ya no intentamos actualizar estadísticas automáticamente pues causa error
        # Los usuarios deberán ir a la pestaña de perfil para ver sus estadísticas actualizadas

    def handle_finish_evaluation(self): 
        """Handler para el botón 'Terminar Evaluación'."""
        print("DEBUG: handle_finish_evaluation llamado.")
        # CORREGIDO: Devolver una referencia al método de clase en lugar de llamar al método
        return EvaluationState.calculate_eval_score

    def _guardar_resultado_en_bd(self):
        """Guarda el resultado en BD (síncrono). NO LLEVA YIELD."""
        print(f"DEBUG: Verificando usuario logueado: {self.logged_in_username}")
        if not hasattr(self, 'logged_in_username') or not self.logged_in_username:
            # Si no está establecido en EvaluationState, intentar obtenerlo de AppState
            print("WARN: Usuario no logueado en EvaluationState")
            # Ya no intentamos obtener de AppState.get_instance() porque causa error
            return
        
        if not BACKEND_AVAILABLE or not hasattr(db_logic, "guardar_resultado_evaluacion"):
            print("WARN: DB no disponible")
            return
        
        try:
            print(f"DEBUG: Guardando resultado para {self.logged_in_username}...")
            # Calcular nota en escala 1.0-7.0 para el sistema chileno
            # Fórmula: nota = (porcentaje * 6.0 / 100) + 1.0
            porcentaje = self.eval_score if self.eval_score is not None else 0.0
            nota_sistema_chileno = (porcentaje * 6.0 / 100) + 1.0
            nota_sistema_chileno = round(nota_sistema_chileno, 1)  # Redondear a un decimal
            
            print(f"DEBUG: Porcentaje {porcentaje}% convertido a nota {nota_sistema_chileno} (sistema 1.0-7.0)")
            
            db_logic.guardar_resultado_evaluacion(
                 self.logged_in_username, self.selected_curso or "N/A",
                 self.selected_libro or "N/A", self.selected_tema or "Evaluación",
                 nota_sistema_chileno,  # Guardar la nota en escala 1.0-7.0
                 self.eval_correct_count, len(self.eval_preguntas)
             )
            print(f"DEBUG: Resultado guardado en BD: Nota={nota_sistema_chileno}, Correctas={self.eval_correct_count}/{len(self.eval_preguntas)}")
            
            # Ya no intentamos actualizar estadísticas aquí, lo haremos en el front-end
            # después de mostrar el modal de resultados
            
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
                    # Filtrar las preguntas duplicadas antes de clasificar
                    # Usaremos el texto de la pregunta como identificador único
                    preguntas_unicas = {}
                    for p in preguntas_recibidas:
                        if not isinstance(p, dict):
                            continue
                        texto_pregunta = p.get("pregunta", "").strip()
                        # Solo añadir si no existe ya una pregunta con el mismo texto
                        if texto_pregunta and texto_pregunta not in preguntas_unicas:
                            preguntas_unicas[texto_pregunta] = p
                    
                    print(f"DEBUG: Filtradas {len(preguntas_recibidas) - len(preguntas_unicas)} preguntas duplicadas")
                    
                    # Clasificar preguntas por tipo
                    vf_preguntas = []
                    alt_preguntas = []
                    sm_preguntas = []
                    
                    for p in preguntas_unicas.values():
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
                    
                    # ALGORITMO COMPLETAMENTE NUEVO: Método de fuerza bruta para ordenamiento óptimo
                    # Esta nueva implementación usa un enfoque diferente que garantiza no tener preguntas del mismo tipo consecutivas
                    
                    # Categorizamos las preguntas en tres tipos distintos:
                    preguntas_vf = [p for p in todas_preguntas if p.get("tipo") == "verdadero_falso"]
                    preguntas_alt = [p for p in todas_preguntas if p.get("tipo") in ["alternativas", "opcion_multiple"]]
                    preguntas_sm = [p for p in todas_preguntas if p.get("tipo") == "seleccion_multiple"]
                    
                    print(f"DEBUG: Preguntas disponibles por tipo - V/F: {len(preguntas_vf)}, Alternativas: {len(preguntas_alt)}, Selección múltiple: {len(preguntas_sm)}")
                    
                    # Mezclamos cada grupo por separado para tener variedad
                    random.shuffle(preguntas_vf)
                    random.shuffle(preguntas_alt)
                    random.shuffle(preguntas_sm)
                    
                    # Asegurar que tenemos suficientes preguntas de cada tipo (5 de cada uno)
                    # Si no hay suficientes, duplicamos las existentes
                    while len(preguntas_vf) < 5 and preguntas_vf:
                        preguntas_vf.append(preguntas_vf[0])
                    while len(preguntas_alt) < 5 and preguntas_alt:
                        preguntas_alt.append(preguntas_alt[0])
                    while len(preguntas_sm) < 5 and preguntas_sm:
                        preguntas_sm.append(preguntas_sm[0])
                    
                    # En caso extremo, si falta algún tipo por completo, usar otro tipo
                    if not preguntas_vf:
                        preguntas_vf = (preguntas_alt + preguntas_sm)[:5]
                    if not preguntas_alt:
                        preguntas_alt = (preguntas_vf + preguntas_sm)[:5]
                    if not preguntas_sm:
                        preguntas_sm = (preguntas_vf + preguntas_alt)[:5]
                    
                    # Recortar a exactamente 5 de cada tipo
                    preguntas_vf = preguntas_vf[:5]
                    preguntas_alt = preguntas_alt[:5]
                    preguntas_sm = preguntas_sm[:5]
                    
                    # MÉTODO DE DISTRIBUCIÓN POR POSICIONES ESPECÍFICAS
                    preguntas_distribuidas = [None] * 15  # Inicializamos con None para todas las posiciones
                    print("INFO: Aplicando distribución estratégica para posiciones específicas")
                    
                    # Primero, colocamos las preguntas de selección múltiple en posiciones específicas
                    # Posiciones en 0-indexado: 1, 3, 5, 7, 9 (corresponden a 2, 4, 6, 8, 10 en 1-indexado)
                    posiciones_sm = [1, 3, 5, 7, 9]
                    for i, pos in enumerate(posiciones_sm):
                        if i < len(preguntas_sm):
                            preguntas_distribuidas[pos] = preguntas_sm[i]
                    
                    # Ahora colocamos las preguntas de verdadero/falso y alternativas en el resto de posiciones
                    # Usamos los primeros 5 espacios disponibles para verdadero/falso
                    # y los siguientes 5 para alternativas
                    posiciones_disponibles = [i for i in range(15) if i not in posiciones_sm]
                    
                    # Colocar verdadero/falso en las primeras 5 posiciones disponibles
                    for i in range(min(5, len(preguntas_vf))):
                        if i < len(posiciones_disponibles):
                            preguntas_distribuidas[posiciones_disponibles[i]] = preguntas_vf[i]
                    
                    # Colocar alternativas en las siguientes 5 posiciones disponibles
                    for i in range(min(5, len(preguntas_alt))):
                        if i + 5 < len(posiciones_disponibles):
                            preguntas_distribuidas[posiciones_disponibles[i + 5]] = preguntas_alt[i]
                            
                    # Verificar si hay posiciones vacías (None) y llenarlas con lo que tengamos
                    tipos_restantes = []
                    if len(preguntas_vf) > 5:
                        tipos_restantes.extend(preguntas_vf[5:])
                    if len(preguntas_alt) > 5:
                        tipos_restantes.extend(preguntas_alt[5:])
                    if len(preguntas_sm) > 5:
                        tipos_restantes.extend(preguntas_sm[5:])
                    
                    # Llenar posiciones vacías con preguntas restantes
                    for i in range(15):
                        if preguntas_distribuidas[i] is None:
                            if tipos_restantes:
                                preguntas_distribuidas[i] = tipos_restantes.pop(0)
                            else:
                                # Si no quedan preguntas, duplicar alguna existente
                                print("ADVERTENCIA: Insuficientes preguntas únicas, duplicando existentes")
                                for j in range(15):
                                    if preguntas_distribuidas[j] is not None:
                                        preguntas_distribuidas[i] = preguntas_distribuidas[j]
                                        break
                        
                    # Verificación post-distribución
                    preguntas_por_tipo = {"verdadero_falso": 0, "seleccion_multiple": 0, "alternativas": 0, "opcion_multiple": 0}
                    
                    # Verificar que no hay valores None en preguntas_distribuidas
                    for i, p in enumerate(preguntas_distribuidas):
                        if p is None:
                            print(f"ERROR: La pregunta en posición {i+1} es None. Reemplazando con pregunta dummy.")
                            # Crear una pregunta dummy como último recurso
                            preguntas_distribuidas[i] = {
                                "tipo": "verdadero_falso",
                                "pregunta": f"Pregunta comodín {i+1}",
                                "respuesta": "verdadero",
                                "opciones": ["verdadero", "falso"]
                            }
                    
                    # Contar preguntas por tipo
                    for i, p in enumerate(preguntas_distribuidas):
                        tipo = p.get("tipo")
                        # Verificar que en posiciones 2,4,6,8,10 hay preguntas de selección múltiple
                        if (i+1) in [2, 4, 6, 8, 10] and tipo != "seleccion_multiple":
                            print(f"ADVERTENCIA: En posición {i+1} hay pregunta de tipo {tipo} en lugar de selección múltiple")
                        if tipo in preguntas_por_tipo:
                            preguntas_por_tipo[tipo] += 1
                        
                    print(f"INFO: Distribución final por tipo: {preguntas_por_tipo}")
                    
                    # Verificar presencia de tipos consecutivos
                    tiene_consecutivos = False
                    for i in range(len(preguntas_distribuidas) - 1):
                        tipo_actual = preguntas_distribuidas[i].get("tipo")
                        tipo_siguiente = preguntas_distribuidas[i+1].get("tipo")
                        
                        actual_es_sm = tipo_actual in ["alternativas", "opcion_multiple", "seleccion_multiple"]
                        siguiente_es_sm = tipo_siguiente in ["alternativas", "opcion_multiple", "seleccion_multiple"]
                        
                        if (actual_es_sm and siguiente_es_sm) or (tipo_actual == tipo_siguiente == "verdadero_falso"):
                            print(f"ALERTA: Se detectaron preguntas consecutivas del mismo tipo en posiciones {i+1} y {i+2}")
                            tiene_consecutivos = True
                            
                    if tiene_consecutivos:
                        print("ADVERTENCIA: La distribución aún tiene algunos tipos consecutivos. Aplicando corrección final...")
                        
                        # SOLUCIÓN FINAL: RECONSTRUCCIÓN TOTAL DEL ORDEN
                        print("Aplicando NUEVO algoritmo de reconstrucción total del orden")
                        
                        # Separar preguntas en dos grupos lógicos
                        preguntas_vf = []
                        preguntas_sm = []
                        
                        for p in preguntas_distribuidas:
                            tipo = p.get("tipo")
                            if tipo == "verdadero_falso":
                                preguntas_vf.append(p)
                            else:  # cualquier tipo de selección múltiple
                                preguntas_sm.append(p)
                        
                        # Mezclar cada grupo para mayor variedad
                        random.shuffle(preguntas_vf)
                        random.shuffle(preguntas_sm)
                        
                        # Reconstruir la secuencia completa intercalando los tipos 
                        # lo mejor posible (VF, SM, VF, SM, etc.)
                        nueva_distribucion = []
                        i_vf = 0
                        i_sm = 0
                        
                        # ALGORITMO DE DISTRIBUCIÓN POR POSICIONES ESPECÍFICAS
                        # Este algoritmo garantiza la distribución específica requerida:
                        # - 5 preguntas de selección múltiple (en posiciones 2, 4, 6, 8, 10)
                        # - 5 preguntas de alternativas
                        # - 5 preguntas de verdadero/falso
                        
                        print("NUEVO ALGORITMO: Distribución específica de preguntas...")
                        print(f"- Selección múltiple en posiciones 2, 4, 6, 8, 10")
                        print(f"- Verdadero/Falso: 5 preguntas")
                        print(f"- Alternativas simples: 5 preguntas")
                        
                        # Primero, colocamos las preguntas de selección múltiple en posiciones específicas
                        # Posiciones en 0-indexado: 1, 3, 5, 7, 9 (corresponden a 2, 4, 6, 8, 10 en 1-indexado)
                        posiciones_sm = [1, 3, 5, 7, 9]
                        for i, pos in enumerate(posiciones_sm):
                            if i < len(preguntas_sm):
                                preguntas_distribuidas[pos] = preguntas_sm[i]
                        
                        # Ahora colocamos las preguntas de verdadero/falso y alternativas en el resto de posiciones
                        # Usamos los primeros 5 espacios disponibles para verdadero/falso
                        # y los siguientes 5 para alternativas
                        posiciones_disponibles = [i for i in range(15) if i not in posiciones_sm]
                        
                        # Colocar verdadero/falso en las primeras 5 posiciones disponibles
                        for i in range(min(5, len(preguntas_vf))):
                            if i < len(posiciones_disponibles):
                                preguntas_distribuidas[posiciones_disponibles[i]] = preguntas_vf[i]
                        
                        # Colocar alternativas en las siguientes 5 posiciones disponibles
                        for i in range(min(5, len(preguntas_alt))):
                            if i + 5 < len(posiciones_disponibles):
                                preguntas_distribuidas[posiciones_disponibles[i + 5]] = preguntas_alt[i]
                            
                    # Verificar que tenemos exactamente 15 preguntas
                    if len(preguntas_distribuidas) != 15:
                        print(f"ERROR: La distribución final tiene {len(preguntas_distribuidas)} preguntas en lugar de 15")
                        # Asegurar que siempre tengamos exactamente 15 preguntas
                        if len(preguntas_distribuidas) < 15:
                            # Rellenar con duplicados si faltan
                            while len(preguntas_distribuidas) < 15 and preguntas_distribuidas:
                                preguntas_distribuidas.append(preguntas_distribuidas[0])
                        elif len(preguntas_distribuidas) > 15:
                            # Recortar si hay demasiadas
                            preguntas_distribuidas = preguntas_distribuidas[:15]
                    
                    # Estadísticas finales de distribución
                    total_vf = sum(1 for p in preguntas_distribuidas if p.get("tipo") == "verdadero_falso")
                    total_alt = sum(1 for p in preguntas_distribuidas if p.get("tipo") in ["alternativas", "opcion_multiple"])
                    total_sm = sum(1 for p in preguntas_distribuidas if p.get("tipo") == "seleccion_multiple")
                    print(f"Distribución final: {total_vf} preguntas V/F, {total_alt} preguntas alternativas, {total_sm} preguntas selección múltiple")
                    
                    # Verificar posiciones específicas para selección múltiple
                    posiciones_sm = [1, 3, 5, 7, 9] # 0-indexado (corresponde a 2,4,6,8,10 en 1-indexado)
                    for pos in posiciones_sm:
                        if pos < len(preguntas_distribuidas):
                            tipo = preguntas_distribuidas[pos].get("tipo")
                            if tipo != "seleccion_multiple":
                                print(f"ADVERTENCIA: La posición {pos+1} tiene una pregunta de tipo {tipo} en lugar de selección múltiple")
                    # Asignar las preguntas distribuidas a la evaluación
                    self.eval_preguntas = preguntas_distribuidas[:MAX_QUESTIONS]
                    self.eval_user_answers = {i: "" for i in range(len(self.eval_preguntas))}
                    self.is_eval_active = True
                    self.eval_total_q = len(self.eval_preguntas)
                    self.eval_current_idx = 0
                    print(f"DEBUG: Evaluación activada con {self.eval_total_q} preguntas distribuidas")
                    
                    # Log de la secuencia final de tipos de preguntas
                    tipos_final = [p.get("tipo") for p in self.eval_preguntas]
                    print(f"DEBUG: Secuencia final de tipos de preguntas: {tipos_final}")
                    
                    # Log detallado de cada pregunta con su tipo
                    for i, pregunta in enumerate(self.eval_preguntas):
                        tipo = pregunta.get("tipo")
                        pos_1indexada = i + 1
                        print(f"DEBUG: Pregunta {pos_1indexada} - Tipo: {tipo}")

                    # Asignar las preguntas distribuidas a la evaluación
                    self.eval_preguntas = preguntas_distribuidas[:MAX_QUESTIONS]
                    self.eval_user_answers = {i: "" for i in range(len(self.eval_preguntas))}
                    self.is_eval_active = True
                    self.eval_total_q = len(self.eval_preguntas)
                    self.eval_current_idx = 0
                    print(f"DEBUG: Evaluación activada con {self.eval_total_q} preguntas distribuidas")
            else:
                self.eval_error_message = resultado_logica.get("message", "Error al generar evaluación.")
                print(f"ERROR: {self.eval_error_message}")
        except Exception as e:
            self.eval_error_message = f"Error inesperado: {str(e)}"
            print(f"ERROR: Excepción en generate_evaluation: {e}\n{traceback.format_exc()}")
        finally:
            self.is_generation_in_progress = False
            yield # Mostrar el resultado final

    # Helper methods for score comparisons to avoid direct comparison operators on State vars
    @rx.var
    def get_score_color_tier(self) -> str:
        """Returns the appropriate color based on the score tier.
        
        Returns:
            A string with the CSS color variable.
        """
        score = self.eval_score_rounded
        if score < 40:
            return "var(--red-9)"
        elif score < 60:
            return "var(--orange-9)"
        elif score < 80:
            return "var(--amber-9)"
        elif score < 90:
            return "var(--green-9)"
        else:
            return "var(--teal-9)"
            
    @rx.var
    def get_score_background_color(self) -> str:
        """Returns the appropriate background color based on the score tier.
        
        Returns:
            A string with the CSS color variable.
        """
        score = self.eval_score_rounded
        if score < 40:
            return "var(--red-2)"
        elif score < 60:
            return "var(--orange-2)"
        elif score < 80:
            return "var(--amber-2)"
        elif score < 90:
            return "var(--green-2)"
        else:
            return "var(--teal-2)"
            
    @rx.var
    def get_score_border_color(self) -> str:
        """Returns the appropriate border color based on the score tier.
        
        Returns:
            A string with the CSS color variable.
        """
        score = self.eval_score_rounded
        if score < 40:
            return "var(--red-6)"
        elif score < 60:
            return "var(--orange-6)"
        elif score < 80:
            return "var(--amber-6)"
        elif score < 90:
            return "var(--green-6)"
        else:
            return "var(--teal-6)"
