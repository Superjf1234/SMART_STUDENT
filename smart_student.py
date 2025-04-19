import reflex as rx
import asyncio  # Necesario para yield si se usa

# Importar lógica de backend
from backend import config_logic, resumen_logic, map_logic, eval_logic, db_logic

# Inicializar DB al arrancar la app
db_logic.inicializar_db()

# Importar nuevas pestañas
from mi_app_estudio.perfiles_ayuda import perfil_tab, ayuda_tab, ProfileHelpState

# --- Estado de la Aplicación ---
class State(rx.State):
    # ... (estado existente para login, resumen, mapa, historial) ...
    logged_in_user: str = ""
    login_error: str = ""
    show_login_error: bool = False

    # Estado para Resumen
    resumen_curso: str = ""
    resumen_libro: str = ""
    resumen_tema: str = ""
    resumen_gen_puntos: bool = True
    resumen_resultado: dict = {"resumen": "", "puntos": ""}
    resumen_loading: bool = False
    resumen_message: str = ""
    resumen_pdf_url: str = ""

    # Estado para Mapa Conceptual
    mapa_curso: str = ""
    mapa_libro: str = ""
    mapa_tema: str = ""
    mapa_orientation: str = "LR"
    mapa_mermaid_code: str = ""
    mapa_loading: bool = False
    mapa_message: str = ""
    mapa_html_url: str = ""
    mapa_pdf_url: str = ""

    # Estado para Historial
    historial_data: list[dict] = []
    historial_loading: bool = False

    # --- NUEVO: Estado para Evaluaciones ---
    eval_curso: str = ""
    eval_libro: str = ""
    eval_tema: str = ""
    eval_tipo_ui: str = "opcion_multiple" # Valor por defecto
    eval_preguntas: list[dict] = []
    eval_loading: bool = False
    eval_message: str = ""
    eval_status: str = "" # Para saber si fue EXITO o ERROR

    # --- Listas para Selectores ---
    @rx.cached_var
    def lista_cursos(self) -> list[str]:
        return config_logic.obtener_lista_cursos()

    @rx.cached_var
    def lista_libros_resumen(self) -> list[str]:
        return list(config_logic.CURSOS.get(self.resumen_curso, {}).keys())

    @rx.cached_var
    def lista_libros_mapa(self) -> list[str]:
        return list(config_logic.CURSOS.get(self.mapa_curso, {}).keys())

    # --- NUEVO: Lista de libros para Evaluaciones ---
    @rx.cached_var
    def lista_libros_eval(self) -> list[str]:
        return list(config_logic.CURSOS.get(self.eval_curso, {}).keys())

    # --- Lógica de Login ---
    async def handle_login(self, form_data: dict):
        # ... (código de handle_login existente) ...
        self.show_login_error = False
        self.login_error = ""
        username = form_data.get("username")
        password = form_data.get("password")

        if not username or not password:
            self.login_error = "Usuario y contraseña son requeridos."
            self.show_login_error = True
            return

        if config_logic.validar_credenciales(username, password):
            self.logged_in_user = username
            print(f"INFO (State): Usuario '{username}' logueado exitosamente.")
            # Cargar historial al loguearse
            await self.cargar_historial()
            # Podrías redirigir a la página principal aquí si tuvieras rutas
        else:
            self.login_error = "Credenciales inválidas."
            self.show_login_error = True
            print(f"WARN (State): Intento de login fallido para '{username}'.")

    def handle_logout(self):
        print(f"INFO (State): Usuario '{self.logged_in_user}' deslogueado.")
        self.logged_in_user = ""
        self.login_error = ""
        self.show_login_error = False
        # Limpiar otros estados si es necesario
        self.resumen_resultado = {"resumen": "", "puntos": ""}
        self.mapa_mermaid_code = ""
        self.historial_data = []
        self.eval_preguntas = []


    # --- Lógica de Resumen ---
    async def generar_resumen(self):
        # ... (código de generar_resumen existente) ...
        if not self.resumen_curso or not self.resumen_libro or not self.resumen_tema:
            self.resumen_message = "Por favor, selecciona curso, libro e ingresa un tema."
            return

        self.resumen_loading = True
        self.resumen_resultado = {"resumen": "", "puntos": ""} # Limpiar resultado anterior
        self.resumen_message = ""
        self.resumen_pdf_url = ""
        yield # Para que se actualice la UI mostrando el loading

        try:
            resultado_backend = await rx.call_module_method(
                resumen_logic.generar_resumen_logica, # Llama directamente a la función
                curso=self.resumen_curso,
                libro=self.resumen_libro,
                tema=self.resumen_tema,
                gen_puntos=self.resumen_gen_puntos
            )

            self.resumen_message = resultado_backend.get("message", "Error desconocido.")
            if resultado_backend.get("status") == "EXITO":
                self.resumen_resultado["resumen"] = resultado_backend.get("resumen", "")
                self.resumen_resultado["puntos"] = resultado_backend.get("puntos", "")
                # Generar PDF si hubo éxito
                pdf_bytes = await rx.call_module_method(
                    resumen_logic.generar_resumen_pdf_bytes,
                    resumen_txt=self.resumen_resultado["resumen"],
                    puntos_txt=self.resumen_resultado["puntos"],
                    titulo=f"Resumen: {self.resumen_tema}",
                    subtitulo=f"{self.resumen_curso} - {self.resumen_libro}"
                )
                if pdf_bytes:
                    self.resumen_pdf_url = rx.get_upload_url(f"resumen_{self.resumen_tema.replace(' ','_')}.pdf")
                    # Necesitas subir los bytes a la URL obtenida
                    # Esto requiere manejo adicional, por ahora solo guardamos la URL teórica
                    print(f"INFO (State): URL para PDF de resumen: {self.resumen_pdf_url}")
                    # Aquí iría la lógica para subir `pdf_bytes` a `self.resumen_pdf_url`
                    # Ejemplo conceptual (requiere implementar `upload_file`):
                    # await self.upload_file(self.resumen_pdf_url, pdf_bytes, "application/pdf")

            else:
                # Limpiar resultados si hubo error
                self.resumen_resultado = {"resumen": "", "puntos": ""}

        except Exception as e:
            self.resumen_message = f"Error inesperado en la interfaz: {e}"
            traceback.print_exc()
        finally:
            self.resumen_loading = False

    # --- Lógica de Mapa Conceptual ---
    async def generar_mapa(self):
        # ... (código de generar_mapa existente) ...
        if not self.mapa_curso or not self.mapa_libro or not self.mapa_tema:
            self.mapa_message = "Por favor, selecciona curso, libro e ingresa un tema."
            return

        self.mapa_loading = True
        self.mapa_mermaid_code = ""
        self.mapa_message = ""
        self.mapa_html_url = ""
        self.mapa_pdf_url = ""
        yield

        try:
            resultado_backend = await rx.call_module_method(
                map_logic.generar_mapa_logica,
                curso=self.mapa_curso,
                libro=self.mapa_libro,
                tema_usuario=self.mapa_tema,
                selected_orientation=self.mapa_orientation
            )
            self.mapa_message = resultado_backend.get("message", "Error desconocido.")
            if resultado_backend.get("status") == "EXITO":
                self.mapa_mermaid_code = resultado_backend.get("mermaid_code", "")
                # Generar visualización HTML y PDF si hay código
                if self.mapa_mermaid_code:
                    self.mapa_html_url = await rx.call_module_method(
                        map_logic.generar_visualizacion_html,
                        mermaid_code=self.mapa_mermaid_code,
                        tema=self.mapa_tema
                    )
                    pdf_bytes = await rx.call_module_method(
                        map_logic.generar_mapa_pdf_bytes,
                        mermaid_code=self.mapa_mermaid_code,
                        tema=self.mapa_tema,
                        curso=self.mapa_curso,
                        libro=self.mapa_libro
                    )
                    if pdf_bytes:
                        self.mapa_pdf_url = rx.get_upload_url(f"mapa_{self.mapa_tema.replace(' ','_')}.pdf")
                        print(f"INFO (State): URL para PDF de mapa: {self.mapa_pdf_url}")
                        # Aquí iría la lógica para subir `pdf_bytes` a `self.mapa_pdf_url`
                        # await self.upload_file(self.mapa_pdf_url, pdf_bytes, "application/pdf")

            else:
                self.mapa_mermaid_code = "" # Limpiar si falla

        except Exception as e:
            self.mapa_message = f"Error inesperado en la interfaz: {e}"
            traceback.print_exc()
        finally:
            self.mapa_loading = False

    # --- Lógica de Historial ---
    async def cargar_historial(self):
        # ... (código de cargar_historial existente) ...
        if not self.logged_in_user:
            return # No cargar si no hay usuario

        self.historial_loading = True
        yield
        try:
            # Llama directamente a la función de db_logic
            self.historial_data = await rx.call_module_method(
                db_logic.obtener_historial,
                username=self.logged_in_user
            )
        except Exception as e:
            print(f"ERROR (State): Cargando historial - {e}")
            traceback.print_exc()
            self.historial_data = [] # Limpiar en caso de error
        finally:
            self.historial_loading = False

    # --- NUEVO: Lógica de Evaluaciones ---
    async def generar_evaluacion(self):
        """Manejador para generar la evaluación."""
        if not self.eval_curso or not self.eval_libro or not self.eval_tema:
            self.eval_message = "Por favor, selecciona curso, libro, ingresa un tema y tipo de pregunta."
            self.eval_status = "ERROR_INPUT"
            return

        self.eval_loading = True
        self.eval_preguntas = [] # Limpiar preguntas anteriores
        self.eval_message = ""
        self.eval_status = ""
        yield # Actualizar UI para mostrar loading

        try:
            print(f"INFO (State): Llamando a generar_evaluacion_funcional con C={self.eval_curso}, L={self.eval_libro}, T={self.eval_tema}, Tipo={self.eval_tipo_ui}")
            # Llamar directamente a la función del backend
            resultado_backend = await rx.call_module_method(
                eval_logic.generar_evaluacion_funcional,
                curso=self.eval_curso,
                libro=self.eval_libro,
                tema=self.eval_tema,
                tipo_ui=self.eval_tipo_ui
            )

            self.eval_status = resultado_backend.get("status", "ERROR")
            self.eval_message = resultado_backend.get("message", "Error desconocido al generar evaluación.")
            
            if self.eval_status == "EXITO":
                self.eval_preguntas = resultado_backend.get("preguntas", [])
                if not self.eval_preguntas:
                     # Si el status es EXITO pero no hay preguntas, ajustar mensaje si no lo hizo el backend
                     if not self.eval_message or "Generadas 0" in self.eval_message:
                          self.eval_message = f"No se encontraron preguntas de tipo '{self.eval_tipo_ui}' para el tema '{self.eval_tema}'."
            else:
                # Limpiar preguntas si hubo error
                self.eval_preguntas = []
                print(f"ERROR (State): Generando evaluación - Status: {self.eval_status}, Msg: {self.eval_message}")


        except Exception as e:
            self.eval_status = "ERROR_INESPERADO"
            self.eval_message = f"Error inesperado en la interfaz al generar evaluación: {e}"
            self.eval_preguntas = []
            print(f"ERROR (State): Excepción generando evaluación - {e}")
            traceback.print_exc()
        finally:
            self.eval_loading = False
            print(f"INFO (State): Generación de evaluación finalizada. Status: {self.eval_status}")

    # --- Limpieza de campos al cambiar curso ---
    def on_change_curso_resumen(self, value: str):
        self.resumen_curso = value
        self.resumen_libro = "" # Limpiar libro
        self.resumen_tema = "" # Limpiar tema
        self.resumen_resultado = {"resumen": "", "puntos": ""} # Limpiar resultado
        self.resumen_message = ""
        self.resumen_pdf_url = ""

    def on_change_curso_mapa(self, value: str):
        self.mapa_curso = value
        self.mapa_libro = ""
        self.mapa_tema = ""
        self.mapa_mermaid_code = ""
        self.mapa_message = ""
        self.mapa_html_url = ""
        self.mapa_pdf_url = ""

    # --- NUEVO: Limpieza para Evaluaciones ---
    def on_change_curso_eval(self, value: str):
        self.eval_curso = value
        self.eval_libro = ""
        self.eval_tema = ""
        self.eval_preguntas = []
        self.eval_message = ""
        self.eval_status = ""

    def on_change_libro_eval(self, value: str):
        self.eval_libro = value
        # Podríamos limpiar el tema si quisiéramos
        # self.eval_tema = ""
        self.eval_preguntas = []
        self.eval_message = ""
        self.eval_status = ""

    # --- Helpers para deshabilitar botones ---
    @rx.var
    def resumen_campos_incompletos(self) -> bool:
        return not self.resumen_curso or not self.resumen_libro or not self.resumen_tema.strip()

    @rx.var
    def mapa_campos_incompletos(self) -> bool:
        return not self.mapa_curso or not self.mapa_libro or not self.mapa_tema.strip()

    # --- NUEVO: Helper para Evaluaciones ---
    @rx.var
    def eval_campos_incompletos(self) -> bool:
        return not self.eval_curso or not self.eval_libro or not self.eval_tema.strip()


