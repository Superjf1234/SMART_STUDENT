"""
Aplicación SMART_STUDENT - Versión Optimizada y Depurada.

Script principal de la interfaz web con Reflex.
"""

import reflex as rx
import sys, os, datetime, traceback, re  # Imports necesarios
from typing import Dict, List, Optional, Set, Union, Any  # Tipado explícito

# --- Importación de Módulos Backend ---
BACKEND_AVAILABLE = False
try:
    # Asumiendo ejecución desde la raíz del proyecto
    from backend import (
        config_logic,
        db_logic,
        login_logic,
        resumen_logic,
        map_logic,
        eval_logic,
    )

    # Inicializar DB si existe la función
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

    # --- Mocks como Fallback ---
    class MockLogic:
        def __getattr__(self, name):
            def _mock_func(*args, **kwargs):
                print(f"ADVERTENCIA: Usando Mock para '{name}({args=}, {kwargs=})'.")
                mock_data = {  # Datos Mock actualizados
                    "CURSOS": {"Mock Curso": {"Mock Libro": "mock.pdf"}},
                    "verificar_login": lambda u, p: (u == "test" and p == "123")
                    or (u == "felipe" and p == "1234"),
                    "generar_resumen_logica": lambda *a, **kw: {
                        "status": "EXITO",
                        "resumen": "Resumen Mock...",
                        "puntos": "1. Punto Mock 1...\n2. Punto Mock 2...",
                        "message": "Generado con Mock",
                    },
                    "generar_resumen_pdf_bytes": lambda *a, **kw: b"%PDF...",  # PDF Dummy bytes
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

# --- Constantes ---
PRIMARY_COLOR_SCHEME = "blue"
ACCENT_COLOR_SCHEME = "amber"
FONT_FAMILY = "Poppins, sans-serif"
GOOGLE_FONT_STYLESHEET = [
    "https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap"
]


# Add this helper function at the top level, before AppState class
def _curso_sort_key(curso: str) -> tuple:
    """Helper function to sort cursos in correct order."""
    try:
        # Split para obtener el número (1ro, 2do, etc.)
        num_str = curso.split()[0]
        # Eliminar todos los sufijos ordinales conocidos
        sufijos = ["ro", "do", "to", "vo", "mo"]
        for sufijo in sufijos:
            num_str = num_str.replace(sufijo, "")
        # Convertir a número y asignar prioridad por nivel
        num = int(num_str) if num_str.isdigit() else 99
        # Básico = 1, Medio = 2, Otro = 9 (para ordenar)
        nivel = "1" if "Básico" in curso else "2" if "Medio" in curso else "9"
        return (nivel, num)
    except Exception as e:
        print(f"Error en _curso_sort_key para '{curso}': {e}")
        return ("9", 99)  # Valor por defecto para casos problemáticos


# --- Estado Central ---
class AppState(rx.State):
    """Estado central de la aplicación SMART_STUDENT Web."""

    # Autenticación / Usuario
    username_input: str = ""
    password_input: str = ""
    is_logged_in: bool = False
    login_error_message: str = ""
    logged_in_username: str = ""

    # Selección de Contenido
    try:
        _cursos_data = getattr(config_logic, "CURSOS", {})  # Acceso seguro
        cursos_dict: Dict[str, Any] = (
            _cursos_data if isinstance(_cursos_data, dict) else {}
        )
        # Modified sorting using custom sort key
        cursos_list: List[str] = sorted(
            [str(c) for c in cursos_dict.keys() if isinstance(c, str) and c != "Error"],
            key=_curso_sort_key,
        )
    except Exception as e:
        print(f"ERROR Cargando CURSOS al inicializar estado: {e}", file=sys.stderr)
        cursos_dict: Dict[str, Any] = {"Error": {"Carga": "error.pdf"}}
        cursos_list: List[str] = ["Error al Cargar Cursos"]
    selected_curso: str = ""
    selected_libro: str = ""
    selected_tema: str = ""

    # Estados Funcionalidades
    is_generating_resumen: bool = False
    resumen_content: str = ""
    puntos_content: str = ""
    include_puntos: bool = False  # Asegurar que el valor por defecto es False
    is_generating_mapa: bool = False
    mapa_mermaid_code: str = ""
    mapa_image_url: str = ""
    mapa_orientacion_horizontal: bool = (
        True  # Cambiado a True para que la orientación predeterminada sea horizontal
    )
    is_generating_eval: bool = False
    is_eval_active: bool = False
    is_reviewing_eval: bool = False
    eval_preguntas: List[Dict[str, Any]] = []
    eval_current_idx: int = 0
    eval_user_answers: Dict[int, Union[str, Set[str]]] = {}
    eval_score: Optional[float] = None
    eval_correct_count: int = 0
    eval_total_q: int = 0
    is_loading_stats: bool = False
    stats_history: List[Dict[str, Any]] = []
    error_message_ui: str = ""
    active_tab: str = "inicio"

    # --- Computed Vars ---
    @rx.var
    def libros_para_curso(self) -> List[str]:
        """Get list of books for selected course."""
        if not self.selected_curso or self.selected_curso == "Error al Cargar Cursos":
            return []
        try:
            return list(self.cursos_dict.get(self.selected_curso, {}).keys())
        except Exception as e:
            print(f"Error obteniendo libros: {e}")
            return []

    @rx.var
    def current_eval_question(self) -> Optional[Dict[str, Any]]:
        if (
            self.eval_preguntas and 0 <= self.eval_current_idx < self.eval_total_q
        ):  # Usar total_q
            q = self.eval_preguntas[self.eval_current_idx]
            return q if isinstance(q, dict) else None
        return None

    @rx.var
    def is_last_eval_question(self) -> bool:
        return self.eval_total_q > 0 and self.eval_current_idx >= self.eval_total_q - 1

    @rx.var
    def is_first_eval_question(self) -> bool:
        return self.eval_current_idx <= 0

    @rx.var
    def pdf_url(self) -> str:
        """Genera la URL del PDF basada en el curso y libro seleccionados."""
        if not self.selected_curso or not self.selected_libro:
            return ""
        try:
            curso = self.selected_curso.lower().replace(" ", "_")
            archivo = self.cursos_dict[self.selected_curso][self.selected_libro]
            return f"/pdfs/{curso}/{archivo}"
        except Exception as e:
            print(f"ERROR generando URL PDF: {e}")
            return ""

    # --- Event Handlers ---
    def set_active_tab(self, tab: str):
        """Cambia la pestaña activa y reinicia estados."""
        if not isinstance(tab, str):
            return

        # Limpiar las selecciones al cambiar de pestaña
        self.selected_curso = ""
        self.selected_libro = ""
        self.selected_tema = ""
        self.resumen_content = ""  # Limpiar contenido del resumen
        self.puntos_content = ""  # Limpiar puntos clave
        self.include_puntos = False  # Reset a False al cambiar de pestaña
        self.error_message_ui = ""

        # Limpiar estados específicos de mapas
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""

        # Resetear estados de evaluación
        self.is_eval_active = False
        self.is_reviewing_eval = False
        self.eval_preguntas = []
        self.eval_user_answers = {}
        self.eval_score = None
        self.eval_current_idx = 0
        self.eval_correct_count = 0
        self.eval_total_q = 0

        # Resetear estados de generación
        self.is_generating_resumen = False
        self.is_generating_mapa = False
        self.is_generating_eval = False

        # Cambiar pestaña activa
        self.active_tab = tab

        if tab == "perfil":
            return AppState.load_stats
        yield

    def go_to_curso_and_resumen(self, curso: str):
        if not isinstance(curso, str) or not curso:
            return
        self.selected_curso = curso
        self.selected_libro = ""
        self.clear_selection_and_results()
        self.active_tab = "resumen"
        yield

    def handle_login(self):
        self.login_error_message = ""
        self.error_message_ui = ""
        if not self.username_input or not self.password_input:
            self.login_error_message = "Ingresa usuario y contraseña."
            return

        # Permitir usuarios de prueba incluso cuando el backend no está disponible
        if (self.username_input == "felipe" and self.password_input == "1234") or (
            self.username_input == "test" and self.password_input == "123"
        ):
            self.is_logged_in = True
            self.logged_in_username = self.username_input
            self.username_input = self.password_input = ""
            self.active_tab = "inicio"
            yield
            return

        # Verificar si el backend está disponible antes de intentar el login
        if not BACKEND_AVAILABLE:
            self.login_error_message = "El servicio de autenticación no está disponible. Intenta de nuevo más tarde."
            # Mostramos instrucciones para usar cuentas de prueba
            self.login_error_message += (
                " Puede usar las cuentas de prueba: felipe/1234 o test/123."
            )
            yield
            return

        # Verificar si la función de login existe
        if not hasattr(login_logic, "verificar_login") or not callable(
            login_logic.verificar_login
        ):
            self.login_error_message = (
                "Error en el servicio de autenticación. Contacta al administrador."
            )
            yield
            return

        # Intentar verificar el login
        try:
            is_valid = login_logic.verificar_login(
                self.username_input, self.password_input
            )
            if is_valid:
                self.is_logged_in = True
                self.logged_in_username = self.username_input
                self.username_input = self.password_input = ""
                self.active_tab = "inicio"
            else:
                self.login_error_message = "Usuario o contraseña incorrectos."
                self.password_input = ""
        except Exception as e:
            print(f"Error login: {e}")
            self.login_error_message = (
                "Error en el servicio de autenticación. Por favor intenta más tarde."
            )
            self.password_input = ""
        yield

    def logout(self):
        try:
            self.reset()
        except Exception as e:
            print(f"Error logout reset: {e}")
            self.is_logged_in = False
            self.logged_in_username = ""
            self.active_tab = "inicio"
            self.clear_selection_and_results()
            self.login_error_message = ""
            yield

    def clear_selection_and_results(self):
        """Limpia estados relacionados con una selección específica."""
        self.selected_tema = ""
        self.selected_libro = ""
        self.resumen_content = ""
        self.puntos_content = ""
        self.mapa_mermaid_code = ""
        self.mapa_image_url = ""
        self.error_message_ui = ""
        self.is_eval_active = False
        self.is_reviewing_eval = False
        self.eval_preguntas = []
        self.eval_user_answers = {}
        self.eval_score = None
        self.eval_current_idx = 0
        self.eval_correct_count = 0
        self.eval_total_q = 0

        # Recargar lista de cursos si está vacía
        if not self.cursos_list:
            try:
                _cursos_data = getattr(config_logic, "CURSOS", {})
                self.cursos_dict = (
                    _cursos_data if isinstance(_cursos_data, dict) else {}
                )
                self.cursos_list = sorted(
                    [
                        str(c)
                        for c in self.cursos_dict.keys()
                        if isinstance(c, str) and c != "Error"
                    ],
                    key=_curso_sort_key,
                )
            except Exception as e:
                print(f"ERROR Recargando cursos: {e}", file=sys.stderr)
                self.cursos_dict = {"Error": {"Carga": "error.pdf"}}
                self.cursos_list = ["Error al Cargar Cursos"]

    def handle_curso_change(self, new_curso: str):
        """Maneja el cambio de curso seleccionado."""
        self.selected_curso = new_curso
        self.selected_libro = ""  # Reset libro cuando cambia el curso
        self.selected_tema = ""  # Reset tema también
        self.error_message_ui = ""
        yield

    def handle_libro_change(self, new_libro: str):
        """Maneja el cambio de libro seleccionado."""
        self.selected_libro = new_libro
        self.selected_tema = ""  # Reset tema cuando cambia el libro
        self.error_message_ui = ""
        yield

    def handle_libros_curso_change(self, new_curso: str):
        """Maneja el cambio de curso en la pestaña de libros."""
        self.selected_curso = new_curso
        self.selected_libro = ""  # Reset libro cuando cambia el curso
        self.error_message_ui = ""
        yield

    def handle_libros_libro_change(self, new_libro: str):
        """Maneja el cambio de libro en la pestaña de libros."""
        self.selected_libro = new_libro
        self.error_message_ui = ""
        yield

    def set_selected_tema(self, new_tema: str):
        if not isinstance(new_tema, str):
            return
        self.selected_tema = new_tema
        yield

    def set_include_puntos(self, value: bool):
        if not isinstance(value, bool):
            return
        self.include_puntos = value
        yield

    def set_mapa_orientacion(self, value: bool):
        """Cambia la orientación del mapa entre horizontal y vertical."""
        if not isinstance(value, bool):
            return
        self.mapa_orientacion_horizontal = value
        # Limpiar la visualización actual del mapa para obligar a regenerarlo
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        yield

    def clear_map(self):
        """Limpia el mapa actual."""
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        self.error_message_ui = ""
        yield

    async def generate_summary(self):
        if not self.selected_curso or not self.selected_libro or not self.selected_tema:
            self.error_message_ui = "Selecciona curso, libro y tema."
            yield
            return
        if not BACKEND_AVAILABLE:
            self.error_message_ui = "Servicio no disponible."
            yield
            return

        self.is_generating_resumen = True
        self.resumen_content = ""
        self.puntos_content = ""  # Limpiar puntos anteriores
        self.error_message_ui = ""
        self.is_eval_active = False
        self.is_reviewing_eval = False
        self.eval_preguntas = []
        self.eval_user_answers = {}
        self.eval_score = None
        self.eval_current_idx = 0
        self.eval_correct_count = 0
        self.eval_total_q = 0
        yield
        try:
            if not hasattr(resumen_logic, "generar_resumen_logica"):
                raise AttributeError("Falta resumen_logic.generar_resumen_logica")

            result = resumen_logic.generar_resumen_logica(
                self.selected_curso,
                self.selected_libro,
                self.selected_tema.strip(),
                self.include_puntos,  # Respetar el estado del switch
            )

            if isinstance(result, dict) and result.get("status") == "EXITO":
                self.resumen_content = result.get("resumen", "")
                # Mostrar puntos solo si el switch está activado
                if self.include_puntos:
                    puntos = result.get("puntos")
                    self.puntos_content = (
                        puntos if isinstance(puntos, str) and puntos else ""
                    )
                else:
                    self.puntos_content = ""  # Asegurar que no se muestran puntos
            else:
                self.error_message_ui = (
                    result.get("message", "Error resumen.")
                    if isinstance(result, dict)
                    else "Error respuesta."
                )
        except AttributeError as ae:
            self.error_message_ui = f"Error config resumen_logic: {ae}"
            print(f"ERROR: {self.error_message_ui}")
        except Exception as e:
            self.error_message_ui = f"Error crítico resumen: {str(e)}"
            print(f"ERROR G-SUM: {traceback.format_exc()}")
        finally:
            self.is_generating_resumen = False
            yield

    async def generate_map(self):
        """Genera un mapa conceptual para el tema seleccionado."""
        if not self.selected_tema:
            self.error_message_ui = "Ingresa un tema."
            yield
            return
        if not BACKEND_AVAILABLE:
            self.error_message_ui = "Servicio no disponible."
            yield
            return

        self.is_generating_mapa = True
        self.error_message_ui = ""
        self.mapa_image_url = ""
        yield
        try:
            # Verificar que las funciones existan antes de llamarlas
            if not all(
                hasattr(map_logic, fn)
                for fn in [
                    "generar_nodos_localmente",
                    "generar_mermaid_code",
                    "generar_visualizacion_html",
                ]
            ):
                raise AttributeError("Funciones de map_logic faltantes.")

            # La función generar_nodos_localmente retorna un diccionario, debemos extraer los nodos
            resultado_nodos = map_logic.generar_nodos_localmente(
                self.selected_tema.strip()
            )

            # Verificar si el resultado es un diccionario con la estructura esperada
            if (
                not isinstance(resultado_nodos, dict)
                or "status" not in resultado_nodos
                or "nodos" not in resultado_nodos
            ):
                self.error_message_ui = "Formato de nodos inesperado."
                return

            # Verificar si la generación fue exitosa
            if resultado_nodos["status"] != "EXITO":
                self.error_message_ui = resultado_nodos.get(
                    "message", "Error al generar nodos."
                )
                return

            # Extraer los nodos del diccionario
            nodos = resultado_nodos["nodos"]

            if not nodos:
                self.error_message_ui = "No se generaron nodos."
            else:
                # Ahora convertimos los nodos a formato de texto para generar el código Mermaid
                # Primero preparamos una representación textual de los nodos
                estructura_texto = (
                    "- Nodo Central: " + self.selected_tema.strip() + "\n"
                )

                for nodo in nodos:
                    titulo = nodo.get("titulo", "")
                    if titulo:
                        estructura_texto += f"  - Nodo Secundario: {titulo}\n"
                        subnodos = nodo.get("subnodos", [])
                        for subnodo in subnodos:
                            estructura_texto += f"    - Nodo Terciario: {subnodo}\n"

                # CORREGIDO: Invertir la lógica aquí para que coincida con el nombre de la variable
                # Si mapa_orientacion_horizontal es True, usamos LR (horizontal)
                # Si es False, usamos TD (vertical)
                orientacion = "LR" if self.mapa_orientacion_horizontal else "TD"

                # Generar el código Mermaid a partir de la estructura de texto
                mermaid_code, error = map_logic.generar_mermaid_code(
                    estructura_texto, orientacion
                )

                if error or not mermaid_code:
                    self.error_message_ui = error or "Error código mapa."
                else:
                    self.mapa_mermaid_code = mermaid_code
                    html_url = map_logic.generar_visualizacion_html(
                        mermaid_code, self.selected_tema.strip()
                    )
                    if not html_url:
                        self.error_message_ui = "Error visualización."
                    else:
                        self.mapa_image_url = html_url
                        self.active_tab = "mapa"
        except AttributeError as ae:
            self.error_message_ui = f"Error config map_logic: {ae}"
            print(f"ERROR: {self.error_message_ui}")
        except Exception as e:
            self.error_message_ui = f"Error generando mapa: {str(e)}"
            print(f"ERROR G-MAP: {traceback.format_exc()}")
        finally:
            self.is_generating_mapa = False
            if not self.mapa_image_url and not self.error_message_ui:
                self.error_message_ui = "No se generó visualización."
            yield

    async def generate_evaluation(self):
        if not self.selected_curso or not self.selected_libro or not self.selected_tema:
            self.error_message_ui = "Selecciona curso, libro y tema."
            yield
            return
        if not BACKEND_AVAILABLE:
            self.error_message_ui = "Servicio no disponible."
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
        yield

        try:
            if not hasattr(eval_logic, "generar_evaluacion_logica"):
                raise AttributeError("Falta eval_logic.generar_evaluacion_logica")

            # Llamar al backend para generar preguntas basadas en el tema
            result = eval_logic.generar_evaluacion_logica(
                curso=self.selected_curso,
                libro=self.selected_libro,
                tema=self.selected_tema.strip()
            )

            if isinstance(result, dict) and result.get("status") == "EXITO":
                preguntas = result.get("preguntas")
                if isinstance(preguntas, list) and preguntas:
                    self.eval_preguntas = [
                        p for p in preguntas if isinstance(p, dict) and "pregunta" in p
                    ]
                    if not self.eval_preguntas:
                        self.error_message_ui = "Preguntas inválidas."
                        self.is_eval_active = False
                    else:
                        self.eval_total_q = len(self.eval_preguntas)
                        self.is_eval_active = True
                        self.active_tab = "evaluacion"
                else:
                    self.error_message_ui = "No se generaron preguntas."
                    self.is_eval_active = False
            else:
                self.error_message_ui = (
                    result.get("message", "Error evaluación.")
                    if isinstance(result, dict)
                    else "Error respuesta."
                )
        except AttributeError as ae:
            self.error_message_ui = f"Error config eval_logic: {ae}"
            print(f"ERROR: {self.error_message_ui}")
        except Exception as e:
            self.error_message_ui = f"Error crítico evaluación: {str(e)}"
            print(f"ERROR G-EVAL: {traceback.format_exc()}")
        finally:
            self.is_generating_eval = False
            yield

    def set_eval_answer(self, answer_value: Union[str, List[str]]):
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

    def next_eval_question(self):
        if self.eval_preguntas and self.eval_current_idx < self.eval_total_q - 1:
            self.eval_current_idx += 1
            yield

    def prev_eval_question(self):
        if self.eval_current_idx > 0:
            self.eval_current_idx -= 1
            yield

    def calculate_eval_score(self):
        if not self.eval_preguntas:
            self.error_message_ui = "No hay preguntas."
            yield
            return
        try:
            correct = 0
            total = self.eval_total_q
            if total == 0:
                self.error_message_ui = "No hay preguntas válidas."
                yield
                return
            for i, q_dict in enumerate(self.eval_preguntas):
                if not isinstance(q_dict, dict):
                    continue
                u_ans = self.eval_user_answers.get(i)
                c_ans = q_dict.get("respuesta_correcta")
                q_type = q_dict.get("tipo")
                correct_inc = 0
                if (
                    q_type == "opcion_multiple"
                    and isinstance(u_ans, str)
                    and u_ans == c_ans
                ):
                    correct_inc = 1
                elif q_type == "seleccion_multiple":
                    c_set = set(c_ans) if isinstance(c_ans, list) else set()
                    u_set = u_ans if isinstance(u_ans, set) else set()
                    if u_set and c_set and u_set == c_set:
                        correct_inc = 1
                correct += correct_inc
            self.eval_correct_count = correct
            self.eval_score = (correct / total) * 100.0
            self.is_reviewing_eval = True
            self.is_eval_active = False
            self.eval_current_idx = 0
            if (
                self.logged_in_username
                and BACKEND_AVAILABLE
                and hasattr(db_logic, "guardar_resultado_evaluacion")
            ):
                try:
                    db_logic.guardar_resultado_evaluacion(
                        self.logged_in_username,
                        self.selected_curso or "N/A",
                        self.selected_libro or "N/A",
                        self.selected_tema or "N/A",
                        self.eval_score,
                    )
                except Exception as db_e:
                    print(f"Error guardando DB: {db_e}")
        except Exception as calc_e:
            print(f"Error cálculo score: {calc_e}")
            self.error_message_ui = "Error cálculo puntaje."
            self.is_reviewing_eval = False
            self.is_eval_active = True
        yield

    async def load_stats(self):
        if not self.logged_in_username:
            self.stats_history = []
            self.is_loading_stats = False
            yield
            return
        if not BACKEND_AVAILABLE:
            self.error_message_ui = "Servicio no disponible."
            self.is_loading_stats = False
            yield
            return

        self.is_loading_stats = True
        self.stats_history = []
        self.error_message_ui = ""
        yield
        try:
            if not hasattr(db_logic, "obtener_estadisticas_usuario"):
                raise AttributeError("Falta db_logic.obtener_estadisticas_usuario")
            stats_raw = db_logic.obtener_estadisticas_usuario(self.logged_in_username)
            if isinstance(stats_raw, list):
                self.stats_history = [
                    {
                        "tema": s.get("tema", "N/A"),
                        "curso": s.get("curso", "N/A"),
                        "libro": s.get("libro", "N/A"),
                        "puntuacion": (
                            float(s.get("puntuacion", 0.0))
                            if s.get("puntuacion") is not None
                            else 0.0
                        ),
                        "fecha": s.get("fecha", "N/A"),
                    }
                    for s in stats_raw
                    if isinstance(s, dict)
                ]
            else:
                print(f"WARN: Stats inesperados: {type(stats_raw)}")
                self.stats_history = []
                self.error_message_ui = "Error datos historial."
        except AttributeError as ae:
            self.error_message_ui = f"Error config db_logic: {ae}"
            print(f"ERROR: {self.error_message_ui}")
        except Exception as e:
            print(f"Error cargando stats: {e}")
            self.error_message_ui = "No se pudo cargar historial."
            self.stats_history = []
        finally:
            self.is_loading_stats = False
            yield

    async def download_pdf(self):
        if not self.resumen_content:
            self.error_message_ui = "No hay resumen."
            yield
            return

        try:
            if not hasattr(resumen_logic, "generar_resumen_pdf_bytes"):
                raise AttributeError("Falta resumen_logic.generar_resumen_pdf_bytes")

            # Sanitizar nombre de archivo
            s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "t")
            s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "l")
            s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "c")

            # Verificar si FPDF está disponible intentando generar el PDF
            try:
                pdf_bytes = resumen_logic.generar_resumen_pdf_bytes(
                    resumen_txt=self.resumen_content,
                    puntos_txt=self.puntos_content if self.include_puntos else "",
                    titulo=f"Resumen: {self.selected_tema or 'General'}",
                    subtitulo=f"Curso: {self.selected_curso or 'N/A'} - Libro: {self.selected_libro or 'N/A'}",
                )

                if isinstance(pdf_bytes, bytes) and pdf_bytes:
                    fname = f"Resumen_{s_cur}_{s_lib}_{s_tema}.pdf".replace(" ", "_")[
                        :100
                    ]
                    yield rx.download(data=pdf_bytes, filename=fname)
                    return
                else:
                    print("PDF bytes inválidos. Intentando alternativa HTML...")
                    # Continuar hacia el fallback HTML
            except Exception as pdf_e:
                print(f"Error en generación de PDF, usando fallback HTML: {pdf_e}")
                # Continuar hacia el fallback HTML

            # Fallback: Generar HTML si PDF falla
            html_content = f"""<!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Resumen: {s_tema}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2c5282; }}
                    h2 {{ color: #2b6cb0; margin-top: 20px; }}
                    .content {{ margin-top: 20px; }}
                    .footer {{ margin-top: 30px; font-size: 0.8em; color: #718096; }}
                </style>
            </head>
            <body>
                <h1>Resumen: {self.selected_tema or 'General'}</h1>
                <h2>Curso: {self.selected_curso or 'N/A'} - Libro: {self.selected_libro or 'N/A'}</h2>
                <div class="content">
                    <h3>Resumen:</h3>
                    <div>{self.resumen_content.replace('\n', '<br>')}</div>
                </div>
                {f'<div class="content"><h3>Puntos Clave:</h3><div>{self.puntos_content.replace("\\n", "<br>")}</div></div>' if self.include_puntos and self.puntos_content else ''}
                <div class="footer">Generado por SMART_STUDENT {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            </body>
            </html>"""

            fname = f"Resumen_{s_cur}_{s_lib}_{s_tema}.html".replace(" ", "_")[:100]
            yield rx.download(data=html_content.encode("utf-8"), filename=fname)
            print(f"Descargado resumen como HTML: {fname}")

        except Exception as e:
            self.error_message_ui = f"Error descarga: {str(e)}"
            print(f"ERROR DWNLD PDF/HTML: {traceback.format_exc()}")
            yield

    async def download_map_pdf(self):
        """Descarga el mapa conceptual actual en formato PDF."""
        if not self.mapa_image_url:
            self.error_message_ui = "No hay mapa para descargar."
            yield
            return

        try:
            # Sanitizar nombre de archivo
            s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "tema")
            s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "libro")
            s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "curso")

            # Verificar que existe la función de generación de PDF
            if hasattr(map_logic, "generar_mapa_pdf_bytes"):
                try:
                    # Llamar directamente al PDF sin fallback a HTML
                    pdf_bytes = map_logic.generar_mapa_pdf_bytes(
                        mermaid_code=self.mapa_mermaid_code,
                        tema=self.selected_tema,
                        curso=self.selected_curso,
                        libro=self.selected_libro,
                        html_url=self.mapa_image_url,
                    )

                    if isinstance(pdf_bytes, bytes) and pdf_bytes:
                        fname = f"Mapa_{s_cur}_{s_lib}_{s_tema}.pdf".replace(" ", "_")[
                            :100
                        ]
                        yield rx.download(data=pdf_bytes, filename=fname)
                        return
                    else:
                        self.error_message_ui = (
                            "Error al generar PDF del mapa conceptual."
                        )
                        print("ERROR: PDF bytes inválidos para el mapa")
                except Exception as e:
                    self.error_message_ui = f"Error al generar PDF: {str(e)}"
                    print(f"ERROR con map_logic.generar_mapa_pdf_bytes: {e}")
            else:
                self.error_message_ui = (
                    "La función para generar PDF no está disponible."
                )
                print("ERROR: Función generar_mapa_pdf_bytes no encontrada")

        except Exception as e:
            self.error_message_ui = f"Error descarga: {str(e)}"
            print(f"ERROR DWNLD MAP PDF: {traceback.format_exc()}")
            yield


