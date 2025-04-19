"""
Módulo para las pestañas de Perfil y Ayuda de SMART_STUDENT.

Este módulo contiene la funcionalidad para:
- Perfil: Visualización y edición de datos del usuario
- Ayuda: Información sobre el uso de la aplicación
"""

import reflex as rx
from typing import Dict, List, Optional
from mi_app_estudio.state import AppState, BACKEND_AVAILABLE, db_logic, error_callout, PRIMARY_COLOR_SCHEME, ACCENT_COLOR_SCHEME

# --- Constantes ---
SECTIONS = {
    "perfil": "Perfil de Usuario",
    "ayuda": "Ayuda y Soporte"
}

# Diccionario para tipos de usuario
USER_TYPES = {
    "estudiante": "Estudiante",
    "profesor": "Profesor",
    "admin": "Administrador"
}

# URL de imágenes predeterminadas para perfiles
DEFAULT_PROFILE_IMAGE = "https://uxwing.com/wp-content/themes/uxwing/download/peoples-avatars/default-profile-picture-grey-male-icon.png"

class ProfileHelpState(AppState):
    """Estado específico para las funcionalidades de Perfil y Ayuda."""
    
    # --- Perfil ---
    is_editing_profile: bool = False
    profile_success_message: str = ""
    profile_error_message: str = ""
    
    # Información del perfil (editable)
    nombre_completo: str = ""
    email: str = ""
    curso_actual: str = ""
    tipo_usuario: str = "estudiante"
    profile_image_url: str = DEFAULT_PROFILE_IMAGE
    
    # --- Ayuda ---
    selected_help_section: str = "uso"  # Sección de ayuda seleccionada por defecto
    selected_faq_item: str = ""  # Pregunta frecuente seleccionada
    
    # --- Estadísticas ---
    stats_loading: bool = False
    evaluaciones_totales: int = 0
    nota_promedio: float = 0.0
    
    def toggle_edit_mode(self):
        """Alterna entre modo visualización y edición del perfil."""
        self.is_editing_profile = not self.is_editing_profile
        if not self.is_editing_profile:
            # Si estamos saliendo del modo edición, limpiar mensajes
            self.profile_success_message = ""
            self.profile_error_message = ""
    
    def set_nombre_completo(self, value: str):
        self.nombre_completo = value
        
    def set_email(self, value: str):
        self.email = value
        
    def set_curso_actual(self, value: str):
        self.curso_actual = value
    
    def set_tipo_usuario(self, value: str):
        if value in USER_TYPES:
            self.tipo_usuario = value
    
    def set_profile_image(self, value: str):
        if value and isinstance(value, str):
            self.profile_image_url = value
        else:
            self.profile_image_url = DEFAULT_PROFILE_IMAGE
    
    def set_help_section(self, section: str):
        """Cambia la sección de ayuda activa."""
        self.selected_help_section = section
    
    def set_faq_item(self, item: str):
        """Selecciona una pregunta frecuente para mostrar su respuesta."""
        if self.selected_faq_item == item:
            # Si se hace clic en el mismo ítem, se cierra
            self.selected_faq_item = ""
        else:
            self.selected_faq_item = item
    
    async def load_user_profile(self):
        """Carga la información del perfil desde la base de datos."""
        if not self.logged_in_username:
            self.profile_error_message = "No hay usuario con sesión iniciada."
            return
            
        # Si tuvieras una función en db_logic para obtener perfil:
        if BACKEND_AVAILABLE and hasattr(db_logic, "obtener_perfil_usuario"):
            try:
                # Ejemplo: profile_data = await db_logic.obtener_perfil_usuario(self.logged_in_username)
                # Simularemos con datos de ejemplo
                # En un caso real, esto se obtendría de la base de datos
                self.nombre_completo = f"{self.logged_in_username.title()} Apellido"
                self.email = f"{self.logged_in_username}@ejemplo.com"
                self.curso_actual = "4to Medio"  # Podría provenir de preferencias guardadas
                self.tipo_usuario = "estudiante"  # Por defecto
                # En un caso real, la URL de la imagen también vendría de la base de datos
                self.profile_image_url = DEFAULT_PROFILE_IMAGE
            except Exception as e:
                self.profile_error_message = f"Error al cargar datos: {str(e)}"
        else:
            # Datos simulados si no hay backend o función
            self.nombre_completo = f"{self.logged_in_username.title()} Apellido"
            self.email = f"{self.logged_in_username}@ejemplo.com"
            self.curso_actual = "4to Medio"
            self.tipo_usuario = "estudiante"
            self.profile_image_url = DEFAULT_PROFILE_IMAGE
    
    async def save_profile(self):
        """Guarda los cambios del perfil en la base de datos."""
        if not self.logged_in_username:
            self.profile_error_message = "No hay usuario con sesión iniciada."
            return
            
        # Validaciones básicas
        if not self.email or "@" not in self.email:
            self.profile_error_message = "El email no es válido."
            return
            
        if not self.nombre_completo.strip():
            self.profile_error_message = "El nombre no puede estar vacío."
            return
        
        # Si tuvieras una función en db_logic para guardar perfil:
        if BACKEND_AVAILABLE and hasattr(db_logic, "guardar_perfil_usuario"):
            try:
                # Ejemplo: await db_logic.guardar_perfil_usuario(
                #     self.logged_in_username, 
                #     {
                #         "nombre_completo": self.nombre_completo,
                #         "email": self.email,
                #         "curso_actual": self.curso_actual,
                #         "tipo_usuario": self.tipo_usuario,
                #         "profile_image_url": self.profile_image_url
                #     }
                # )
                # Simulación exitosa:
                self.profile_success_message = "¡Perfil actualizado correctamente!"
                self.profile_error_message = ""
                self.is_editing_profile = False  # Salir del modo edición
            except Exception as e:
                self.profile_error_message = f"Error al guardar: {str(e)}"
                self.profile_success_message = ""
        else:
            # Simulación exitosa sin backend
            self.profile_success_message = "¡Perfil actualizado correctamente! (Simulado)"
            self.profile_error_message = ""
            self.is_editing_profile = False  # Salir del modo edición
    
    async def load_user_stats(self):
        """Carga estadísticas del usuario desde la base de datos."""
        if not self.logged_in_username:
            return
            
        self.stats_loading = True
        yield  # Actualizar UI con indicador de carga
        
        try:
            # Obtener estadísticas del usuario
            if BACKEND_AVAILABLE and hasattr(db_logic, "obtener_estadisticas_usuario"):
                stats_raw = db_logic.obtener_estadisticas_usuario(self.logged_in_username)
                
                # Manejar tanto diccionarios como listas
                if isinstance(stats_raw, dict):
                    # Si recibimos un diccionario con resumen de estadísticas
                    self.evaluaciones_totales = stats_raw.get("total_evaluaciones", 0)
                    self.nota_promedio = stats_raw.get("nota_promedio", 0.0)
                elif isinstance(stats_raw, list) and stats_raw:
                    # Si recibimos una lista de evaluaciones, calculamos el resumen
                    self.evaluaciones_totales = len(stats_raw)
                    puntuaciones = [float(s.get("puntuacion", 0.0)) for s in stats_raw if s.get("puntuacion") is not None]
                    self.nota_promedio = sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0.0
                else:
                    # Si no hay datos o formato desconocido
                    self.evaluaciones_totales = 0
                    self.nota_promedio = 0.0
            else:
                # Datos simulados si no hay backend
                import random
                self.evaluaciones_totales = random.randint(5, 15)
                self.nota_promedio = random.uniform(4.0, 6.5)
        except Exception as e:
            print(f"Error cargando estadísticas: {e}")
            self.evaluaciones_totales = 0
            self.nota_promedio = 0.0
        finally:
            self.stats_loading = False
            yield  # Actualizar UI con datos cargados