# --- Componentes de UI ---

def selector_comun(label: str, placeholder: str, items: rx.Var[list[str]], on_change: callable, value: rx.Var[str], is_disabled: rx.Var[bool] = False) -> rx.Component:
    # ... (selector_comun existente) ...
    return rx.form_control(
        rx.form_label(label),
        rx.select(
            items=items,
            placeholder=placeholder,
            on_change=on_change,
            value=value,
            is_disabled=is_disabled,
        ),
        width="100%",
    )

def input_comun(label: str, placeholder: str, on_change: callable, value: rx.Var[str], is_disabled: rx.Var[bool] = False) -> rx.Component:
    # ... (input_comun existente) ...
     return rx.form_control(
        rx.form_label(label),
        rx.input(
            placeholder=placeholder,
            on_change=on_change,
            value=value,
            is_disabled=is_disabled,
        ),
        width="100%",
    )

def login_form() -> rx.Component:
    # ... (login_form existente) ...
    return rx.center(
        rx.vstack(
            rx.heading("Iniciar Sesión", size="lg", margin_bottom="1em"),
            rx.form(
                rx.vstack(
                    rx.form_control(
                        rx.form_label("Usuario"),
                        rx.input(name="username", placeholder="Nombre de usuario"),
                        is_required=True,
                    ),
                    rx.form_control(
                        rx.form_label("Contraseña"),
                        rx.input(name="password", type="password", placeholder="Contraseña"),
                        is_required=True,
                    ),
                    rx.cond(
                        State.show_login_error,
                        rx.callout(
                            State.login_error,
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                            margin_top="1em",
                        )
                    ),
                    rx.button("Entrar", type="submit", width="100%", margin_top="1em"),
                ),
                on_submit=State.handle_login,
            ),
            align="center",
            bg="white",
            padding="2em",
            shadow="lg",
            border_radius="md",
            width=["90%", "60%", "40%"], # Responsive width
        ),
        height="100vh",
        bg="gray.100",
    )