# --- Funciones Helper para UI ---
def create_card(
    title, icon, description, action_text, on_click, color_scheme=PRIMARY_COLOR_SCHEME
):
    return rx.card(
        rx.vstack(
            rx.icon(icon, size=48, color=f"var(--{color_scheme}-9)"),
            rx.heading(title, size="5", mt="0.7em", text_align="center", flex_grow=0),
            rx.text(
                description,
                text_align="center",
                size="3",
                color_scheme="gray",
                flex_grow=1,
            ),
            # Espacio adicional entre el texto y el botón
            rx.spacer(height="0.75em"),  # Reducido de 1.5em a 0.75em (la mitad)
            # Centrar el botón horizontalmente en la tarjeta
            rx.box(
                rx.button(
                    action_text,
                    on_click=on_click,
                    size="3",
                    variant="soft",
                    color_scheme=color_scheme,
                    width="200px",  # Ancho fijo para el botón
                ),
                width="100%",
                display="flex",
                justify_content="center",  # Centrar el botón horizontalmente
            ),
            align="center",
            justify="between",
            p="2em",
            spacing="4",
            h="100%",
        ),
        variant="surface",
        size="3",
        h="500px",
        w="2500px",
        as_child=True,
    )


def error_callout(message: rx.Var[str]):
    return rx.cond(
        message != "",
        rx.callout.root(
            rx.callout.icon(
                rx.icon("triangle-alert")
            ),  # Changed from alert-triangle to triangle-alert
            rx.callout.text(message),
            color_scheme="red",
            role="alert",
            w="100%",
            my="1em",
            size="2",
        ),
    )


