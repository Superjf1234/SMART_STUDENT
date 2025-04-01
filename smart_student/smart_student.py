# smart_student/smart_student.py
"""Archivo principal de la aplicación web SMART STUDENT con Reflex."""

import reflex as rx
import sys # Asegúrate que sys esté importado si usas sys.stderr

# Importa los módulos de lógica del backend de forma RELATIVA
try:
    from .backend import ( # <-- CAMBIADO a importación relativa con "."
        config_logic,
        db_logic,
        login_logic,
        resumen_logic,
        map_logic,
        eval_logic,
    )
except ImportError as e:
    print(
        f"ERROR CRITICO: No se pueden importar módulos del backend: {e}. Verifica la estructura.",
        file=sys.stderr,
    )

    # Define mocks básicos si la importación falla
    class MockLogic:
        def __getattr__(self, name):
            def _mock_func(*args, **kwargs):
                print(f"ADVERTENCIA: Llamando a función mock '{name}'.")
                if name == "CURSOS":
                    return {"Mock Curso": {"Mock Libro": "mock.pdf"}}
                if name == "verificar_login":
                    return lambda u, p: u == "test" and p == "123"
                return None

            return _mock_func

    config_logic = login_logic = db_logic = resumen_logic = map_logic = eval_logic = (
        MockLogic()
    )

import os
import datetime
import typing


# --- Constantes de Estilo ---
# Dejamos las constantes pero no las aplicaremos globalmente por ahora
PRIMARY_COLOR_SCHEME = "blue"
ACCENT_COLOR_SCHEME = "amber"
# FONT_FAMILY = "Poppins, sans-serif"
# GOOGLE_FONT_STYLESHEET = ["https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap"]