def seccion_resumen() -> rx.Component:
    # ... (seccion_resumen existente) ...
    return rx.vstack(
        rx.heading("Generador de Resúmenes", size="md", margin_bottom="1em"),
        rx.hstack(
            selector_comun("Curso:", "Selecciona curso...", State.lista_cursos, State.on_change_curso_resumen, State.resumen_curso),
            selector_comun("Libro:", "Selecciona libro...", State.lista_libros_resumen, State.set_resumen_libro, State.resumen_libro, is_disabled=~State.resumen_curso),
            width="100%",
            spacing="4",
        ),
        input_comun("Tema:", "Ingresa el tema del resumen", State.set_resumen_tema, State.resumen_tema, is_disabled=~State.resumen_libro),
        rx.checkbox("Generar Puntos Clave", on_change=State.set_resumen_gen_puntos, is_checked=State.resumen_gen_puntos, margin_y="1em"),
        rx.button(
            "Generar Resumen",
            on_click=State.generar_resumen,
            is_loading=State.resumen_loading,
            is_disabled=State.resumen_campos_incompletos | State.resumen_loading,
            width="100%",
        ),
        rx.cond(
            State.resumen_loading,
            rx.center(rx.circular_progress(is_indeterminate=True), padding="2em")
        ),
        rx.cond(
            State.resumen_message,
            rx.callout(
                State.resumen_message,
                icon="info",
                color_scheme="teal" if "EXITO" in State.resumen_message else "orange",
                width="100%",
                margin_top="1em",
            )
        ),
        rx.cond(
            State.resumen_resultado["resumen"] | State.resumen_resultado["puntos"],
            rx.box(
                rx.cond(
                    State.resumen_pdf_url,
                     rx.link(
                        rx.button("Descargar PDF", left_icon=rx.icon("download"), color_scheme="green"),
                        href=State.resumen_pdf_url,
                        is_external=True,
                        margin_bottom="1em"
                    )
                ),
                rx.cond(
                    State.resumen_resultado["resumen"],
                    rx.vstack(
                        rx.heading("Resumen Generado", size="sm", margin_bottom="0.5em"),
                        rx.text(State.resumen_resultado["resumen"], white_space="pre-wrap"),
                        align_items="flex-start",
                        width="100%",
                        border="1px solid #e2e8f0",
                        padding="1em",
                        border_radius="md",
                        margin_bottom="1em",
                    )
                ),
                rx.cond(
                    State.resumen_resultado["puntos"],
                    rx.vstack(
                        rx.heading("Puntos Clave", size="sm", margin_bottom="0.5em"),
                        rx.text(State.resumen_resultado["puntos"], white_space="pre-wrap"),
                        align_items="flex-start",
                        width="100%",
                        border="1px solid #e2e8f0",
                        padding="1em",
                        border_radius="md",
                    )
                ),
                width="100%",
                margin_top="1em",
            )
        ),
        width="100%",
        spacing="4",
        align_items="flex-start",
    )