# --- Componentes de UI para Perfil ---
def perfil_tab():
    """Contenido de la pestaña de perfil."""
    return rx.vstack(
        rx.heading("👤 Perfil y Progreso", size="6", mb="2em", text_align="center"),
        rx.text(
            "Consulta y administra tu información personal y progreso académico.",
            color="gray.500",
            mb="2em",
            text_align="center",
            max_width="600px",
        ),
        error_callout(AppState.error_message_ui),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.image(
                            src="/assets/tmprsubw3bf.png",  # Imagen de perfil predeterminada
                            alt="Foto de perfil",
                            border_radius="full",
                            box_size="100px",
                        ),
                        text_align="center",
                    ),
                    rx.vstack(
                        rx.text(f"Nombre: {AppState.logged_in_username}", size="3"),
                        rx.text("Email: usuario@ejemplo.com", size="3"),
                        rx.text("Tipo de Usuario: Estudiante", size="3"),
                        rx.text("Curso Actual: 8vo Básico", size="3"),
                        spacing="1",
                        align_items="flex-start",
                    ),
                    spacing="6",
                    align_items="center",
                ),
                rx.button(
                    "Editar Perfil",
                    size="3",
                    color_scheme="blue",
                    width="100%",
                    margin_top="1em",
                ),
                width="100%",
                spacing="4",
                padding="2em",
            ),
            variant="surface",
            width="100%",
            max_width="500px",
        ),
        rx.card(
            rx.vstack(
                rx.heading("Estadísticas de Progreso", size="5", mb="1em"),
                rx.cond(
                    AppState.is_loading_stats,
                    rx.spinner(size="lg"),
                    rx.vstack(
                        rx.foreach(
                            AppState.stats_history,
                            lambda stat: rx.box(
                                rx.text(f"Tema: {stat['tema']}", size="3"),
                                rx.text(f"Curso: {stat['curso']}", size="3"),
                                rx.text(f"Libro: {stat['libro']}", size="3"),
                                rx.text(f"Puntuación: {stat['puntuacion']}%", size="3"),
                                rx.text(f"Fecha: {stat['fecha']}", size="3"),
                                border="1px solid var(--gray-4)",
                                border_radius="medium",
                                padding="1em",
                                margin_bottom="1em",
                            ),
                        ),
                        spacing="4",
                    ),
                ),
                rx.button(
                    "Actualizar Estadísticas",
                    size="3",
                    color_scheme="green",
                    width="100%",
                    margin_top="1em",
                    on_click=AppState.load_stats,
                ),
                width="100%",
                spacing="4",
                padding="2em",
            ),
            variant="surface",
            width="100%",
            max_width="800px",
            margin_top="2em",
        ),
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="5em",
    )


