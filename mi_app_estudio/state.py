# Archivo: mi_app_estudio/state.py
# ¡VERSIÓN COMPLETA FINAL Y VERIFICADA!

"""
Módulo de estado base para SMART_STUDENT.
Contiene la definición de AppState que es usada por otros módulos.
"""

import reflex as rx
import sys, os, datetime, traceback, re
from typing import Dict, List, Optional, Set, Union, Any
import random

# --- IMPORTACIONES EXTERNAS Y BACKEND ---
# ¡NO DEBE HABER importaciones de .evaluaciones ni de .state aquí!
BACKEND_AVAILABLE = False
try:
    # Asume que la carpeta 'backend' está en la raíz del proyecto
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

    # --- Mock Logic (Solo si el backend falla) ---
    class MockLogic:
        def __getattr__(self, name):
            def _mock_func(*args, **kwargs):
                print(f"ADVERTENCIA: Usando Mock para '{name}({args=}, {kwargs=})'.")
                mock_data = {
                    "CURSOS": {"Mock Curso": {"Mock Libro": "mock.pdf"}},
                    "verificar_login": lambda u, p: (u == "test" and p == "123") or (u == "felipe" and p == "1234"),
                    "generar_resumen_logica": lambda *a, **kw: {"status": "EXITO", "resumen": "Resumen Mock...", "puntos": "1. Punto Mock...", "message": "Generado con Mock"},
                    "generar_resumen_pdf_bytes": lambda *a, **kw: b"%PDF...",
                    "generar_nodos_localmente": lambda *a, **kw: {"status": "EXITO", "nodos": [{"titulo": "Nodo Central", "subnodos": ["Subnodo A", "Subnodo B"]}, {"titulo": "Otro Nodo"}]},
                    "generar_mermaid_code": lambda *a, **kw: ("graph TD A[Centro]-->B(Nodo 1);...", None),
                    "generar_visualizacion_html": lambda *a, **kw: "data:text/html,<html><body>Mock</body></html>",
                    "generar_evaluacion": lambda curso, libro, tema: {
                        "status": "EXITO",
                        "preguntas": [
                            {
                                "pregunta": f"Pregunta {i+1}: ¿Es esto correcto?",
                                "tipo": "verdadero_falso",
                                "opciones": [
                                    {"letra": "Verdadero", "texto": "Verdadero"},
                                    {"letra": "Falso", "texto": "Falso"}
                                ],
                                "respuesta_correcta": random.choice(["Verdadero", "Falso"]),
                                "explicacion": f"Respuesta para la pregunta {i+1}."
                            } if (i % 3 == 0) else {
                                "pregunta": f"Pregunta {i+1}: Selecciona la opción correcta.",
                                "tipo": "alternativas",
                                "opciones": [
                                    {"letra": "a", "texto": "Opción A"},
                                    {"letra": "b", "texto": "Opción B"},
                                    {"letra": "c", "texto": "Opción C"}
                                ],
                                "respuesta_correcta": random.choice(["a", "b", "c"]),
                                "explicacion": f"Respuesta para la pregunta {i+1}."
                            }
                            for i in range(15)  # Generar 15 preguntas
                        ]
                    },
                    "obtener_estadisticas_usuario": lambda *a, **kw: [{"curso": "Mock C", "libro": "Mock L", "tema": "Mock T", "puntuacion": 85.0, "fecha": "Hoy"}],
                    "guardar_resultado_evaluacion": lambda *a, **kw: print("Mock: Guardando resultado..."),
                }
                return (
                    mock_data.get(name, lambda *a, **kw: None)(*args, **kwargs)
                    if callable(mock_data.get(name))
                    else mock_data.get(name)
                )
            return _mock_func
    # --- Fin Mock Logic ---

    config_logic = login_logic = db_logic = resumen_logic = map_logic = eval_logic = MockLogic()
    print("ADVERTENCIA: Usando Mocks para la lógica del backend.", file=sys.stderr)
# --- FIN IMPORTACIONES ---


# --- IMPORTACIONES DE SUB-ESTADOS ---
# Importar CuestionarioState para poder obtener su instancia
try:
    from .cuestionario import CuestionarioState
except ImportError:
    CuestionarioState = None # Handle case where file might not exist yet

# --- CONSTANTES ---
PRIMARY_COLOR_SCHEME = "blue"
ACCENT_COLOR_SCHEME = "amber"
FONT_FAMILY = "Poppins, sans-serif"
GOOGLE_FONT_STYLESHEET = [
    "https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap"
]
# --- FIN CONSTANTES ---


# --- FUNCIONES HELPER ---
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

def error_callout(message: rx.Var[str]):
    """Componente UI para mostrar errores."""
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
# --- FIN FUNCIONES HELPER ---