# --- El Estado Central de la Aplicación ---
class AppState(rx.State):
    """El estado central de la aplicación SMART STUDENT Web."""

    # --- Estado de Autenticación ---
    username_input: str = ""
    password_input: str = ""
    is_logged_in: bool = False
    login_error_message: str = ""
    logged_in_username: str = ""
    # --- Estado de Selección ---
    try:
        cursos_dict: dict = config_logic.CURSOS
        cursos_list: list[str] = [c for c in cursos_dict.keys() if c != "Error"]
    except Exception as e_cursos:
        print(f"ERROR Cargando CURSOS: {e_cursos}", file=sys.stderr)
        cursos_dict: dict = {"Error": {"Carga": "error.pdf"}}
        cursos_list: list[str] = ["Error al Cargar Cursos"]
    selected_curso: str = ""
    selected_libro: str = ""
    selected_tema: str = ""

    @rx.var
    def libros_para_curso(self) -> list[str]:
        if not self.selected_curso or self.selected_curso == "Error al Cargar Cursos":
            return []
        return list(self.cursos_dict.get(self.selected_curso, {}).keys())

    # --- Estados para Funcionalidades ---
    is_generating_resumen: bool = False
    resumen_content: str = ""
    puntos_content: str = ""
    include_puntos: bool = True
    is_generating_mapa: bool = False
    mapa_orientation: str = "LR"
    mapa_mermaid_code: str = ""
    is_generating_eval: bool = False
    is_eval_active: bool = False
    is_reviewing_eval: bool = False
    eval_preguntas: list = []
    eval_current_idx: int = 0
    eval_user_answers: typing.Dict[int, typing.Union[str, typing.Set[str]]] = {}
    eval_score: typing.Optional[float] = None
    eval_correct_count: int = 0
    eval_total_q: int = 0
    is_loading_stats: bool = False
    stats_history: list = []
    error_message_ui: str = ""

    # --- Event Handlers ---
    def handle_login(self):
        self.login_error_message = ""
        if not self.username_input or not self.password_input:
            self.login_error_message = "Ingresa usuario y contraseña."
            return
        is_valid = login_logic.verificar_login(self.username_input, self.password_input)
        if is_valid:
            self.is_logged_in = True
            self.logged_in_username = self.username_input
            self.username_input = ""
            self.password_input = ""
        else:
            self.login_error_message = "Usuario o contraseña incorrectos."
            self.password_input = ""

    def logout(self):
        self.reset() # reset() es un método base de rx.State que limpia el estado

    # --- Placeholders otros Handlers ---
    # Estos handlers necesitarán ser implementados para llamar a la lógica del backend
    # y actualizar el estado (ej. resumen_content, mapa_mermaid_code, etc.)
    async def generate_summary(self):
        # Ejemplo: Llamar a resumen_logic, actualizar resumen_content/puntos_content
        # self.is_generating_resumen = True
        # result = resumen_logic.generar_resumen_logica(...)
        # if result['status'] == 'EXITO':
        #      self.resumen_content = result['resumen']
        #      self.puntos_content = result['puntos']
        # else:
        #      self.error_message_ui = result['message']
        # self.is_generating_resumen = False
        pass

    async def download_summary_pdf(self):
        # Ejemplo: Llamar a resumen_logic.generar_resumen_pdf_bytes
        # y usar rx.download para enviar los bytes al navegador
        pass

    async def generate_map(self):
        # Ejemplo: Llamar a map_logic, actualizar mapa_mermaid_code
        # self.is_generating_mapa = True
        # result = map_logic.generar_mapa_logica(...)
        # if result['status'] == 'EXITO':
        #     self.mapa_mermaid_code = result['mermaid_code']
        # else:
        #     self.error_message_ui = result['message']
        # self.is_generating_mapa = False
        pass

    async def start_evaluation(self):
        # Ejemplo: Llamar a eval_logic.generar_evaluacion_logica
        # actualizar eval_preguntas, resetear estado de evaluación
        # self.is_generating_eval = True
        # result = eval_logic.generar_evaluacion_logica(...)
        # if result['status'] == 'EXITO':
        #      self.eval_preguntas = result['preguntas']
        #      self.eval_current_idx = 0
        #      self.eval_user_answers = {}
        #      self.eval_score = None
        #      self.is_eval_active = True
        #      self.is_reviewing_eval = False
        # else:
        #      self.error_message_ui = result['message']
        # self.is_generating_eval = False
        pass

    def handle_answer_change(self, index: int, answer: typing.Union[str, list[str]]):
        # Actualizar self.eval_user_answers[index] = answer
        pass

    def next_question(self):
        # Incrementar self.eval_current_idx si no es la última pregunta
        pass

    async def submit_evaluation(self):
        # Calcular resultado con eval_logic.calcular_resultado_logica
        # Guardar resultado con eval_logic.guardar_resultado_evaluacion
        # Actualizar eval_score, eval_correct_count, is_eval_active=False, is_reviewing_eval=True
        pass

    async def load_stats(self):
        # Llamar a db_logic.obtener_historial y actualizar self.stats_history
        # self.is_loading_stats = True
        # self.stats_history = db_logic.obtener_historial(self.logged_in_username)
        # self.is_loading_stats = False
        pass

    def start_repaso(self, history_entry: dict):
        # Lógica para iniciar un repaso basado en una entrada del historial
        # Podría re-seleccionar el curso/libro/tema y quizás generar una nueva eval
        pass


# --- Fin AppState ---

# --- Definición de la Interfaz de Usuario (UI) ---