# --- Componentes de UI para Ayuda ---
def ayuda_tab():
    """Contenido de la pestaña de ayuda y soporte."""
    return rx.vstack(
        rx.heading("❓ Ayuda y Soporte", size="6", mb="2em", text_align="center"),
        
        rx.card(
            rx.vstack(
                # Pestañas de secciones de ayuda
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("Uso de la aplicación", value="uso"),
                        rx.tabs.trigger("Preguntas Frecuentes", value="faq"),
                        rx.tabs.trigger("Acerca de", value="about"),
                        rx.tabs.trigger("Contacto", value="contacto"),
                    ),
                    
                    # Sección: Uso de la aplicación
                    rx.tabs.content(
                        rx.vstack(
                            rx.heading("¿Cómo usar SMART STUDENT?", size="4", mb="1em"),
                            
                            rx.accordion.root(
                                rx.accordion.item(
                                    rx.accordion.trigger("Creación de resúmenes"),
                                    rx.accordion.content(
                                        rx.vstack(
                                            rx.text("Para crear un resumen:"),
                                            rx.ordered_list(
                                                rx.list_item("Selecciona un curso y libro del material disponible."),
                                                rx.list_item("Escribe el tema específico que deseas resumir."),
                                                rx.list_item("Opcionalmente, marca la casilla para incluir puntos clave."),
                                                rx.list_item("Haz clic en \"Generar Resumen\" y espera a que se procese."),
                                                rx.list_item("El resumen generado aparecerá abajo y podrás descargarlo en PDF."),
                                            ),
                                            rx.text("Los resúmenes generados son personalizados según el contenido del libro y tema seleccionados."),
                                            align_items="start",
                                            width="100%",
                                        )
                                    ),
                                    value="resumen",
                                ),
                                rx.accordion.item(
                                    rx.accordion.trigger("Mapas conceptuales"),
                                    rx.accordion.content(
                                        rx.vstack(
                                            rx.text("Para crear un mapa conceptual:"),
                                            rx.ordered_list(
                                                rx.list_item("Primero debes generar un resumen como se indica arriba."),
                                                rx.list_item("Luego, ve a la pestaña de \"Mapa Conceptual\"."),
                                                rx.list_item("Haz clic en \"Generar Mapa\" y espera a que se procese."),
                                                rx.list_item("El mapa conceptual aparecerá como una imagen que puedes descargar."),
                                            ),
                                            rx.text("Los mapas utilizan la información del resumen para crear una representación visual de los conceptos clave."),
                                            align_items="start",
                                            width="100%",
                                        )
                                    ),
                                    value="mapa",
                                ),
                                rx.accordion.item(
                                    rx.accordion.trigger("Evaluaciones"),
                                    rx.accordion.content(
                                        rx.vstack(
                                            rx.text("Para realizar una evaluación:"),
                                            rx.ordered_list(
                                                rx.list_item("Primero debes generar un resumen como se indica arriba."),
                                                rx.list_item("Luego, ve a la pestaña de \"Evaluaciones\"."),
                                                rx.list_item("Haz clic en \"Crear Evaluación\" y espera a que se generen las preguntas."),
                                                rx.list_item("Contesta las preguntas una por una, usando los botones de navegación."),
                                                rx.list_item("Al finalizar, verás tu puntuación y podrás revisar las respuestas correctas."),
                                            ),
                                            rx.text("Las evaluaciones te permiten comprobar tu comprensión del tema resumido."),
                                            align_items="start",
                                            width="100%",
                                        )
                                    ),
                                    value="evaluacion",
                                ),
                                rx.accordion.item(
                                    rx.accordion.trigger("Historial"),
                                    rx.accordion.content(
                                        rx.vstack(
                                            rx.text("Para revisar tu historial:"),
                                            rx.ordered_list(
                                                rx.list_item("Ve a la pestaña \"Historial\"."),
                                                rx.list_item("Aquí verás una lista de todas las evaluaciones que has realizado."),
                                                rx.list_item("Puedes ver tus notas y fechas para hacer seguimiento de tu progreso."),
                                            ),
                                            align_items="start",
                                            width="100%",
                                        )
                                    ),
                                    value="historial",
                                ),
                                rx.accordion.item(
                                    rx.accordion.trigger("Perfil de usuario"),
                                    rx.accordion.content(
                                        rx.vstack(
                                            rx.text("Para gestionar tu perfil:"),
                                            rx.ordered_list(
                                                rx.list_item("Ve a la pestaña \"Perfil\"."),
                                                rx.list_item("Aquí puedes ver y editar tu información personal."),
                                                rx.list_item("También puedes consultar tus estadísticas de uso."),
                                            ),
                                            align_items="start",
                                            width="100%",
                                        )
                                    ),
                                    value="perfil",
                                ),
                                type_="multiple",
                                default_value=["resumen"],
                                collapsible=True,
                                width="100%",
                            ),
                            
                            width="100%",
                            spacing="4",
                            align_items="start",
                        ),
                        value="uso",
                    ),
                    
                    # Sección: Preguntas Frecuentes - Rediseñada
                    rx.tabs.content(
                        rx.center(  # Centrar el contenido
                            rx.vstack(
                                rx.heading("Preguntas Frecuentes (FAQ)", size="4", mb="2em", text_align="center"),
                                
                                # Preguntas frecuentes en formato de tarjetas expandibles
                                rx.vstack(
                                    faq_item(
                                        "¿Qué materias están disponibles en la aplicación?",
                                        "La aplicación incluye materias para educación básica y media, incluyendo Matemáticas, Ciencias (Biología, Física, Química), Historia, Lenguaje y Literatura, entre otras. El contenido se basa en los textos escolares oficiales.",
                                        "subjects"
                                    ),
                                    faq_item(
                                        "¿Los resúmenes reemplazan la lectura completa del material?",
                                        "No. Los resúmenes son herramientas de estudio complementarias que te ayudan a repasar y consolidar el conocimiento, pero siempre es recomendable leer el material completo para una comprensión profunda.",
                                        "reading"
                                    ),
                                    faq_item(
                                        "¿Puedo descargar los resúmenes y mapas para estudiar sin conexión?",
                                        "Sí, todos los resúmenes pueden descargarse en formato PDF y los mapas conceptuales como imágenes, para que puedas estudiar sin necesidad de estar conectado a internet.",
                                        "download"
                                    ),
                                    faq_item(
                                        "¿Cómo se calculan las notas de las evaluaciones?",
                                        "Las notas se calculan en base al porcentaje de respuestas correctas, utilizando una escala de 1.0 a 7.0 donde el 60% de respuestas correctas equivale generalmente a la nota 4.0 (aprobatoria).",
                                        "grades"
                                    ),
                                    faq_item(
                                        "¿Cuánto tiempo tengo para completar una evaluación?",
                                        "Las evaluaciones tienen un tiempo asignado de aproximadamente 33 minutos (2000 segundos). Si se acaba el tiempo, la evaluación se calificará automáticamente con las respuestas proporcionadas hasta ese momento.",
                                        "time"
                                    ),
                                    faq_item(
                                        "¿Puedo usar la aplicación en mi teléfono móvil?",
                                        "Sí, la aplicación está diseñada con un enfoque responsive y funciona en dispositivos móviles, aunque algunas funcionalidades como los mapas conceptuales pueden verse mejor en pantallas más grandes.",
                                        "mobile"
                                    ),
                                    width="100%",
                                    spacing="3",
                                ),
                                
                                width="100%",
                                max_width="900px",  # Ancho máximo más grande
                                spacing="4",
                                align_items="center",  # Centrar elementos
                            ),
                            width="100%",
                        ),
                        value="faq",
                    ),
                    
                    # Sección: Acerca de
                    rx.tabs.content(
                        rx.vstack(
                            rx.heading("Acerca de SMART STUDENT", size="4", mb="1em"),
                            
                            rx.text(
                                "SMART STUDENT es una aplicación educativa diseñada para ayudar a estudiantes a optimizar su proceso de aprendizaje mediante herramientas de inteligencia artificial.",
                                mb="1em",
                            ),
                            rx.text(
                                "La aplicación utiliza tecnología de procesamiento de lenguaje natural avanzada para generar resúmenes, mapas conceptuales y evaluaciones personalizadas basadas en los textos escolares.",
                                mb="1em",
                            ),
                            
                            rx.heading("Tecnologías utilizadas", size="5", mt="1em", mb="0.5em"),
                            rx.unordered_list(
                                rx.list_item("Frontend: Reflex (Python + React)"),
                                rx.list_item("Backend: Python"),
                                rx.list_item("IA: API de Google Gemini"),
                                rx.list_item("Base de datos: SQLite"),
                            ),
                            
                            rx.heading("Versión", size="5", mt="1em", mb="0.5em"),
                            rx.text("SMART STUDENT v1.0.0"),
                            rx.text("© 2023-2024 Todos los derechos reservados"),
                            
                            width="100%",
                            spacing="2",
                            align_items="start",
                        ),
                        value="about",
                    ),
                    
                    # Sección: Contacto
                    rx.tabs.content(
                        rx.vstack(
                            rx.heading("Contacto y Soporte", size="4", mb="1em"),
                            
                            rx.text(
                                "Si tienes preguntas, problemas o sugerencias, no dudes en contactarnos:",
                                mb="1em",
                            ),
                            
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("envelope", mr="0.5em"),
                                    rx.text("Email:"),
                                    rx.text("soporte@smartstudent.edu", font_weight="bold"),
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.icon("telephone", mr="0.5em"),
                                    rx.text("Teléfono:"),
                                    rx.text("+56 2 2123 4567", font_weight="bold"),
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.icon("geo-alt", mr="0.5em"),
                                    rx.text("Dirección:"),
                                    rx.text("Av. Educación 1234, Santiago, Chile", font_weight="bold"),
                                    width="100%",
                                ),
                                width="100%",
                                spacing="4",
                                align_items="start",
                                mt="1em",
                            ),
                            
                            rx.heading("Formulario de Contacto", size="5", mt="2em", mb="1em"),
                            rx.form(
                                rx.vstack(
                                    rx.vstack(
                                        rx.text("Asunto", font_weight="bold"),
                                        rx.select(
                                            [
                                                "Problema técnico",
                                                "Consulta general",
                                                "Sugerencia",
                                                "Otro",
                                            ],
                                            placeholder="Selecciona un asunto...",
                                        ),
                                        align_items="start",
                                        width="100%",
                                    ),
                                    rx.vstack(
                                        rx.text("Mensaje", font_weight="bold"),
                                        rx.text_area(
                                            placeholder="Escribe tu mensaje aquí...",
                                            min_height="150px",
                                        ),
                                        align_items="start",
                                        width="100%",
                                    ),
                                    rx.button(
                                        "Enviar Mensaje",
                                        type_="submit",
                                        color_scheme=PRIMARY_COLOR_SCHEME,
                                        width="100%",
                                    ),
                                    width="100%",
                                    spacing="4",
                                ),
                            ),
                            
                            width="100%",
                            spacing="3",
                            align_items="start",
                        ),
                        value="contacto",
                    ),
                    
                    default_value="uso",
                    width="100%",
                ),
                
                width="100%",
                spacing="4",
                padding="1em",
            ),
            variant="surface",
            width="100%",
            max_width="1000px",  # Aumentado el ancho máximo de toda la tarjeta
        ),
        
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
    )

