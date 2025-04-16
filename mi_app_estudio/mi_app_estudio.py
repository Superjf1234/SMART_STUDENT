"""
Aplicación SMART_STUDENT - Versión Optimizada y Depurada.

Script principal de la interfaz web con Reflex.
"""

import reflex as rx
import sys, os, datetime, traceback, re
from typing import Dict, List, Optional, Set, Union, Any

# Importación del Módulo de Evaluaciones
# Definimos la función de evaluación directamente aquí para evitar problemas de importación
def evaluacion_tab():
    """Contenido de la pestaña de evaluación."""
    return rx.vstack(
        rx.heading("📝 Evaluación de Conocimientos", size="6", mb="2em", text_align="center"),
        rx.text(
            "Pon a prueba tu comprensión del tema con preguntas generadas automáticamente.",
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
                    placeholder="Tema específico a evaluar...",
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
                rx.button(
                    rx.cond(
                        AppState.is_generating_eval,
                        rx.hstack(rx.spinner(size="2"), "Generando evaluación..."),
                        "Crear Evaluación"
                    ),
                    on_click=AppState.generate_summary,
                    size="3",
                    color_scheme="purple",
                    width="100%",
                    margin_top="1em",
                    is_disabled=rx.cond(
                        (AppState.selected_tema == "") | AppState.is_generating_eval,
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
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="5em",
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

# Estado Central
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
        cursos_dict: Dict[str, Any] = (
            _cursos_data if isinstance(_cursos_data, dict) else {}
        )
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
    include_puntos: bool = False
    is_generating_mapa: bool = False
    mapa_mermaid_code: str = ""
    mapa_image_url: str = ""
    mapa_orientacion_horizontal: bool = True
    is_loading_stats: bool = False
    stats_history: List[Dict[str, Any]] = []
    error_message_ui: str = ""
    active_tab: str = "inicio"
    is_generating_eval: bool = False

    # Computed Vars
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

    # Event Handlers
    def set_active_tab(self, tab: str):
        if not isinstance(tab, str):
            return
        self.selected_curso = ""
        self.selected_libro = ""
        self.selected_tema = ""
        self.resumen_content = ""
        self.puntos_content = ""
        self.include_puntos = False
        self.error_message_ui = ""
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        self.is_generating_resumen = False
        self.is_generating_mapa = False
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
        if (self.username_input == "felipe" and self.password_input == "1234") or (
            self.username_input == "test" and self.password_input == "123"
        ):
            self.is_logged_in = True
            self.logged_in_username = self.username_input
            self.username_input = self.password_input = ""
            self.active_tab = "inicio"
            yield
            return
        if not BACKEND_AVAILABLE:
            self.login_error_message = "El servicio de autenticación no está disponible. Intenta de nuevo más tarde."
            self.login_error_message += " Puede usar las cuentas de prueba: felipe/1234 o test/123."
            yield
            return
        if not hasattr(login_logic, "verificar_login") or not callable(
            login_logic.verificar_login
        ):
            self.login_error_message = (
                "Error en el servicio de autenticación. Contacta al administrador."
            )
            yield
            return
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
        self.selected_tema = ""
        self.selected_libro = ""
        self.resumen_content = ""
        self.puntos_content = ""
        self.mapa_mermaid_code = ""
        self.mapa_image_url = ""
        self.error_message_ui = ""
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
        self.selected_curso = new_curso
        self.selected_libro = ""
        self.selected_tema = ""
        self.error_message_ui = ""
        yield

    def handle_libro_change(self, new_libro: str):
        self.selected_libro = new_libro
        self.selected_tema = ""
        self.error_message_ui = ""
        yield

    def handle_libros_curso_change(self, new_curso: str):
        self.selected_curso = new_curso
        self.selected_libro = ""
        self.error_message_ui = ""
        yield

    def handle_libros_libro_change(self, new_libro: str):
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
            result = resumen_logic.generar_resumen_logica(
                self.selected_curso,
                self.selected_libro,
                self.selected_tema.strip(),
                self.include_puntos,
            )
            if isinstance(result, dict) and result.get("status") == "EXITO":
                self.resumen_content = result.get("resumen", "")
                if self.include_puntos:
                    puntos = result.get("puntos")
                    self.puntos_content = (
                        puntos if isinstance(puntos, str) and puntos else ""
                    )
                else:
                    self.puntos_content = ""
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
            if not all(
                hasattr(map_logic, fn)
                for fn in [
                    "generar_nodos_localmente",
                    "generar_mermaid_code",
                    "generar_visualizacion_html",
                ]
            ):
                raise AttributeError("Funciones de map_logic faltantes.")
            resultado_nodos = map_logic.generar_nodos_localmente(
                self.selected_tema.strip()
            )
            if (
                not isinstance(resultado_nodos, dict)
                or "status" not in resultado_nodos
                or "nodos" not in resultado_nodos
            ):
                self.error_message_ui = "Formato de nodos inesperado."
                return
            if resultado_nodos["status"] != "EXITO":
                self.error_message_ui = resultado_nodos.get(
                    "message", "Error al generar nodos."
                )
                return
            nodos = resultado_nodos["nodos"]
            if not nodos:
                self.error_message_ui = "No se generaron nodos."
            else:
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
                orientacion = "LR" if self.mapa_orientacion_horizontal else "TD"
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
            s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "t")
            s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "l")
            s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "c")
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
            except Exception as pdf_e:
                print(f"Error en generación de PDF, usando fallback HTML: {pdf_e}")
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
        if not self.mapa_image_url:
            self.error_message_ui = "No hay mapa para descargar."
            yield
            return
        try:
            s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "tema")
            s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "libro")
            s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "curso")
            if hasattr(map_logic, "generar_mapa_pdf_bytes"):
                try:
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