def nav_button(text: str, tab_name: str, active_tab: rx.Var[str]):
    return rx.button(
        text,
        on_click=lambda: AppState.set_active_tab(tab_name),
        variant=rx.cond(active_tab == tab_name, "solid", "ghost"),
        color_scheme=rx.cond(active_tab == tab_name, PRIMARY_COLOR_SCHEME, "gray"),
        size="2",
    )


# --- Definición de Páginas/Pestañas ---


def login_page():
    """Página de inicio de sesión."""
    return rx.center(
        rx.vstack(
            # Logo y Título
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
                    align_items="center",  # Cambiado de "start" a "center"
                ),
                spacing="3",
                align_items="center",
                justify="center",  # Cambiado de "start" a "center"
                margin_bottom="1em",
                width="100%",
            ),
            # Formulario de Login dentro de una Card
            rx.card(
                rx.form(  # Usar rx.form para semántica y posible manejo de submit
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
                            AppState.login_error_message
                            != "",  # Mostrar error de login
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
                            width="100%",  # type="submit"
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
                    reset_on_submit=False,  # No resetear campos si falla
                ),
                width="400px",
                max_width="90%",
            ),  # Fin Card
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
    return rx.vstack(
        # Título y subtítulo centrados
        rx.center(
            rx.vstack(
                # Añadir espacio superior de 0.5em antes del título
                rx.spacer(height="0.5em"),
                rx.heading(
                    "Bienvenido a SMART_STUDENT",
                    size="7",
                    mb="0.5em",
                    text_align="center",
                ),
                rx.text(
                    "Tu asistente de estudio inteligente potenciado por IA.",
                    mb="0.5em",
                    size="4",
                    color_scheme="gray",
                    text_align="center",
                ),
                width="100%",
                align_items="center",
                mt="1em",
            )
        ),
        # Contenedor centrado para las tarjetas
        rx.center(
            rx.box(
                rx.vstack(
                    rx.grid(
                        create_card(
                            "Libros",
                            "book",
                            "Accede a tus libros digitales.",
                            "Ver Libros",
                            lambda: AppState.set_active_tab("libros"),
                            "green",
                        ),
                        create_card(
                            "Resúmenes",
                            "file-text",
                            "Genera resúmenes y puntos clave.",
                            "Crear Resumen",
                            lambda: AppState.set_active_tab("resumen"),
                            PRIMARY_COLOR_SCHEME,
                        ),
                        create_card(
                            "Mapas Conceptuales",
                            "git-branch",
                            "Explora ideas y conexiones.",
                            "Crear Mapa",
                            lambda: AppState.set_active_tab("mapa"),
                            ACCENT_COLOR_SCHEME,
                        ),
                        create_card(
                            "Evaluaciones",
                            "clipboard-check",
                            "Pon a prueba tu conocimiento.",
                            "Evaluar",
                            lambda: AppState.set_active_tab("evaluacion"),
                            "purple",  # Cambiado de "green" a "purple" para dar un color distintivo
                        ),
                        columns="2",  # Dos columnas para mostrar 2 tarjetas por fila
                        spacing="4",
                        width="100%",
                        max_width="1600px",  # Ancho máximo del grid
                    ),
                    width="100%",
                    align_items="center",
                    spacing="4",
                ),
                width="100%",
                overflow_x="auto",
                padding="1em",
            )
        ),
        # Recursos Populares centrados - Ajustado el ancho para que coincida con las tarjetas
        rx.center(
            rx.card(
                rx.vstack(
                    rx.heading(
                        "Recursos Populares", size="4", mb="1em", text_align="center"
                    ),
                    rx.hstack(
                        rx.foreach(
                            ["Matemáticas", "Ciencias", "Historia", "Lenguaje"],
                            lambda c: rx.cond(
                                AppState.cursos_list.contains(c),
                                rx.button(
                                    c,
                                    on_click=lambda curso=c: AppState.go_to_curso_and_resumen(
                                        curso
                                    ),
                                    variant="soft",
                                    color_scheme="gray",
                                    size="2",
                                ),
                                rx.fragment(),
                            ),
                        ),
                        spacing="3",
                        justify="center",  # Centrar los botones
                        wrap="wrap",
                    ),
                    p="1.5em",
                    width="100%",
                    align="center",  # Alinear todo al centro
                ),
                mt="2.5em",
                variant="surface",
                width="100%",  # Cambiado de 80% a 100% para consistencia con las tarjetas superiores
                max_width="1600px",  # Ajustado para coincidir con el grid de tarjetas
            )
        ),
        width="100%",
        m="0 auto",
        p="2em",
        spacing="5",
        align_items="center",
    )