# --- PÁGINA DE LOGIN (Funcional) ---
def login_page() -> rx.Component:
    # (Sin cambios respecto al código original)
    return rx.container(
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon(
                        "brain-circuit", size=36, color_scheme=PRIMARY_COLOR_SCHEME
                    ),
                    rx.heading("SMART STUDENT", size="8", weight="bold"),
                    spacing="3",
                    align_items="center",
                    justify="center",
                    margin_bottom="0.5em",
                ),
                rx.heading(
                    "Inicio de Sesión", size="6", color_scheme="gray", weight="medium"
                ),
                rx.cond(
                    AppState.login_error_message != "",
                    rx.callout(
                        AppState.login_error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                        margin_y="1em",
                        size="2",
                    ),
                ),
                rx.form(
                    rx.vstack(
                        rx.input(
                            placeholder="Nombre de usuario",
                            value=AppState.username_input,
                            on_change=AppState.set_username_input,
                            name="username",
                            width="100%",
                            size="3",
                            required=True,
                            variant="surface",
                        ),
                        rx.input(
                            placeholder="Contraseña",
                            type="password",
                            value=AppState.password_input,
                            on_change=AppState.set_password_input,
                            name="password",
                            width="100%",
                            size="3",
                            required=True,
                            variant="surface",
                        ),
                        rx.button(
                            "Ingresar",
                            type="submit",
                            width="100%",
                            size="3",
                            color_scheme=PRIMARY_COLOR_SCHEME,
                            margin_top="1em",
                        ),
                        spacing="4",
                    ),
                    on_submit=AppState.handle_login,
                    reset_on_submit=False, # No resetea campos si login falla
                    width="100%",
                ),
                align="center",
                spacing="4",
            ),
            padding_x="2em",
            padding_y="3em",
            border="1px solid var(--accent-4)",
            border_radius="12px",
            box_shadow=f"0 10px 25px -5px rx.color('{PRIMARY_COLOR_SCHEME}', 3), 0 8px 10px -6px rx.color('{PRIMARY_COLOR_SCHEME}', 2)",
            max_width="450px",
            width="100%",
            background_color="var(--color-panel-solid)",
        ),
        display="flex",
        justify_content="center",
        padding_top="15vh",
        width="100%",
        min_height="100vh",
        background=f"radial-gradient(circle at top left, var(--accent-2), transparent 50%), radial-gradient(circle at bottom right, rx.color('{PRIMARY_COLOR_SCHEME}', 2), transparent 50%)",
    )


# --- Contenido de Pestañas (Simplificado - Necesita desarrollo) ---
# Aquí es donde construirías la UI para cada funcionalidad usando el AppState
def resumen_tab_content() -> rx.Component:
    # TODO: Añadir Selects para curso/libro/tema, Input para tema,
    # Checkbox para puntos, Botón 'Generar', Área para mostrar resumen/puntos,
    # Indicador de carga, Botón de descarga PDF.
    return rx.box(
        rx.vstack(
            rx.heading("Generador de Resúmenes", size="5"),
            rx.select(
                AppState.cursos_list,
                placeholder="Selecciona Curso...",
                value=AppState.selected_curso,
                on_change=AppState.set_selected_curso,
            ),
            # El select de libros debería actualizarse basado en selected_curso
            rx.cond(
                AppState.selected_curso,
                rx.select(
                   AppState.libros_para_curso,
                   placeholder="Selecciona Libro...",
                   value=AppState.selected_libro,
                   on_change=AppState.set_selected_libro,
                )
            ),
            rx.input(
                placeholder="Ingresa Tema Específico",
                value=AppState.selected_tema,
                on_change=AppState.set_selected_tema
            ),
            rx.checkbox(
                "Incluir Puntos Clave",
                checked=AppState.include_puntos,
                on_change=AppState.set_include_puntos,
            ),
            rx.button(
                "Generar Resumen",
                on_click=AppState.generate_summary,
                is_loading=AppState.is_generating_resumen,
                # Podrías deshabilitarlo si no se ha seleccionado curso/libro/tema
                # disabled=not(AppState.selected_curso and AppState.selected_libro and AppState.selected_tema)
            ),
             rx.cond(
                AppState.is_generating_resumen,
                 rx.circular_progress(is_indeterminate=True),
            ),
             rx.cond(
                AppState.resumen_content,
                 rx.box(
                    rx.heading("Resumen Generado", size="4"),
                    rx.text(AppState.resumen_content, white_space="pre-wrap"),
                    # ... (botón descarga) ...
                 )
             ),
            rx.cond(
                AppState.puntos_content,
                 rx.box(
                    rx.heading("Puntos Clave", size="4"),
                    rx.text(AppState.puntos_content, white_space="pre-wrap"),
                 )
             ),
            rx.cond(
                AppState.error_message_ui,
                rx.callout(AppState.error_message_ui, icon="triangle_alert", color_scheme="red"),
            ),
            spacing="3",
            align_items="start", # Alinear elementos a la izquierda
        ),
        padding="1em",
        width="100%"
    )


def mapa_tab_content() -> rx.Component:
    # TODO: Similar a Resúmenes (selects, input tema), Opción orientación (LR/TD),
    # Botón Generar, Área para mostrar mapa (usando rx.Component.mermaid o similar),
    # Indicador de carga.
    return rx.box(rx.text("Contenido Mapas Mentales (Pendiente)"), padding="1em")