def seccion_mapa() -> rx.Component:
    # ... (seccion_mapa existente) ...
    return rx.vstack(
        rx.heading("Generador de Mapas Conceptuales", size="md", margin_bottom="1em"),
        rx.hstack(
            selector_comun("Curso:", "Selecciona curso...", State.lista_cursos, State.on_change_curso_mapa, State.mapa_curso),
            selector_comun("Libro:", "Selecciona libro...", State.lista_libros_mapa, State.set_mapa_libro, State.mapa_libro, is_disabled=~State.mapa_curso),
            width="100%",
            spacing="4",
        ),
        input_comun("Tema:", "Ingresa el tema central", State.set_mapa_tema, State.mapa_tema, is_disabled=~State.mapa_libro),
        rx.form_control(
            rx.form_label("Orientación del Mapa"),
            rx.select(
                ["LR", "TD"], # Left-to-Right, Top-Down
                placeholder="Selecciona orientación",
                on_change=State.set_mapa_orientation,
                value=State.mapa_orientation,
            ),
            width="100%",
        ),
        rx.button(
            "Generar Mapa",
            on_click=State.generar_mapa,
            is_loading=State.mapa_loading,
            is_disabled=State.mapa_campos_incompletos | State.mapa_loading,
            width="100%",
        ),
        rx.cond(
            State.mapa_loading,
            rx.center(rx.circular_progress(is_indeterminate=True), padding="2em")
        ),
        rx.cond(
            State.mapa_message,
            rx.callout(
                State.mapa_message,
                icon="info",
                color_scheme="teal" if "EXITO" in State.mapa_message else "orange",
                width="100%",
                margin_top="1em",
            )
        ),
        rx.cond(
            State.mapa_mermaid_code,
            rx.box(
                 rx.hstack(
                    rx.cond(
                        State.mapa_html_url,
                        rx.link(
                            rx.button("Ver Mapa Interactivo", left_icon=rx.icon("eye"), color_scheme="blue"),
                            href=State.mapa_html_url,
                            is_external=True,
                        )
                    ),
                    rx.cond(
                        State.mapa_pdf_url,
                        rx.link(
                            rx.button("Descargar PDF", left_icon=rx.icon("download"), color_scheme="green"),
                            href=State.mapa_pdf_url,
                            is_external=True,
                        )
                    ),
                    spacing="4",
                    margin_bottom="1em",
                ),
                # Usar rx.html para renderizar el código Mermaid si es posible,
                # o mostrar el código como texto si no hay integración directa.
                # rx.markdown(f"```mermaid\n{State.mapa_mermaid_code}\n```"), # Si markdown soporta mermaid
                rx.code_block(
                    State.mapa_mermaid_code,
                    language="mermaid",
                    show_line_numbers=False,
                    can_copy=True,
                    width="100%",
                    border="1px solid #e2e8f0",
                    padding="1em",
                    border_radius="md",
                ),
                width="100%",
                margin_top="1em",
            )
        ),
        width="100%",
        spacing="4",
        align_items="flex-start",
    )