# Componente para preguntas frecuentes mejorado
def faq_item(question: str, answer: str, item_id: str):
    """Crea un elemento de pregunta frecuente con diseño mejorado."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(question, size="3"),
                rx.spacer(),
                rx.icon(
                    rx.cond(
                        ProfileHelpState.selected_faq_item == item_id,
                        "chevron-up",
                        "chevron-down"
                    ),
                    size="18",
                    color=f"var(--{PRIMARY_COLOR_SCHEME}-500)",
                ),
                width="100%",
                cursor="pointer",
                on_click=lambda id=item_id: ProfileHelpState.set_faq_item(id),
            ),
            rx.cond(
                ProfileHelpState.selected_faq_item == item_id,
                rx.vstack(
                    rx.divider(mt="0.5em", mb="1em"),
                    rx.text(answer, size="3"),  # Aumentado el tamaño del texto de respuesta
                    width="100%",
                    align_items="start",
                    padding="1em",  # Añadido padding para mejorar la presentación
                ),
            ),
            width="100%",
            padding="1em",  # Aumentado el padding
            align_items="start",
        ),
        variant="soft", 
        color_scheme=rx.cond(
            ProfileHelpState.selected_faq_item == item_id,
            PRIMARY_COLOR_SCHEME,
            "gray"
        ),
        width="100%",
    )