# Funciones Helper para UI
def create_card(
    title, icon, description, action_text, on_click, color_scheme=PRIMARY_COLOR_SCHEME
):
    return rx.card(
        rx.vstack(
            rx.icon(icon, size=64, color=f"var(--{color_scheme}-9)"),
            rx.heading(title, size="5", mt="0.7em", text_align="center", flex_grow=0),
            rx.text(
                description,
                text_align="center",
                size="3",
                color_scheme="gray",
                flex_grow=1,
            ),
            rx.spacer(height="1em"),
            rx.box(
                rx.button(
                    action_text,
                    on_click=on_click,
                    size="3",
                    variant="soft",
                    color_scheme=color_scheme,
                    width="200px",
                ),
                width="100%",
                display="flex",
                justify_content="center",
            ),
            align="center",
            justify="between",
            p="2.5em",
            spacing="4",
            h="100%",
        ),
        variant="surface",
        size="3",
        h="400px",
        min_width="350px",
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

def nav_button(text: str, tab_name: str, active_tab: rx.Var[str]):
    return rx.button(
        text,
        on_click=lambda: AppState.set_active_tab(tab_name),
        variant=rx.cond(active_tab == tab_name, "solid", "ghost"),
        color_scheme=rx.cond(active_tab == tab_name, PRIMARY_COLOR_SCHEME, "gray"),
        size="2",
    )

# Definición de Páginas/Pestañas
def login_page():
    return rx.center(
        rx.vstack(
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
                            AppState.login_error_message != "",
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
                            width="100%",
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
                    reset_on_submit=False,
                ),
                width="400px",
                max_width="90%",
            ),
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
    """Contenido de la pestaña de inicio."""
    return rx.vstack(
        rx.heading("🏠 Bienvenido a SMART STUDENT", size="6", mb="2em", text_align="center"),
        rx.text(
            "Tu asistente de estudio inteligente potenciado por IA. Explora las herramientas para mejorar tu aprendizaje.",
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
                            "Libros Digitales",
                            "book",
                            "Accede a tus libros digitales y contenidos de estudio.",
                            "Ver Libros",
                            lambda: AppState.set_active_tab("libros"),
                            "green",
                        ),
                        create_card(
                            "Resúmenes Inteligentes",
                            "file-text",
                            "Genera resúmenes y puntos clave para estudiar de forma eficiente.",
                            "Crear Resumen",
                            lambda: AppState.set_active_tab("resumen"),
                            PRIMARY_COLOR_SCHEME,
                        ),
                        create_card(
                            "Mapas Conceptuales",
                            "git-branch",
                            "Visualiza conexiones entre conceptos para mejorar tu comprensión.",
                            "Crear Mapa",
                            lambda: AppState.set_active_tab("mapa"),
                            ACCENT_COLOR_SCHEME,
                        ),
                        create_card(
                            "Evaluaciones",
                            "clipboard-check",
                            "Pon a prueba tu conocimiento con preguntas generadas automáticamente.",
                            "Crear Evaluación",
                            lambda: AppState.set_active_tab("evaluacion"),
                            "purple",
                        ),
                        columns="2",
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
                        "Recursos Populares", size="5", mb="1em", text_align="center"
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
        ),
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="1em",
    )