def seccion_historial() -> rx.Component:
    # ... (seccion_historial existente) ...
    return rx.vstack(
        rx.heading("Historial de Evaluaciones", size="md", margin_bottom="1em"),
        rx.button("Recargar Historial", on_click=State.cargar_historial, is_loading=State.historial_loading, margin_bottom="1em"),
        rx.cond(
            State.historial_loading,
            rx.center(rx.circular_progress(is_indeterminate=True), padding="2em")
        ),
        rx.cond(
            ~State.historial_loading & ~State.historial_data,
            rx.callout("No hay historial de evaluaciones para mostrar.", icon="info")
        ),
        rx.cond(
            State.historial_data,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Fecha"),
                        rx.table.column_header_cell("Curso"),
                        rx.table.column_header_cell("Libro"),
                        rx.table.column_header_cell("Tema"),
                        rx.table.column_header_cell("Nota"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        State.historial_data,
                        lambda item: rx.table.row(
                            rx.table.cell(item["fecha"]),
                            rx.table.cell(item["curso"]),
                            rx.table.cell(item["libro"]),
                            rx.table.cell(item["tema"]),
                            rx.table.cell(item["nota"]),
                        )
                    )
                ),
                variant="surface", # Estilo de tabla
                width="100%",
            )
        ),
        width="100%",
        align_items="flex-start",
    )