def resumen_tab():
    """Contenido de la pestaña de resumen."""
    return rx.center(  # Envolvemos todo en un centro para alineación horizontal
        rx.flex(  # Usamos flex para centrado vertical similar a la pestaña de libros
            rx.vstack(
                # Espacio adicional para separar del menú
                rx.spacer(
                    height="60em"
                ),  # Incrementado el espaciador para bajar todo el contenido unos 30 cm más
                # Título centrado
                rx.heading(
                    "🎯 Turbo Aprendizaje", size="6", mb="2em", text_align="center"
                ),
                # Mostrar error si existe
                error_callout(AppState.error_message_ui),
                # Contenedor de selección con ancho fijo
                rx.vstack(
                    # Selectores con el mismo ancho que en libros_tab
                    rx.box(
                        rx.grid(
                            rx.select(
                                AppState.cursos_list,
                                placeholder="Selecciona un Curso...",
                                on_change=AppState.handle_curso_change,
                                value=AppState.selected_curso,
                                size="3",
                                variant="soft",
                                color_scheme=PRIMARY_COLOR_SCHEME,
                                w="100%",
                            ),
                            rx.select(
                                AppState.libros_para_curso,
                                placeholder="Selecciona un Libro...",
                                on_change=AppState.handle_libro_change,
                                value=AppState.selected_libro,
                                size="3",
                                variant="soft",
                                color_scheme=PRIMARY_COLOR_SCHEME,
                                w="100%",
                                is_disabled=rx.cond(
                                    (AppState.selected_curso == "")
                                    | (
                                        AppState.selected_curso
                                        == "Error al Cargar Cursos"
                                    ),
                                    True,
                                    False,
                                ),
                            ),
                            # Tema específico como área de texto
                            rx.text_area(
                                placeholder="Tema específico...",
                                on_change=AppState.set_selected_tema,
                                value=AppState.selected_tema,
                                size="3",
                                min_h="6em",
                                w="100%",
                                is_disabled=rx.cond(
                                    AppState.selected_libro == "", True, False
                                ),
                            ),
                            # Una fila por elemento
                            columns="1",
                            spacing="4",
                            w="100%",
                        ),
                        width="100%",
                        max_width="400px",  # Mismo ancho máximo que en libros_tab
                    ),
                    # Fila de opciones y botón
                    rx.box(
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
                                rx.text("Puntos Relevantes", size="2", ml="0.5em"),
                                spacing="2",
                                align_items="center",
                            ),
                            rx.spacer(),
                            rx.button(
                                rx.cond(
                                    AppState.is_generating_resumen,
                                    rx.hstack(rx.spinner(size="2"), "Generando..."),
                                    "Generar Resumen",
                                ),
                                on_click=AppState.generate_summary,
                                size="3",
                                color_scheme=PRIMARY_COLOR_SCHEME,
                                is_disabled=rx.cond(
                                    AppState.is_generating_resumen
                                    | (AppState.selected_tema == ""),
                                    True,
                                    False,
                                ),
                            ),
                            width="100%",
                            align_items="center",
                            mt="1em",
                        ),
                        width="100%",
                        max_width="400px",  # Mismo ancho máximo que en libros_tab
                    ),
                    width="100%",
                    align_items="center",
                    spacing="4",
                ),
                # Resultados
                rx.cond(
                    (AppState.resumen_content != "") | (AppState.puntos_content != ""),
                    rx.vstack(
                        rx.grid(
                            rx.cond(
                                AppState.resumen_content != "",
                                rx.box(
                                    rx.heading(
                                        "Resumen",
                                        size="4",
                                        mb="0.5em",
                                        text_align="center",
                                    ),
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
                                ),
                            ),
                            rx.cond(
                                AppState.include_puntos
                                & (AppState.puntos_content != ""),
                                rx.box(
                                    rx.heading(
                                        "Puntos",
                                        size="4",
                                        mb="0.5em",
                                        text_align="center",
                                    ),
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
                                ),
                            ),
                            columns=rx.cond(
                                (AppState.resumen_content != "")
                                & AppState.include_puntos
                                & (AppState.puntos_content != ""),
                                "1fr 1fr",
                                "1fr",
                            ),
                            spacing="5",
                            width="100%",
                            mt="1.5em",
                            mb="1.5em",
                        ),
                        rx.hstack(  # Botones de acción
                            rx.button(
                                rx.icon("download", mr="0.2em"),
                                "PDF",
                                on_click=AppState.download_pdf,
                                variant="soft",
                                size="2",
                                color_scheme=PRIMARY_COLOR_SCHEME,
                                is_disabled=rx.cond(
                                    AppState.resumen_content == "", True, False
                                ),
                            ),
                            rx.button(
                                rx.icon("git-branch", mr="0.2em"),
                                "Mapa",
                                on_click=AppState.generate_map,
                                variant="soft",
                                size="2",
                                color_scheme=ACCENT_COLOR_SCHEME,
                                is_disabled=rx.cond(
                                    AppState.is_generating_mapa
                                    | (AppState.selected_tema == ""),
                                    True,
                                    False,
                                ),
                            ),
                            rx.button(
                                rx.icon("clipboard-check", mr="0.2em"),
                                "Evaluar",
                                on_click=AppState.generate_evaluation,
                                variant="soft",
                                size="2",
                                color_scheme="green",
                                is_disabled=rx.cond(
                                    AppState.is_generating_eval
                                    | (AppState.resumen_content == ""),
                                    True,
                                    False,
                                ),
                            ),
                            justify="center",
                            spacing="4",
                            mt="1em",
                            width="100%",
                        ),
                        width="100%",
                        align="center",
                    ),
                ),
                spacing="4",
                width="100%",
                max_width="1000px",
                p="2em",
                align_items="center",
            ),
            # Propiedades para centrar verticalmente, iniciando desde el primer tercio de la pantalla
            direction="column",
            align_items="center",
            min_h="calc(100vh - 200px)",
            justify_content="flex-start",
            width="100%",
        ),
        width="100%",
    )


