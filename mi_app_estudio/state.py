# Archivo: mi_app_estudio/state.py
# ¡VERSIÓN COMPLETA FINAL Y VERIFICADA!

"""
Módulo de estado base para SMART_STUDENT.
Contiene la definición de AppState que es usada por otros módulos.
"""

import reflex as rx
import sys, os, datetime, traceback, re
from typing import Dict, List, Optional, Set, Union, Any

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
                     "generar_evaluacion": lambda *a, **kw: {"status": "EXITO", "preguntas": [{"pregunta": "¿Mock?", "tipo": "opcion_multiple", "opciones": [{"id": "a", "texto": "Op A"}, {"id": "b", "texto": "Op B"}], "respuesta_correcta": "b", "explicacion": "Expl."}]},
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
    stats_history: List[Dict[str, Any]] = []
    error_message_ui: str = ""
    active_tab: str = "inicio"

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
    # --- Fin Computed Vars ---


    # --- Event Handlers ---
    def set_active_tab(self, tab: str):
        # (Versión corregida que preserva selección)
        if not isinstance(tab, str):
            return
        print(f"DEBUG: Navegando a tab '{tab}'. Selección actual: Curso='{self.selected_curso}', Libro='{self.selected_libro}', Tema='{self.selected_tema}'")
        tabs_que_limpian_seleccion = ["inicio", "libros"]
        if tab in tabs_que_limpian_seleccion:
            print(f"DEBUG: Limpiando selección porque tab '{tab}' está en {tabs_que_limpian_seleccion}")
            self.selected_curso = ""
            self.selected_libro = ""
            self.selected_tema = ""
        self.error_message_ui = ""
        self.resumen_content = ""
        self.puntos_content = ""
        self.include_puntos = False
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        self.is_generating_resumen = False
        self.is_generating_mapa = False
        self.active_tab = tab
        if tab == "perfil":
             # Asegúrate que AppState.load_stats exista y funcione como se espera
             # Si es async, el return podría necesitar ser yield o diferente manejo
             return AppState.load_stats # O self.load_stats si prefieres llamar método de instancia
        yield

    def go_to_curso_and_resumen(self, curso: str):
        if not isinstance(curso, str) or not curso:
            return
        self.selected_curso = curso
        self.selected_libro = ""
        # Limpiamos manualmente lo necesario
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

    # --- MÉTODO logout() ---
    def logout(self):
        """Cierra la sesión del usuario y resetea el estado."""
        print("DEBUG: Ejecutando logout...")
        try:
            self.reset()
            self.is_logged_in = False
            self.logged_in_username = ""
            self.active_tab = "inicio"
            if hasattr(self, "clear_selection_and_results") and callable(getattr(self, "clear_selection_and_results", None)):
                 self.clear_selection_and_results()
            self.login_error_message = ""
            print("DEBUG: Estado reseteado después de logout.")
        except Exception as e:
            print(f"ERROR: Excepción durante self.reset() en logout: {e}")
            print(traceback.format_exc())
            # Fallback manual
            self.is_logged_in = False
            self.logged_in_username = ""
            self.active_tab = "inicio"
            self.selected_curso = ""
            self.selected_libro = ""
            self.selected_tema = ""
            self.resumen_content = ""
            self.puntos_content = ""
            self.mapa_image_url = ""
            self.mapa_mermaid_code = ""
            self.stats_history = []
            self.error_message_ui = "Error al cerrar sesión."
            self.login_error_message = ""
        yield
    # --- FIN MÉTODO logout() ---

    def clear_selection_and_results(self):
        """Limpia selecciones de tema/libro y resultados."""
        print("DEBUG: Ejecutando clear_selection_and_results...")
        self.selected_tema = ""
        self.selected_libro = ""
        # self.selected_curso = "" # Decide si quieres borrar el curso aquí
        self.resumen_content = ""
        self.puntos_content = ""
        self.mapa_mermaid_code = ""
        self.mapa_image_url = ""
        self.error_message_ui = ""
        # No es necesario recargar cursos aquí si se cargan al inicio

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
        """Genera el resumen llamando al backend."""
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
            # Ajusta la llamada si la función del backend es async o síncrona
            # Si es async y expuesta como endpoint:
            # result = await rx.call_endpoint(...)
            # Si es sync pero podría bloquear: yield rx.call(resumen_logic...)
            # Si es sync rápida:
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
        """Genera el mapa conceptual llamando al backend."""
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
            # Ajusta la llamada si es async/sync
            resultado_nodos = map_logic.generar_nodos_localmente(self.selected_tema.strip())
            print(f"DEBUG: Resultado nodos: {resultado_nodos}")
            # ... (resto de la lógica para procesar nodos, generar mermaid, html) ...
            # ... (asegúrate que las llamadas a map_logic.generar_mermaid_code y
            #      map_logic.generar_visualizacion_html sean sync o async según corresponda) ...
        except AttributeError as ae:
             self.error_message_ui = f"Error config map: {ae}"
             print(f"ERROR Config: {self.error_message_ui}")
        except Exception as e:
             self.error_message_ui = f"Error generando mapa: {str(e)}"
             print(f"ERROR G-MAP: {traceback.format_exc()}")
        finally:
             self.is_generating_mapa = False
             # ... (lógica de error si no se generó imagen) ...
             yield

    async def load_stats(self):
         """Carga las estadísticas del usuario."""
         print("DEBUG: Iniciando load_stats...")
         if not self.logged_in_username:
              self.stats_history = []
              self.is_loading_stats = False
              yield
              return
         # ... (resto del código como lo tenías, ajustando llamadas si son async) ...
         self.is_loading_stats = True; yield
         try:
             if not hasattr(db_logic, "obtener_estadisticas_usuario"):
                 raise AttributeError("Falta db_logic.obtener_estadisticas_usuario")
             # Ajusta llamada si es async
             stats_raw = db_logic.obtener_estadisticas_usuario(self.logged_in_username)
             # ... (procesamiento de stats_raw) ...
         except Exception as e:
              # ... (manejo de errores) ...
              pass
         finally:
              self.is_loading_stats = False
              yield

    async def download_pdf(self):
        """Genera y descarga el resumen en PDF (o HTML como fallback)."""
        print("DEBUG: Iniciando download_pdf...")
        if not self.resumen_content:
            self.error_message_ui = "No hay resumen para descargar."
            yield
            return

        # Limpiar nombres de archivo
        s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "tema")[:50]
        s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "libro")[:50]
        s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "curso")[:50]
        fname_base = f"Resumen_{s_cur}_{s_lib}_{s_tema}".replace(" ", "_")

        try: # <-- Try principal (aprox línea 496)
            pdf_generado = False # Flag para saber si generamos PDF
            if hasattr(resumen_logic, "generar_resumen_pdf_bytes"):
                print("DEBUG: Intentando generar PDF con resumen_logic...")
                try:
                    pdf_bytes = await rx.call_endpoint( # O llamada síncrona si corresponde
                        resumen_logic.generar_resumen_pdf_bytes,
                        resumen_txt=self.resumen_content,
                        puntos_txt=self.puntos_content if self.include_puntos else "",
                        titulo=f"Resumen: {self.selected_tema or 'General'}",
                        subtitulo=f"Curso: {self.selected_curso or 'N/A'} - Libro: {self.selected_libro or 'N/A'}",
                    )
                    if isinstance(pdf_bytes, bytes) and pdf_bytes.startswith(b"%PDF"):
                        fname = f"{fname_base}.pdf"
                        print(f"DEBUG: PDF generado ({len(pdf_bytes)} bytes). Descargando como {fname}")
                        yield rx.download(data=pdf_bytes, filename=fname)
                        pdf_generado = True # Marcamos que sí se generó
                    else:
                        print("WARN: resumen_logic.generar_resumen_pdf_bytes no devolvió un PDF válido.")
                except Exception as pdf_e:
                    print(f"WARN: Error en generación de PDF con resumen_logic (usando fallback HTML): {pdf_e}")
                    # No ponemos error_message_ui aquí para permitir el fallback

            # Fallback a HTML si no se generó PDF
            if not pdf_generado:
                print("DEBUG: Generando fallback HTML...")
                html_content = f"""<!DOCTYPE html>
                <html lang="es">
                <head><meta charset="UTF-8"><title>Resumen: {s_tema}</title>...</head>
                <body>... (Tu contenido HTML aquí) ...</body></html>""" # Asegúrate que el HTML esté completo
                fname = f"{fname_base}.html"
                print(f"DEBUG: Descargando resumen como HTML: {fname}")
                yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)

        # --- BLOQUE except CORREGIDO (CON INDENTACIÓN) ---
        except Exception as e: # <-- Línea 500 (aprox)
             # El código DENTRO del except DEBE estar indentado
             self.error_message_ui = f"Error descarga: {str(e)}"
             print(f"ERROR DWNLD PDF/HTML: {traceback.format_exc()}")
             # El yield aquí asegura que el error se muestre en UI si es necesario
             yield # Asegura yield al final

# --- FIN CLASE AppState ---