# --- NUEVO: Componente para la sección de Evaluaciones ---
def seccion_evaluaciones() -> rx.Component:
    """UI para la pestaña de generación de evaluaciones."""
    return rx.vstack(
        rx.heading("Generador de Evaluaciones", size="md", margin_bottom="1em"),
        # Selectores de Curso y Libro
        rx.hstack(
            selector_comun(
                "Curso:",
                "Selecciona curso...",
                State.lista_cursos,
                State.on_change_curso_eval, # Usa el handler específico
                State.eval_curso
            ),
            selector_comun(
                "Libro:",
                "Selecciona libro...",
                State.lista_libros_eval, # Usa la lista específica
                State.on_change_libro_eval, # Usa el handler específico
                State.eval_libro,
                is_disabled=~State.eval_curso # Deshabilitado si no hay curso
            ),
            width="100%",
            spacing="4",
        ),
        # Input para el Tema
        input_comun(
            "Tema:",
            "Ingresa el tema de la evaluación",
            State.set_eval_tema,
            State.eval_tema,
            is_disabled=~State.eval_libro # Deshabilitado si no hay libro
        ),
        # Selector para Tipo de Pregunta
        rx.form_control(
            rx.form_label("Tipo de Pregunta"),
            rx.select(
                [
                    {"value": "opcion_multiple", "label": "Opción Múltiple (1 correcta)"},
                    {"value": "seleccion_multiple", "label": "Selección Múltiple (Varias correctas)"},
                ],
                placeholder="Selecciona tipo...",
                on_change=State.set_eval_tipo_ui,
                value=State.eval_tipo_ui,
                is_disabled=~State.eval_libro # Deshabilitado si no hay libro
            ),
            width="100%",
        ),
        # Botón para Generar
        rx.button(
            "Generar Evaluación",
            on_click=State.generar_evaluacion,
            is_loading=State.eval_loading,
            is_disabled=State.eval_campos_incompletos | State.eval_loading,
            width="100%",
            margin_top="1em",
        ),
        # Indicador de Carga
        rx.cond(
            State.eval_loading,
            rx.center(rx.circular_progress(is_indeterminate=True), padding="2em")
        ),
        # Mensaje de Estado/Error
        rx.cond(
            State.eval_message,
            rx.callout(
                State.eval_message,
                icon="info" if State.eval_status == "EXITO" else "triangle_alert",
                color_scheme="teal" if State.eval_status == "EXITO" else "orange",
                width="100%",
                margin_top="1em",
            )
        ),
        # Área para mostrar Preguntas
        rx.cond(
            ~State.eval_loading & State.eval_preguntas,
            rx.vstack(
                rx.heading("Preguntas Generadas", size="sm", margin_top="1.5em", margin_bottom="1em"),
                rx.foreach(
                    State.eval_preguntas,
                    lambda pregunta, index: rx.box(
                        rx.heading(f"Pregunta {index + 1}: {pregunta['pregunta']}", size="xs", margin_bottom="0.5em"),
                        rx.vstack(
                            rx.foreach(
                                pregunta["opciones"],
                                lambda opcion: rx.text(f"{opcion['id']}) {opcion['texto']}")
                            ),
                            align_items="flex-start",
                            margin_bottom="0.5em",
                        ),
                        # Opcional: Mostrar respuesta correcta y explicación (quizás ocultable)
                        rx.accordion.root(
                             rx.accordion.item(
                                 rx.accordion.trigger(
                                     rx.hstack(
                                         rx.text("Mostrar Respuesta y Explicación"),
                                         rx.spacer(),
                                         rx.accordion.icon(),
                                     ),
                                     width="100%",
                                 ),
                                 rx.accordion.content(
                                     rx.vstack(
                                         rx.text(f"Respuesta(s) Correcta(s): {pregunta['respuesta_correcta']}"),
                                         rx.text("Explicación:", font_weight="bold"),
                                         rx.text(pregunta['explicacion'], white_space="pre-wrap"),
                                         align_items="flex-start",
                                     )
                                 ),
                             ),
                             collapsible=True,
                             type="single",
                             margin_top="0.5em",
                         ),
                        border="1px solid #e2e8f0",
                        padding="1em",
                        border_radius="md",
                        margin_bottom="1em",
                        width="100%",
                    )
                ),
                width="100%",
                align_items="flex-start",
            )
        ),
        width="100%",
        spacing="4",
        align_items="flex-start",
    )