def mapa_tab():
    """Contenido de la pestaña de mapa conceptual."""
    return rx.center(  # Envolver en centro para alineación horizontal, igual que en resumen_tab
        rx.flex(  # Usar flex para centrado vertical, igual que en resumen_tab
            rx.vstack(
                # Espacio adicional para separar del menú, igual que en resumen_tab
                rx.spacer(height="60em"),
                # Título centrado con un nombre más divertido y novedoso
                rx.heading(
                    "🧠 Explorando Conexiones Mentales",
                    size="6",
                    mb="2em",
                    text_align="center",
                ),
                # Mostrar error si existe
                error_callout(AppState.error_message_ui),
                # Contenedor de selección con ancho fijo, igual que en resumen_tab
                rx.vstack(
                    rx.box(
                        rx.grid(
                            rx.select(
                                AppState.cursos_list,
                                placeholder="Selecciona un Curso...",
                                on_change=AppState.handle_curso_change,
                                value=AppState.selected_curso,
                                size="3",
                                variant="soft",
                                color_scheme=PRIMARY_COLOR_SCHEME,
                                w="100%",
                            ),
                            rx.select(
                                AppState.libros_para_curso,
                                placeholder="Selecciona un Libro...",
                                on_change=AppState.handle_libro_change,
                                value=AppState.selected_libro,
                                size="3",
                                variant="soft",
                                color_scheme=PRIMARY_COLOR_SCHEME,
                                w="100%",
                                is_disabled=rx.cond(
                                    (AppState.selected_curso == "")
                                    | (
                                        AppState.selected_curso
                                        == "Error al Cargar Cursos"
                                    ),
                                    True,
                                    False,
                                ),
                            ),
                            columns="1",
                            spacing="4",
                            w="100%",
                        ),
                        width="100%",
                        max_width="400px",  # Mismo ancho máximo que en resumen_tab
                    ),
                    rx.box(
                        rx.text_area(
                            placeholder="Tema central...",
                            on_change=AppState.set_selected_tema,
                            value=AppState.selected_tema,
                            size="3",
                            min_h="6em",
                            w="100%",
                        ),
                        width="100%",
                        max_width="400px",  # Mismo ancho máximo que en resumen_tab
                    ),
                    # Opciones para el mapa - agregamos el switch para orientación
                    rx.box(
                        rx.hstack(
                            rx.hstack(
                                rx.switch(
                                    is_checked=AppState.mapa_orientacion_horizontal,
                                    on_change=AppState.set_mapa_orientacion,
                                    size="2",
                                    color_scheme=ACCENT_COLOR_SCHEME,
                                ),
                                rx.text("Orientación Vertical", size="2", ml="0.5em"),
                                spacing="2",
                                align_items="center",
                            ),
                            rx.spacer(),
                            width="100%",
                            align_items="center",
                        ),
                        width="100%",
                        max_width="400px",
                    ),
                    rx.box(
                        rx.button(
                            rx.cond(
                                AppState.is_generating_mapa,
                                rx.hstack(rx.spinner(size="2"), "Generando..."),
                                "Generar Mapa",
                            ),
                            on_click=AppState.generate_map,
                            size="3",
                            color_scheme=PRIMARY_COLOR_SCHEME,
                            is_disabled=rx.cond(
                                AppState.is_generating_mapa
                                | (AppState.selected_tema == ""),
                                True,
                                False,
                            ),
                            width="100%",
                        ),
                        width="100%",
                        max_width="400px",  # Mismo ancho máximo que en resumen_tab
                        mt="1em",
                    ),
                    width="100%",
                    align_items="center",
                    spacing="4",
                ),
                # Resultados
                rx.cond(
                    AppState.mapa_image_url != "",
                    rx.vstack(
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
                        # Agregar espacio adicional antes del botón
                        rx.spacer(height="1.5em"),
                        rx.hstack(
                            rx.button(
                                rx.icon("download", mr="0.2em"),
                                "PDF",
                                on_click=AppState.download_map_pdf,
                                variant="soft",
                                size="2",
                                color_scheme=PRIMARY_COLOR_SCHEME,
                                is_disabled=rx.cond(
                                    AppState.mapa_image_url == "", True, False
                                ),
                            ),
                            justify="center",
                            spacing="4",
                            width="100%",
                        ),
                        width="100%",
                        spacing="2",
                        align="center",
                    ),
                ),
                spacing="4",
                width="100%",
                max_width="1000px",
                p="2em",
                align_items="center",
            ),
            # Propiedades para centrar verticalmente, igual que en resumen_tab
            direction="column",
            align_items="center",
            min_h="calc(100vh - 200px)",
            justify_content="flex-start",
            width="100%",
        ),
        width="100%",
    )