def evaluacion_tab_content() -> rx.Component:
    # TODO: Selects, Input tema, Botón Iniciar Evaluación,
    # UI para mostrar pregunta actual (texto, opciones), Inputs para respuesta (radio/checkbox),
    # Botones Anterior/Siguiente/Finalizar, Muestra de puntaje/revisión.
    return rx.box(rx.text("Contenido Evaluación (Pendiente)"), padding="1em")


def estadisticas_tab_content() -> rx.Component:
    # TODO: Botón Cargar Historial, Tabla (rx.table) para mostrar stats_history,
    # Indicador de carga.
    return rx.box(rx.text("Contenido Estadísticas (Pendiente)"), padding="1em")


# --- DASHBOARD PRINCIPAL (Pestañas restauradas, estilos simplificados) ---
def main_dashboard() -> rx.Component:
    """Dashboard con pestañas funcionales y estilos simplificados."""
    return rx.vstack(
        # --- Barra Superior (Estilos mínimos) ---
        rx.hstack(
            rx.hstack(
                rx.icon("brain-circuit", size=24), # Ícono ajustado
                rx.heading("SMART", size="6", weight="bold"),
                rx.heading("STUDENT", size="6", weight="medium", color_scheme="gray"), # Estilo diferente
                spacing="1", # Menos espacio
                align_items="center",
            ),
            rx.spacer(),
            rx.text(f"Hola, {AppState.logged_in_username}!"),
            rx.button(
                "Cerrar Sesión",
                on_click=AppState.logout,
                size="2", # Botón más pequeño
                variant="soft", # Variante suave
                color_scheme="gray"
            ),
            width="100%",
            padding="0.8em 1.5em",  # Padding ajustado
            border_bottom="1px solid var(--accent-4)", # Borde más sutil
            background_color="var(--accent-1)", # Fondo leve
            align_items="center",
        ),
        # --- Fin Barra Superior ---

        # --- Sistema de Pestañas ---
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(rx.hstack(rx.icon("scroll-text", size=16), rx.text("Resúmenes"), spacing="2"), value="resumen"),
                rx.tabs.trigger(rx.hstack(rx.icon("git-fork", size=16), rx.text("Mapas"), spacing="2"), value="mapa"),
                rx.tabs.trigger(rx.hstack(rx.icon("clipboard-check", size=16), rx.text("Evaluación"), spacing="2"), value="evaluacion"),
                rx.tabs.trigger(rx.hstack(rx.icon("bar-chart-3", size=16), rx.text("Estadísticas"), spacing="2"), value="estadisticas"),
                width="100%",
                padding_x="1.5em",
                border_bottom="1px solid var(--accent-6)",
            ),
            # Contenido
            rx.box(
                rx.tabs.content(resumen_tab_content(), value="resumen"),
                rx.tabs.content(mapa_tab_content(), value="mapa"),
                rx.tabs.content(evaluacion_tab_content(), value="evaluacion"),
                rx.tabs.content(estadisticas_tab_content(), value="estadisticas"),
                padding_top="1em",
                padding_x="1.5em", # Padding horizontal consistente
                width="100%"
            ),
            defaultValue="resumen", # Pestaña inicial
            width="100%",
            flex_grow="1", # Para que ocupe el espacio vertical restante
        ),
        # --- Fin Sistema de Pestañas ---
        width="100%",
        height="calc(100vh - 50px)", # Ocupar altura menos la barra superior (ajustar 50px si cambia altura barra)
        align_items="stretch", # Estirar elementos verticalmente
        spacing="0", # Sin espacio entre barra y tabs
    )


# --- FUNCIÓN PRINCIPAL DE RENDERIZADO ---
def index() -> rx.Component:
    """La vista principal que muestra Login o el Dashboard."""
    return rx.fragment( # Usar fragment para evitar div extra innecesario
        rx.cond(
            AppState.is_logged_in,
            main_dashboard(),
            login_page(),
        ),
    )


# --- Crear e Inicializar la App ---
app = rx.App()
app.add_page(index, route="/")
# app.compile() # No es necesario llamar compile() explícitamente aquí, 'reflex run' lo hace