# --- Página Principal ---
def index() -> rx.Component:
    return rx.cond(
        State.logged_in_user == "",
        login_form(),
        rx.container(
            rx.hstack(
                rx.heading("SMART STUDENT", size="lg"),
                rx.spacer(),
                rx.text(f"Usuario: {State.logged_in_user}"),
                rx.button("Salir", on_click=State.handle_logout, color_scheme="red", variant="soft"),
                align="center",
                width="100%",
                padding_y="1em",
                border_bottom="1px solid #e2e8f0",
                margin_bottom="1em",
            ),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Resumen", value="resumen"),
                    rx.tabs.trigger("Mapa Conceptual", value="mapa"),
                    rx.tabs.trigger("Evaluaciones", value="evaluaciones"),
                    rx.tabs.trigger("Historial", value="historial"),
                    rx.tabs.trigger("Perfil", value="perfil"),
                    rx.tabs.trigger("Ayuda", value="ayuda"),
                ),
                rx.tabs.content(seccion_resumen(), value="resumen"),
                rx.tabs.content(seccion_mapa(), value="mapa"),
                rx.tabs.content(seccion_evaluaciones(), value="evaluaciones"),
                rx.tabs.content(seccion_historial(), value="historial"),
                rx.tabs.content(perfil_tab(), value="perfil"),
                rx.tabs.content(ayuda_tab(), value="ayuda"),
                defaultValue="resumen", # Pestaña por defecto
                width="100%",
            ),
            padding_x="1em", # Padding horizontal para el contenedor
            max_width="1200px", # Ancho máximo
        )
    )


# --- Configuración de la App ---
app = rx.App(state=State)
app.add_page(index)