def evaluacion_tab():
    """Contenido de la pestaña de evaluaciones."""
    return rx.center(
        rx.flex(
            rx.vstack(
                # Espacio adicional para separar del menú
                rx.spacer(height="60em"),
                # Título centrado con un nombre más divertido y novedoso
                rx.heading(
                    "📝 Desafía tu Conocimiento", size="6", mb="2em", text_align="center"
                ),
                # Mostrar error si existe
                error_callout(AppState.error_message_ui),
                # Contenedor de selección con ancho fijo
                rx.vstack(
                    rx.box(
                        rx.grid(
                            rx.select(
                                AppState.cursos_list,
                                placeholder="Selecciona un Curso...",
                                on_change=AppState.handle_curso_change,
                                value=AppState.selected_curso,
                                size="3",
                                variant="soft",
                                color_scheme=PRIMARY_COLOR_SCHEME,
                                w="100%",
                            ),
                            rx.select(
                                AppState.libros_para_curso,
                                placeholder="Selecciona un Libro...",
                                on_change=AppState.handle_libro_change,
                                value=AppState.selected_libro,
                                size="3",
                                variant="soft",
                                color_scheme=PRIMARY_COLOR_SCHEME,
                                w="100%",
                                is_disabled=rx.cond(
                                    (AppState.selected_curso == "")
                                    | (
                                        AppState.selected_curso
                                        == "Error al Cargar Cursos"
                                    ),
                                    True,
                                    False,
                                ),
                            ),
                            columns="1",
                            spacing="4",
                            w="100%",
                        ),
                        width="100%",
                        max_width="400px",
                    ),
                    rx.box(
                        rx.text_area(
                            placeholder="Tema a evaluar...",
                            on_change=AppState.set_selected_tema,
                            value=AppState.selected_tema,
                            size="3",
                            min_h="6em",
                            w="100%",
                        ),
                        width="100%",
                        max_width="400px",
                    ),
                    rx.box(
                        rx.button(
                            rx.cond(
                                AppState.is_generating_eval,
                                rx.hstack(rx.spinner(size="2"), "Generando..."),
                                "Crear Evaluación",
                            ),
                            on_click=AppState.generate_evaluation,
                            size="3",
                            color_scheme=PRIMARY_COLOR_SCHEME,
                            is_disabled=rx.cond(
                                AppState.is_generating_eval
                                | (AppState.selected_tema == ""),
                                True,
                                False,
                            ),
                            width="100%",
                        ),
                        width="100%",
                        max_width="400px",
                        mt="1em",
                    ),
                    width="100%",
                    align_items="center",
                    spacing="4",
                ),
                spacing="4",
                width="100%",
                max_width="1000px",
                p="2em",
                align_items="center",
            ),
            direction="column",
            align_items="center",
            min_h="calc(100vh - 200px)",
            justify_content="flex-start",
            width="100%",
        ),
        width="100%",
    )