def resumen_tab():
    """Contenido de la pestaña de resúmenes."""
    return rx.vstack(
        rx.heading("📄 Genera Resúmenes Inteligentes", size="6", mb="2em", text_align="center"),
        rx.text(
            "Simplifica temas complejos con resúmenes generados por IA para facilitar tu comprensión y estudio.",
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
                    placeholder="Tema específico a resumir...",
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
                        rx.text("Incluir puntos clave", size="2", ml="0.5em"),
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
                        rx.hstack(rx.spinner(size="2"), "Generando resumen..."),
                        "Generar Resumen"
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
        ),
        # Espacio para mostrar el resumen generado
        rx.cond(
            (AppState.resumen_content != "") | (AppState.puntos_content != ""),
            rx.card(
                rx.vstack(
                    rx.heading("Resultado", size="5", mb="1em"),
                    rx.cond(
                        AppState.resumen_content != "",
                        rx.vstack(
                            rx.heading("Resumen", size="4", mb="0.5em"),
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
                            align_items="flex-start",
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
                            align_items="flex-start",
                            spacing="2",
                        ),
                    ),
                    rx.hstack(
                        rx.button(
                            rx.icon("download", mr="0.2em"),
                            "Descargar PDF",
                            on_click=AppState.download_pdf,
                            variant="soft",
                            size="2",
                            color_scheme=PRIMARY_COLOR_SCHEME,
                        ),
                        rx.button(
                            rx.icon("git-branch", mr="0.2em"),
                            "Crear Mapa",
                            on_click=AppState.generate_map,
                            variant="soft",
                            size="2",
                            color_scheme=ACCENT_COLOR_SCHEME,
                            is_disabled=rx.cond(
                                AppState.is_generating_mapa,
                                True,
                                False,
                            ),
                        ),
                        rx.button(
                            rx.icon("clipboard-check", mr="0.2em"),
                            "Crear Evaluación",
                            on_click=lambda: AppState.set_active_tab("evaluacion"),
                            variant="soft",
                            size="2",
                            color_scheme="purple",
                        ),
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
        margin_top="1em",
    )

def mapa_tab():
    """Contenido de la pestaña de mapas conceptuales."""
    return rx.vstack(
        rx.heading("🧠 Crea Mapas Conceptuales", size="6", mb="2em", text_align="center"),
        rx.text(
            "Visualiza relaciones entre conceptos y fortalece tu comprensión con mapas conceptuales personalizados.",
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
                        rx.hstack(rx.spinner(size="2"), "Generando mapa..."),
                        "Generar Mapa"
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
                    rx.heading("Mapa Conceptual", size="5", mb="1em", text_align="center"),
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
                    rx.hstack(
                        rx.button(
                            rx.icon("download", mr="0.2em"),
                            "Descargar PDF",
                            on_click=AppState.download_map_pdf,
                            variant="soft",
                            size="2",
                            color_scheme=PRIMARY_COLOR_SCHEME,
                        ),
                        rx.button(
                            rx.icon("clipboard-check", mr="0.2em"),
                            "Crear Evaluación",
                            on_click=lambda: AppState.set_active_tab("evaluacion"),
                            variant="soft",
                            size="2",
                            color_scheme="purple",
                        ),
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
        margin_top="1em",
    )

def perfil_tab():
    return rx.vstack(
        rx.heading("Perfil y Progreso", size="6", mb="1.5em", text_align="center"),
        rx.grid(
            # Aquí iría el contenido del perfil
        ),
        rx.card(
            # Aquí iría el contenido de estadísticas
        ),
        w="100%",
        max_width="1000px",
        margin="0 auto",
        p="2em",
        spacing="5",
    )

def ayuda_tab():
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
    """Contenido de la pestaña de libros digitales."""
    return rx.vstack(
        rx.heading("📚 Biblioteca Digital", size="6", mb="2em", text_align="center"),
        rx.text(
            "Accede a tu colección de libros digitales para estudiar y repasar los contenidos académicos.",
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
                    on_change=AppState.handle_libros_curso_change,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                ),
                rx.select(
                    AppState.libros_para_curso,
                    placeholder="Selecciona un Libro...",
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
                    rx.heading("Información del Libro", size="5", mb="1em", text_align="center"),
                    rx.box(
                        rx.vstack(
                            rx.heading(AppState.selected_libro, size="4", mb="0.5em"),
                            rx.text(
                                f"Curso: {AppState.selected_curso}",
                                color="gray.500",
                                mb="0.5em",
                            ),
                            rx.text(
                                "Este libro contiene material educativo importante para tu aprendizaje.",
                                mb="1em",
                            ),
                            rx.link(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("file-text", mr="0.2em"),
                                        "Crear Resumen"
                                    ),
                                    variant="soft",
                                    size="2",
                                    color_scheme=PRIMARY_COLOR_SCHEME,
                                ),
                                on_click=lambda: AppState.set_active_tab("resumen"),
                                text_decoration="none",
                            ),
                            width="100%",
                            align_items="flex-start",
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
        margin_top="1em",
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
rx.Config.static_dir = "assets"
rx.Config.title = "Smart Student | Aprende, Crea y Destaca"
rx.Config.favicon = "/favicon.ico"

@app.add_page
def index() -> rx.Component:
    return rx.fragment(
        rx.script(
            "document.title = 'Smart Student | Aprende, Crea y Destaca'"
        ),
        rx.html('<link rel="icon" type="image/x-icon" href="/smartstudent_icon.ico">'),
        rx.cond(AppState.is_logged_in, main_dashboard(), login_page()),
    )