# --- ESTADO CENTRAL: AppState ---
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
        _cursos_data = getattr(config_logic, "CURSOS", {})
        cursos_dict: Dict[str, Any] = _cursos_data if isinstance(_cursos_data, dict) else {}
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

    # Estados Funcionalidades (Generales)
    is_generating_resumen: bool = False
    resumen_content: str = ""
    puntos_content: str = ""
    include_puntos: bool = False
    is_generating_mapa: bool = False
    mapa_mermaid_code: str = ""
    mapa_image_url: str = ""
    mapa_orientacion_horizontal: bool = True
    is_loading_stats: bool = False
    is_loading_profile_data: bool = False  # Added missing attribute
    stats_history: List[Dict[str, Any]] = []
    error_message_ui: str = ""
    active_tab: str = "inicio"
    
    # Estado para la pestaña de ayuda
    ayuda_search_query: str = ""
    show_contact_form: bool = False
    ayuda_pregunta_abierta: int = -1  # Índice de la pregunta abierta (-1 significa ninguna abierta)
    
    # Catálogo de preguntas y respuestas de ayuda
    ayuda_preguntas_respuestas: List[Dict[str, str]] = [
        {
            "pregunta": "¿Cómo registrarse en tu cuenta de Student?", 
            "respuesta": "Para registrarte, haz clic en el botón 'Crear cuenta' en la página de inicio de sesión. Completa el formulario con tu información personal y académica. Recibirás un correo de confirmación para activar tu cuenta. Una vez activada, podrás iniciar sesión con tu nombre de usuario y contraseña."
        },
        {
            "pregunta": "Para comenzar a usar Student:", 
            "respuesta": "Después de iniciar sesión, explora las diferentes pestañas de la aplicación. Comienza seleccionando un curso y un libro en la pestaña 'Libros'. Luego, utiliza las funcionalidades de resúmenes, mapas conceptuales o evaluaciones para potenciar tu aprendizaje. Recuerda personalizar tu perfil para una mejor experiencia."
        },
        {
            "pregunta": "¿Cómo elegir un curso?", 
            "respuesta": "Navega a la pestaña 'Libros' o a cualquier funcionalidad que requiera selección de curso. Utiliza el menú desplegable para ver los cursos disponibles según tu nivel académico. Selecciona el curso que necesites estudiar. Una vez seleccionado, podrás acceder a los libros y materiales asociados a ese curso específico."
        },
        {
            "pregunta": "Configurar horarios, calificaciones, etc:", 
            "respuesta": "En la pestaña 'Perfil', encontrarás opciones para configurar tu horario de estudio personalizado. Puedes establecer recordatorios, programar sesiones de estudio y dar seguimiento a tus calificaciones. La sección de análisis te permitirá visualizar tu progreso académico y áreas de mejora. Personaliza estas opciones según tus necesidades específicas."
        },
        {
            "pregunta": "¿Cómo explorar materiales y recursos?", 
            "respuesta": "En la pestaña 'Libros' encontrarás todos los materiales organizados por curso y asignatura. Puedes descargar PDFs, crear resúmenes o mapas conceptuales a partir de estos contenidos. La barra de búsqueda te permite encontrar rápidamente temas específicos. Explora también la sección 'Recursos Populares' en la página de inicio para acceder a los materiales más utilizados por estudiantes de tu nivel."
        },
        {
            "pregunta": "Añadir a compañeros, ¡es sencillo!", 
            "respuesta": "Para colaborar con compañeros, ve a tu perfil y selecciona la opción 'Compañeros de estudio'. Busca a tus amigos por nombre de usuario o correo electrónico. Envía solicitudes de conexión y espera su confirmación. Una vez conectados, podrán compartir recursos, crear grupos de estudio y colaborar en tiempo real en diversas actividades académicas."
        },
        {
            "pregunta": "Trabajar en equipo, ¡es divertido!", 
            "respuesta": "Student ofrece herramientas para el trabajo colaborativo. Crea grupos de estudio, comparte resúmenes y mapas conceptuales con tus compañeros, realiza evaluaciones en grupo y discute resultados. Utiliza la función de chat para comunicarte en tiempo real mientras estudian juntos. Crea documentos compartidos donde todos puedan contribuir con sus ideas y conocimientos."
        },
        {
            "pregunta": "¿Qué funciones ofrece la aplicación para aprender?", 
            "respuesta": "Student cuenta con múltiples herramientas para potenciar tu aprendizaje: Resúmenes inteligentes generados por IA, mapas conceptuales interactivos, evaluaciones personalizadas, cuestionarios de práctica, biblioteca digital con materiales por curso, seguimiento de progreso con estadísticas y análisis de rendimiento, y funciones colaborativas para estudiar con compañeros. Explora cada pestaña para descubrir todas las funcionalidades disponibles."
        }
    ]

    # --- Computed Vars ---
    @rx.var
    def libros_para_curso(self) -> List[str]:
        if not self.selected_curso or self.selected_curso == "Error al Cargar Cursos":
            return []
        try:
            return list(self.cursos_dict.get(self.selected_curso, {}).keys())
        except Exception as e:
            print(f"Error obteniendo libros: {e}")
            return []

    @rx.var
    def pdf_url(self) -> str:
        if not self.selected_curso or not self.selected_libro:
            return ""
        try:
            curso = self.selected_curso.lower().replace(" ", "_")
            archivo = self.cursos_dict[self.selected_curso][self.selected_libro]
            return f"/pdfs/{curso}/{archivo}"
        except Exception as e:
            print(f"ERROR generando URL PDF: {e}")
            return ""
            
    @rx.var
    def user_stats(self) -> List[Dict[str, Any]]:
        """Obtiene las estadísticas del usuario para mostrar en la pestaña de perfil."""
        if not self.logged_in_username or not BACKEND_AVAILABLE:
            # Mock data para demostración cuando no hay backend o usuario
            return [
                {
                    "nombre": "Examen Final",
                    "curso": "Historia",
                    "libro": "Historia universal tomo 1",
                    "tema": "La Edad Media",
                    "puntuacion": 8.5,
                    "fecha": "15/04/2024"
                }
            ]
        
        try:
            if not hasattr(db_logic, "obtener_estadisticas_usuario"):
                print("WARN: No se encontró la función obtener_estadisticas_usuario")
                return []
                
            stats_raw = db_logic.obtener_estadisticas_usuario(self.logged_in_username)
            
            # Handle different return types
            if isinstance(stats_raw, list):
                stats = stats_raw
            elif isinstance(stats_raw, dict):
                print(f"INFO: Convirtiendo estadísticas de diccionario a lista: {stats_raw}")
                # If it's a dictionary with items, convert it to a list of one item
                if stats_raw:
                    stats = [stats_raw]
                else:
                    stats = []
            else:
                print(f"WARN: Las estadísticas obtenidas no son ni lista ni diccionario: {type(stats_raw)}")
                return []
                
            # Asegurarse de que cada ítem tenga todas las claves necesarias
            formatted_stats = []
            for stat in stats:
                if isinstance(stat, dict):
                    # Por defecto, usar 'Evaluación' como nombre si no está especificado
                    if "nombre" not in stat:
                        stat["nombre"] = "Examen Final"
                    formatted_stats.append(stat)
            
            return formatted_stats
        except Exception as e:
            print(f"ERROR obteniendo estadísticas: {e}")
            return []
            
    @rx.var
    def promedio_calificaciones(self) -> str:
        """Calcula el promedio de calificaciones del usuario para mostrar en la pestaña de perfil."""
        stats = self.user_stats
        if not stats:
            return "0.0"
            
        total_puntuacion = 0
        count = 0
        
        for stat in stats:
            if isinstance(stat, dict) and "puntuacion" in stat:
                try:
                    puntuacion = float(stat["puntuacion"])
                    total_puntuacion += puntuacion
                    count += 1
                except (ValueError, TypeError):
                    # Ignorar valores que no se pueden convertir a float
                    pass
                    
        if count == 0:
            return "0.0"
            
        promedio = total_puntuacion / count
        return f"{promedio:.1f}"
    # --- Fin Computed Vars ---

    # --- Event Handlers ---
    async def set_active_tab(self, tab: str):
        if not isinstance(tab, str):
            return
        print(f"DEBUG: Navegando a tab '{tab}'. Selección actual: Curso='{self.selected_curso}', Libro='{self.selected_libro}', Tema='{self.selected_tema}'")

        tab_anterior = self.active_tab

        if tab != tab_anterior:
            print(f"DEBUG: Cambiando de pestaña {tab_anterior} a {tab}, limpiando campos generales...")

            # Reiniciar la selección de curso, libro y tema (general)
            self.selected_curso = ""
            self.selected_libro = ""
            self.selected_tema = ""

            # Limpiar contenido de resultados generales
            self.error_message_ui = ""
            self.resumen_content = ""
            self.puntos_content = ""
            self.include_puntos = False
            self.mapa_image_url = ""
            self.mapa_mermaid_code = ""
            self.is_generating_resumen = False
            self.is_generating_mapa = False

            # Limpiar estado específico de evaluaciones si existe la clase
            try:
                from .evaluaciones import EvaluationState
                if tab_anterior == "evaluacion":
                    print("DEBUG: Reseteando EvaluationState...")
                    eval_substate = await self.get_state(EvaluationState)
                    if eval_substate and hasattr(eval_substate, "reset_evaluation_state"):
                        print("DEBUG: Llamando a EvaluationState.reset_evaluation_state() en la instancia...")
                        async for _ in eval_substate.reset_evaluation_state():
                            pass
                    else:
                        print("WARN: No se pudo obtener la instancia de EvaluationState o el método reset_evaluation_state.")
            except (ImportError, AttributeError, TypeError) as e:
                print(f"DEBUG: No se pudo resetear EvaluationState: {e}")
                pass

            # Limpiar estado específico de cuestionarios si venimos de esa pestaña
            if tab_anterior == "cuestionario" and CuestionarioState:
                print("DEBUG: Reseteando estado de Cuestionario via get_state...")
                try:
                    cuestionario_substate = await self.get_state(CuestionarioState)
                    if cuestionario_substate and hasattr(cuestionario_substate, "reset_cuestionario"):
                        print("DEBUG: Llamando a CuestionarioState.reset_cuestionario() en la instancia...")
                        async for _ in cuestionario_substate.reset_cuestionario():
                            pass
                    else:
                        print("WARN: No se pudo obtener la instancia de CuestionarioState o el método reset_cuestionario.")
                except Exception as e:
                    print(f"ERROR: Excepción al intentar resetear CuestionarioState via get_state: {e}")
                    traceback.print_exc()

        # Establecer la nueva pestaña activa
        self.active_tab = tab

        # Cargar estadísticas si vamos a la pestaña de perfil
        if tab == "perfil":
            async for _ in self.load_stats():
                pass
        else:
            yield

    def toggle_pregunta(self, index: int):
        """Abre o cierra una pregunta de la pestaña de ayuda."""
        if self.ayuda_pregunta_abierta == index:
            # Si la pregunta ya está abierta, la cerramos
            self.ayuda_pregunta_abierta = -1
        else:
            # Si la pregunta está cerrada, la abrimos
            self.ayuda_pregunta_abierta = index
        yield

    def go_to_curso_and_resumen(self, curso: str):
        if not isinstance(curso, str) or not curso:
            return
        self.selected_curso = curso
        self.selected_libro = ""
        self.selected_tema = ""
        self.resumen_content = ""
        self.puntos_content = ""
        self.mapa_mermaid_code = ""
        self.mapa_image_url = ""
        self.error_message_ui = ""
        self.active_tab = "resumen"
        yield

    def go_to_resumen_tab(self):
        self.error_message_ui = ""
        self.resumen_content = ""
        self.puntos_content = ""
        yield

    def go_to_mapa_tab(self):
        self.error_message_ui = ""
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        yield

    def go_to_evaluacion_tab(self):
        self.error_message_ui = ""
        yield

    def handle_login(self):
        self.login_error_message = ""
        self.error_message_ui = ""
        if not self.username_input or not self.password_input:
            self.login_error_message = "Ingresa usuario y contraseña."
            return
        if (self.username_input == "felipe" and self.password_input == "1234") or \
           (self.username_input == "test" and self.password_input == "123"):
            self.is_logged_in = True
            self.logged_in_username = self.username_input
            self.username_input = self.password_input = ""
            self.active_tab = "inicio"
            yield
            return
        if not BACKEND_AVAILABLE:
            self.login_error_message = "Servicio no disponible. Cuentas prueba: felipe/1234, test/123."
            yield
            return
        if not hasattr(login_logic, "verificar_login") or not callable(login_logic.verificar_login):
            self.login_error_message = "Error servicio autenticación."
            yield
            return
        try:
            is_valid = login_logic.verificar_login(self.username_input, self.password_input)
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
            self.login_error_message = "Error servicio autenticación. Intenta más tarde."
            self.password_input = ""
        yield

    def logout(self):
        """Cierra la sesión del usuario actual."""
        self.is_logged_in = False
        self.logged_in_username = ""  # Corregido: username → logged_in_username
        self.active_tab = "inicio"
        # Reiniciar todas las variables de estado relacionadas con la sesión
        self.selected_curso = ""
        self.selected_libro = ""
        self.selected_tema = ""
        self.mapa_image_url = ""
        # Eliminamos la redirección que podría causar el error 404
        yield  # Usamos yield en lugar de return para que Reflex maneje la redirección internamente

    def clear_selection_and_results(self):
        print("DEBUG: Ejecutando clear_selection_and_results...")
        self.selected_tema = ""
        self.selected_libro = ""
        self.resumen_content = ""
        self.puntos_content = ""
        self.mapa_mermaid_code = ""
        self.mapa_image_url = ""
        self.error_message_ui = ""

    def handle_curso_change(self, new_curso: str):
        print(f"DEBUG: handle_curso_change -> {new_curso}")
        self.selected_curso = new_curso
        self.selected_libro = ""
        self.selected_tema = ""
        self.error_message_ui = ""
        yield

    def handle_libro_change(self, new_libro: str):
        print(f"DEBUG: handle_libro_change -> {new_libro}")
        self.selected_libro = new_libro
        self.selected_tema = ""
        self.error_message_ui = ""
        yield

    def handle_libros_curso_change(self, new_curso: str):
        print(f"DEBUG: handle_libros_curso_change -> {new_curso}")
        self.selected_curso = new_curso
        self.selected_libro = ""
        self.error_message_ui = ""
        yield

    def handle_libros_libro_change(self, new_libro: str):
        print(f"DEBUG: handle_libros_libro_change -> {new_libro}")
        self.selected_libro = new_libro
        self.error_message_ui = ""
        yield

    def set_selected_tema(self, new_tema: str):
        if not isinstance(new_tema, str):
            return
        print(f"DEBUG: set_selected_tema -> {new_tema[:50]}...")
        self.selected_tema = new_tema
        yield

    def set_include_puntos(self, value: bool):
        if not isinstance(value, bool):
            return
        self.include_puntos = value
        yield

    def set_mapa_orientacion(self, value: bool):
        if not isinstance(value, bool):
            return
        self.mapa_orientacion_horizontal = value
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        yield

    def clear_map(self):
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        self.error_message_ui = ""
        yield

    async def generate_summary(self):
        print("DEBUG: Iniciando generate_summary...")
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
        self.puntos_content = ""
        self.error_message_ui = ""
        yield
        try:
            if not hasattr(resumen_logic, "generar_resumen_logica"):
                raise AttributeError("Falta resumen_logic.generar_resumen_logica")
            print(f"DEBUG: Llamando resumen_logic con C='{self.selected_curso}', L='{self.selected_libro}', T='{self.selected_tema}', Puntos={self.include_puntos}")
            result = resumen_logic.generar_resumen_logica(
                self.selected_curso, self.selected_libro, self.selected_tema.strip(), self.include_puntos
            )
            print(f"DEBUG: Resultado de resumen_logic: {result}")
            if isinstance(result, dict) and result.get("status") == "EXITO":
                self.resumen_content = result.get("resumen", "")
                if self.include_puntos:
                    puntos = result.get("puntos")
                    self.puntos_content = puntos if isinstance(puntos, str) else ""
                else:
                    self.puntos_content = ""
            else:
                msg = result.get("message", "Error resumen.") if isinstance(result, dict) else "Error respuesta."
                self.error_message_ui = msg
                print(f"ERROR: Falla en resumen_logic: {msg}")
        except AttributeError as ae:
            self.error_message_ui = f"Error config: {ae}"
            print(f"ERROR Config: {self.error_message_ui}")
        except Exception as e:
            self.error_message_ui = f"Error crítico resumen: {str(e)}"
            print(f"ERROR G-SUM: {traceback.format_exc()}")
        finally:
            self.is_generating_resumen = False
            yield

    async def generate_map(self):
        print("DEBUG: Iniciando generate_map...")
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
        self.mapa_mermaid_code = ""
        yield
        try:
            if not all(hasattr(map_logic, fn) for fn in ["generar_nodos_localmente", "generar_mermaid_code", "generar_visualizacion_html"]):
                raise AttributeError("Funciones de map_logic faltantes.")
            print(f"DEBUG: Llamando map_logic.generar_nodos_localmente con T='{self.selected_tema}'")
            resultado_nodos = map_logic.generar_nodos_localmente(self.selected_tema.strip())
            print(f"DEBUG: Resultado nodos: {resultado_nodos}")
            
            # PASO 1: Convertir los nodos a formato de texto estructurado para Mermaid
            if resultado_nodos.get("status") == "EXITO" and "nodos" in resultado_nodos:
                nodos = resultado_nodos["nodos"]
                estructura_texto = f"- Nodo Central: {self.selected_tema.strip().title()}\n"
                
                for nodo in nodos:
                    titulo = nodo.get("titulo", "")
                    if titulo:
                        estructura_texto += f"  - Nodo Secundario: {titulo}\n"
                        
                        for subnodo in nodo.get("subnodos", []):
                            estructura_texto += f"    - Nodo Terciario: {subnodo}\n"
                
                # PASO 2: Generar código Mermaid a partir de la estructura de texto
                print("DEBUG: Generando código Mermaid a partir de la estructura...")
                orientation = "LR" if self.mapa_orientacion_horizontal else "TD"
                mermaid_code, error_mermaid = map_logic.generar_mermaid_code(estructura_texto, orientation)
                
                if error_mermaid:
                    raise Exception(f"Error generando código Mermaid: {error_mermaid}")
                
                if not mermaid_code:
                    raise Exception("No se generó código Mermaid válido")
                
                self.mapa_mermaid_code = mermaid_code
                
                # PASO 3: Generar HTML para visualización
                print("DEBUG: Generando HTML para visualización del mapa...")
                html_url = map_logic.generar_visualizacion_html(mermaid_code, self.selected_tema)
                
                if not html_url:
                    raise Exception("No se pudo generar la visualización HTML")
                
                # PASO 4: Actualizar la URL de la imagen para mostrarla en la UI
                self.mapa_image_url = html_url
                print(f"DEBUG: HTML URL generada: {html_url[:100]}...")
            else:
                raise Exception(f"Error en resultado de nodos: {resultado_nodos.get('status')}")
                
        except AttributeError as ae:
            self.error_message_ui = f"Error config map: {ae}"
            print(f"ERROR Config: {self.error_message_ui}")
        except Exception as e:
            self.error_message_ui = f"Error generando mapa: {str(e)}"
            print(f"ERROR G-MAP: {traceback.format_exc()}")
        finally:
            self.is_generating_mapa = False
            yield

    async def load_stats(self):
        print("DEBUG: Iniciando load_stats...")
        if not self.logged_in_username:
            self.stats_history = []
            self.is_loading_stats = False
            yield
            return
        self.is_loading_stats = True
        yield
        try:
            if not hasattr(db_logic, "obtener_estadisticas_usuario"):
                raise AttributeError("Falta db_logic.obtener_estadisticas_usuario")
            stats_raw = db_logic.obtener_estadisticas_usuario(self.logged_in_username)
        except Exception as e:
            pass
        finally:
            self.is_loading_stats = False
            yield

    async def download_pdf(self):
        """Función general para descargar PDFs según el contexto actual (resumen, mapa o cuestionario)"""
        print("DEBUG: Iniciando download_pdf...")
        
        # Determinar qué tipo de contenido descargar según la pestaña activa
        if self.active_tab == "resumen":
            async for result in self.download_resumen_pdf():
                yield result
        elif self.active_tab == "mapa":
            async for result in self.download_map_pdf():
                yield result
        elif self.active_tab == "cuestionario":
            async for result in self.download_cuestionario_pdf():
                yield result
        else:
            self.error_message_ui = "No hay contenido disponible para descargar."
            yield

    async def download_resumen_pdf(self):
        """Descarga el resumen actual en formato PDF"""
        print("DEBUG: Iniciando download_resumen_pdf...")
        if not self.resumen_content:
            self.error_message_ui = "No hay resumen para descargar."
            yield
            return

        s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "tema")[:50]
        s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "libro")[:50]
        s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "curso")[:50]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fname_base = f"Resumen_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")

        try:
            pdf_generado = False
            if hasattr(resumen_logic, "generar_resumen_pdf_bytes"):
                print("DEBUG: Intentando generar PDF con resumen_logic...")
                try:
                    pdf_bytes = resumen_logic.generar_resumen_pdf_bytes(
                        resumen_txt=self.resumen_content,
                        puntos_txt=self.puntos_content if self.include_puntos else "",
                        titulo=f"Resumen: {self.selected_tema or 'General'}",
                        subtitulo=f"Curso: {self.selected_curso or 'N/A'} - Libro: {self.selected_libro or 'N/A'}",
                    )
                    if isinstance(pdf_bytes, bytes) and pdf_bytes.startswith(b"%PDF"):
                        fname = f"{fname_base}.pdf"
                        print(f"DEBUG: PDF generado ({len(pdf_bytes)} bytes). Descargando como {fname}")
                        yield rx.download(data=pdf_bytes, filename=fname)
                        pdf_generado = True
                    else:
                        print("WARN: resumen_logic.generar_resumen_pdf_bytes no devolvió un PDF válido.")
                except Exception as pdf_e:
                    print(f"WARN: Error en generación de PDF con resumen_logic (usando fallback HTML): {pdf_e}")

            if not pdf_generado:
                print("DEBUG: Generando fallback HTML...")
                html_content = f"""<!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Resumen: {s_tema}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                        h1 {{ color: #2563eb; }}
                        h2 {{ color: #4b5563; margin-top: 30px; }}
                        .resumen {{ background-color: #f3f4f6; padding: 20px; border-radius: 5px; }}
                        .puntos {{ margin-top: 30px; }}
                        .puntos ol {{ padding-left: 20px; }}
                    </style>
                </head>
                <body>
                    <h1>Resumen: {self.selected_tema}</h1>
                    <h3>Curso: {self.selected_curso} - Libro: {self.selected_libro}</h3>
                    <hr>
                    <div class="resumen">
                        {self.resumen_content.replace('\n', '<br>')}
                    </div>
                    
                    {f'<h2>Puntos Clave:</h2><div class="puntos">{self.puntos_content.replace("\n", "<br>")}</div>' if self.puntos_content and self.include_puntos else ''}
                    
                    <hr>
                    <footer>
                        <p><i>Generado por SMART_STUDENT el {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</i></p>
                    </footer>
                </body>
                </html>"""
                fname = f"{fname_base}.html"
                print(f"DEBUG: Descargando resumen como HTML: {fname}")
                yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)

        except Exception as e:
            self.error_message_ui = f"Error descarga: {str(e)}"
            print(f"ERROR DWNLD PDF/HTML: {traceback.format_exc()}")
            yield

    async def download_map_pdf(self):
        """Descarga el mapa conceptual actual en formato PDF"""
        print("DEBUG: Iniciando download_map_pdf...")
        if not self.mapa_mermaid_code or not self.mapa_image_url:
            self.error_message_ui = "No hay mapa conceptual para descargar."
            yield
            return

        s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "tema")[:50]
        s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "libro")[:50]
        s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "curso")[:50]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fname_base = f"Mapa_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")

        try:
            pdf_generado = False
            if hasattr(map_logic, "generar_mapa_pdf_bytes"):
                print("DEBUG: Intentando generar PDF del mapa con map_logic...")
                try:
                    pdf_bytes = map_logic.generar_mapa_pdf_bytes(
                        mermaid_code=self.mapa_mermaid_code,
                        tema=self.selected_tema,
                        curso=self.selected_curso,
                        libro=self.selected_libro,
                        html_url=self.mapa_image_url
                    )
                    if isinstance(pdf_bytes, bytes) and pdf_bytes.startswith(b"%PDF"):
                        fname = f"{fname_base}.pdf"
                        print(f"DEBUG: PDF del mapa generado ({len(pdf_bytes)} bytes). Descargando como {fname}")
                        yield rx.download(data=pdf_bytes, filename=fname)
                        pdf_generado = True
                    else:
                        print("WARN: map_logic.generar_mapa_pdf_bytes no devolvió un PDF válido.")
                except Exception as pdf_e:
                    print(f"WARN: Error en generación de PDF del mapa (usando fallback HTML): {pdf_e}")
                    traceback.print_exc()

            if not pdf_generado:
                print("DEBUG: Generando mapa fallback HTML...")
                html_content = f"""<!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Mapa Conceptual: {s_tema}</title>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        h1 {{ color: #2563eb; }}
                        .mermaid {{ background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    </style>
                </head>
                <body>
                    <h1>Mapa Conceptual: {self.selected_tema}</h1>
                    <h3>Curso: {self.selected_curso} - Libro: {self.selected_libro}</h3>
                    <hr>
                    <div class="mermaid">
                        {self.mapa_mermaid_code}
                    </div>
                    <script>
                        mermaid.initialize({{
                            startOnLoad: true,
                            theme: 'default',
                            themeVariables: {{
                                primaryColor: '#d4e8ff',
                                primaryTextColor: '#003366',
                                primaryBorderColor: '#7fb3ff',
                                lineColor: '#4b5563',
                                fontSize: '16px'
                            }}
                        }});
                    </script>
                    <hr>
                    <footer>
                        <p><i>Generado por SMART_STUDENT el {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</i></p>
                    </footer>
                </body>
                </html>"""
                fname = f"{fname_base}.html"
                print(f"DEBUG: Descargando mapa como HTML: {fname}")
                yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)

        except Exception as e:
            self.error_message_ui = f"Error al descargar mapa: {str(e)}"
            print(f"ERROR DWNLD MAP PDF/HTML: {traceback.format_exc()}")
            yield

    async def download_cuestionario_pdf(self):
        """Descarga el cuestionario actual en formato PDF"""
        # Importamos solo cuando se necesita para evitar dependencias circulares
        from .cuestionario import CuestionarioState
        
        print("DEBUG: Iniciando download_cuestionario_pdf...")
        
        # Verificamos primero si el atributo existe
        if not hasattr(CuestionarioState, "cuestionario_preguntas"):
            self.error_message_ui = "No hay cuestionario para descargar."
            yield
            return
            
        # Verificamos si hay preguntas de manera segura con variables reactivas
        try:
            # Tratamos de acceder a alguna pregunta para ver si hay contenido
            # En lugar de usar length() directamente en un if
            primera_pregunta = CuestionarioState.cuestionario_preguntas[0]
            tiene_preguntas = True
        except Exception as e:
            print(f"DEBUG: No se encontraron preguntas en el cuestionario: {e}")
            tiene_preguntas = False
            
        # Si no hay preguntas, informar y salir
        if not tiene_preguntas:
            self.error_message_ui = "No hay preguntas en el cuestionario para descargar."
            yield
            return

        s_tema = re.sub(r'[\\/*?:"<>|]', "", CuestionarioState.cuestionario_tema or "tema")[:50]
        s_lib = re.sub(r'[\\/*?:"<>|]', "", CuestionarioState.cuestionario_libro or "libro")[:50]
        s_cur = re.sub(r'[\\/*?:"<>|]', "", CuestionarioState.cuestionario_curso or "curso")[:50]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fname_base = f"Cuestionario_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")

        try:
            # Primero intentamos utilizar la URL del PDF que ya se generó en la clase CuestionarioState
            if hasattr(CuestionarioState, "cuestionario_pdf_url") and CuestionarioState.cuestionario_pdf_url:
                # Si ya hay un PDF generado, usamos esa URL
                print(f"DEBUG: Usando PDF ya generado: {CuestionarioState.cuestionario_pdf_url}")
                # La URL es relativa, así que buscamos el archivo directamente
                pdf_path = os.path.join("assets", CuestionarioState.cuestionario_pdf_url.lstrip('/'))
                if os.path.exists(pdf_path) and os.path.isfile(pdf_path):
                    try:
                        with open(pdf_path, 'rb') as f:
                            pdf_bytes = f.read()
                        if pdf_bytes and pdf_bytes.startswith(b"%PDF"):
                            fname = f"{fname_base}.pdf"
                            print(f"DEBUG: Leyendo PDF existente ({len(pdf_bytes)} bytes). Descargando como {fname}")
                            yield rx.download(data=pdf_bytes, filename=fname)
                            return
                    except Exception as e:
                        print(f"WARN: Error leyendo PDF existente: {e}")
            
            # Si no hay PDF o falló la lectura, generamos HTML con las preguntas
            preguntas_html = ""
            for i, pregunta in enumerate(CuestionarioState.cuestionario_preguntas):
                pregunta_texto = pregunta.get("pregunta", f"Pregunta {i+1}")
                explicacion = pregunta.get("explicacion", "")
                correcta = pregunta.get("correcta", "")
                
                preguntas_html += f"""
                <div class="pregunta">
                    <h3>{i+1}. {pregunta_texto}</h3>
                    <div class="respuesta">Respuesta: {correcta}</div>
                    {f'<div class="explicacion">Explicación: {explicacion}</div>' if explicacion else ''}
                </div>
                """
            
            html_content = f"""<!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Cuestionario: {s_tema}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2563eb; }}
                    h2 {{ color: #4b5563; margin-top: 30px; }}
                    .pregunta {{ background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .pregunta h3 {{ margin-top: 0; color: #1e40af; }}
                    .respuesta {{ margin-top: 10px; font-weight: bold; }}
                    .explicacion {{ margin-top: 10px; font-style: italic; color: #4b5563; }}
                </style>
            </head>
            <body>
                <h1>Cuestionario: {s_tema}</h1>
                <h3>Curso: {s_cur} - Libro: {s_lib}</h3>
                <p>Contiene preguntas generadas para tu estudio</p>
                <hr>
                {preguntas_html}
                <hr>
                <footer>
                    <p><i>Generado por SMART_STUDENT el {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</i></p>
                </footer>
            </body>
            </html>"""
            fname = f"{fname_base}.html"
            print(f"DEBUG: Descargando cuestionario como HTML: {fname}")
            yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)

        except Exception as e:
            self.error_message_ui = f"Error al descargar cuestionario: {str(e)}"
            print(f"ERROR DWNLD CUESTIONARIO PDF/HTML: {traceback.format_exc()}")
            yield

    def open_contact_form(self):
        """Abre el formulario de contacto o redirige al correo de soporte."""
        # En una implementación completa, esto mostraría un modal con un formulario de contacto
        # Por ahora, simplemente abrimos el cliente de correo del usuario
        print("DEBUG: Abriendo formulario de contacto o cliente de correo")
        import webbrowser
        try:
            webbrowser.open("mailto:support@smartstudent.cl?subject=Consulta%20desde%20SMART%20STUDENT")
        except Exception as e:
            self.error_message_ui = "No se pudo abrir el cliente de correo. Por favor, envía un correo a support@smartstudent.cl"
            print(f"ERROR: No se pudo abrir el cliente de correo: {e}")
        yield
        
    def set_ayuda_search_query(self, query: str):
        """Establece la consulta de búsqueda para la pestaña de ayuda."""
        if not isinstance(query, str):
            return
        self.ayuda_search_query = query
        yield

# --- FIN CLASE AppState ---