def perfil_tab():
    """Contenido de la pestaña de perfil y estadísticas."""
    return rx.vstack(
        rx.heading("Perfil y Progreso", size="6", mb="1.5em", text_align="center"),
        rx.grid(
            # ... existing code ...
        ),
        rx.card(
            # ... existing code ...
        ),
        w="100%",
        max_width="1000px",
        margin="0 auto",
        p="2em",
        spacing="5",
    )


def ayuda_tab():
    """Contenido de la pestaña de ayuda."""
    # Definir contenido aquí para evitar que sea muy largo
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
    """Contenido de la pestaña de libros."""
    return rx.box(
        rx.vstack(
            # Contenido principal directamente sin el flex intermediario
            rx.heading(
                "📚 Biblioteca Digital", size="7", mb="1em", text_align="center"
            ),
            rx.text(
                "¡Embárcate en una aventura de conocimiento con solo un clic!",
                color="gray.500",
                mb="1.5em",
                text_align="center",
                font_size="lg",
            ),
            error_callout(AppState.error_message_ui),
            # Contenedor principal de selección
            rx.box(
                rx.grid(
                    # Primer selector: Curso
                    rx.select(
                        AppState.cursos_list,
                        placeholder="Selecciona un Curso...",
                        on_change=AppState.handle_libros_curso_change,
                        value=AppState.selected_curso,
                        size="3",
                        variant="soft",
                        color_scheme=PRIMARY_COLOR_SCHEME,
                        w="100%",
                    ),
                    # Segundo selector: Libro
                    rx.select(
                        AppState.libros_para_curso,
                        placeholder="Selecciona un Libro...",
                        on_change=AppState.handle_libros_libro_change,
                        value=AppState.selected_libro,
                        size="3",
                        variant="soft",
                        color_scheme=PRIMARY_COLOR_SCHEME,
                        w="100%",
                        is_disabled=rx.cond(
                            (AppState.selected_curso == "")
                            | (AppState.selected_curso == "Error al Cargar Cursos"),
                            True,
                            False,
                        ),
                    ),
                    columns="1",
                    spacing="3",  # Reducido de 4 a 3
                    w="100%",
                ),
                width="100%",
                max_width="400px",
            ),
            # Botón de descarga con tamaño fijo
            rx.box(
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
                    ),
                ),
                width="100%",
                max_width="400px",
            ),
            spacing="3",
            width="100%",
            max_width="600px",
            p="1.5em",
            align_items="center",
            # Propiedades para centrar todo el contenido en la página
            margin="0 auto",
            margin_top="9em",  # Aumentado de 4em a 5.5em para bajar un poco más el título
            min_height="calc(100vh - 150px)",
            justify_content="flex-start",  # Alinear al inicio para que esté arriba
        ),
        width="100%",
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
                    on_click=AppState.logout,
                    color_scheme="red",
                    variant="soft",
                    size="2",
                ),
                content="Cerrar Sesión",
            ),
            p="1.5em 2em 1.5em 2em",
            w="100%",
            bg="var(--gray-1)",
            border_bottom="1px solid var(--gray-4)",
            position="sticky",
            top="0",
            z_index="10",
            align_items="center",
            justify="start",
            mb="0.5em",
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
                size="2",
                w="100%",
                justify="center",
                border_bottom="1px solid var(--gray-6)",
            ),
            rx.tabs.content(inicio_tab(), value="inicio"),
            rx.tabs.content(libros_tab(), value="libros"),
            rx.tabs.content(resumen_tab(), value="resumen"),
            rx.tabs.content(mapa_tab(), value="mapa"),
            rx.tabs.content(evaluacion_tab(), value="evaluacion"),
            rx.tabs.content(perfil_tab(), value="perfil"),
            rx.tabs.content(ayuda_tab(), value="ayuda"),
            value=AppState.active_tab,
            w="100%",
            h="calc(100vh - 60px)",
        ),
        w="100%",
        h="100vh",
        spacing="0",
        align_items="stretch",
    )


# --- Definición y Configuración de la App ---
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
rx.Config.title = (
    "Smart Student | Aprende, Crea y Destaca"  # Configurar el título de la aplicación
)
rx.Config.favicon = "/favicon.ico"  # Configurar el favicon correctamente


# --- Página Principal ---
@app.add_page
def index() -> rx.Component:
    """Página principal: renderiza login o dashboard."""
    return rx.fragment(
        rx.script(
            "document.title = 'Smart Student | Aprende, Crea y Destaca'"
        ),  # También actualizar aquí para consistencia
        rx.html('<link rel="icon" type="image/x-icon" href="/smartstudent_icon.ico">'),
        rx.cond(AppState.is_logged_in, main_dashboard(), login_page()),
    )


# FIN DEL SCRIPT - Asegúrate que no haya código extra después de esto.
