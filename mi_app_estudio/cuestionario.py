# Archivo: mi_app_estudio/cuestionario.py

import reflex as rx
from typing import Dict, List, Any, Optional
# Importaciones relativas
# Asegúrate de que AppState, config_logic, eval_logic, db_logic, error_callout,
# PRIMARY_COLOR_SCHEME, ACCENT_COLOR_SCHEME están definidos y accesibles en state.py
from .state import AppState, BACKEND_AVAILABLE, config_logic, eval_logic, db_logic, error_callout, PRIMARY_COLOR_SCHEME, ACCENT_COLOR_SCHEME
import asyncio
import traceback
import random
import datetime
import io
import os
from fpdf import FPDF

# --- Constantes ---
NUM_QUESTIONS = 15  # Número de preguntas por cuestionario
# ------------------

# NOTE: To ensure the state of this tab is reset when navigating away,
# add logic in the AppState's tab switching method (e.g., set_active_tab)
# to call `self.get_state(CuestionarioState).reset_cuestionario()` when leaving
# the 'cuestionario' tab.

class CuestionarioState(AppState):
    """Estado específico para la funcionalidad de cuestionarios."""

    # Estado para el formulario de generación de cuestionario
    cuestionario_loading: bool = False
    cuestionario_message: str = ""
    cuestionario_status: str = ""
    cuestionario_preguntas: List[Dict[str, Any]] = []
    cuestionario_pdf_url: str = ""
    
    # Variables para reutilizar cuando se cambia de pestaña
    cuestionario_curso: str = ""
    cuestionario_libro: str = ""
    cuestionario_tema: str = ""

    @rx.var
    def form_incompleto(self) -> bool:
        """Verifica si el formulario está incompleto para deshabilitar el botón."""
        return (
            not self.selected_curso
            or not self.selected_libro
            or not self.selected_tema
            or self.cuestionario_loading
        )

    # Helper method to get alternativas for a specific question index
    @rx.var
    def alternativas_texto(self) -> List[str]:
        """Lista de textos de alternativas para todas las preguntas."""
        result = []
        for pregunta in self.cuestionario_preguntas:
            texto = ""
            alternativas = pregunta.get("alternativas", [])
            for alt in alternativas:
                if isinstance(alt, dict):
                    texto += f"{alt.get('letra', '-')}) {alt.get('texto', '')}\n"
                else:
                    # Handle cases where alternative might just be a string
                    texto += f"- {alt}\n"
            result.append(texto)
        return result

    async def reset_cuestionario(self):
        """Limpia todo el estado del cuestionario generado."""
        print("DEBUG: Reseteando CuestionarioState (instancia)")
        self.cuestionario_loading = False
        self.cuestionario_message = ""
        self.cuestionario_status = ""
        self.cuestionario_preguntas = []
        self.cuestionario_pdf_url = ""
        # Limpiar también las selecciones asociadas a este estado
        self.selected_curso = ""
        self.selected_libro = ""
        self.selected_tema = ""
        yield  # Para actualizar la UI

    async def generar_cuestionario(self):
        """Manejador para generar el cuestionario."""
        if not self.selected_curso or not self.selected_libro or not self.selected_tema:
            self.cuestionario_message = "Por favor, selecciona curso, libro e ingresa un tema."
            self.cuestionario_status = "ERROR_INPUT"
            # Yield immediately to show the error message
            yield
            return

        self.cuestionario_loading = True
        self.cuestionario_preguntas = []  # Limpiar preguntas anteriores
        self.cuestionario_message = ""
        self.cuestionario_status = ""
        self.cuestionario_pdf_url = ""
        yield  # Actualizar UI para mostrar loading

        try:
            print(f"INFO (State): Llamando a generar_evaluacion_logica con C={self.selected_curso}, L={self.selected_libro}, T={self.selected_tema}")
            # Llamar a la función del backend que genera preguntas
            # Asegúrate de que eval_logic.generar_evaluacion_logica es una función síncrona si no usas await
            # Si es async, necesitas await here. As it's currently called without await, assuming sync.
            # If it's truly async, you need to handle it correctly.
            # Based on the original code, it seems to be treated as synchronous.
            resultado_backend = eval_logic.generar_evaluacion_logica(
                curso=self.selected_curso,
                libro=self.selected_libro,
                tema=self.selected_tema
            )

            self.cuestionario_status = resultado_backend.get("status", "ERROR")
            self.cuestionario_message = resultado_backend.get("message", "Error desconocido al generar cuestionario.")

            if self.cuestionario_status == "EXITO":
                # Ensure preguntas is a list before slicing
                preguntas_generadas = resultado_backend.get("preguntas", [])
                if isinstance(preguntas_generadas, list):
                     self.cuestionario_preguntas = preguntas_generadas[:NUM_QUESTIONS]
                else:
                     print(f"ERROR: Backend did not return a list of questions. Received: {type(preguntas_generadas)}")
                     self.cuestionario_status = "ERROR_FORMATO_BACKEND"
                     self.cuestionario_message = "El backend devolvió datos en un formato inesperado."
                     self.cuestionario_preguntas = [] # Ensure empty list

                if self.cuestionario_preguntas:
                    self.cuestionario_message = f"Se ha generado un cuestionario con {len(self.cuestionario_preguntas)} preguntas."
                    # Generar PDF (this is an async method, needs await)
                    await self.generar_pdf_cuestionario()
                else:
                    # Clear message if no questions found after successful status
                    if self.cuestionario_status == "EXITO":
                         self.cuestionario_message = f"No se encontraron preguntas para el tema '{self.selected_tema}'."


            else:
                # Limpiar preguntas si hubo error
                self.cuestionario_preguntas = []
                print(f"ERROR (State): Generando cuestionario - Status: {self.cuestionario_status}, Msg: {self.cuestionario_message}")

        except Exception as e:
            self.cuestionario_status = "ERROR_INESPERADO"
            self.cuestionario_message = f"Error inesperado en la interfaz al generar cuestionario: {e}"
            self.cuestionario_preguntas = []
            print(f"ERROR (State): Excepción generando cuestionario - {e}")
            traceback.print_exc()
        finally:
            self.cuestionario_loading = False
            print(f"INFO (State): Generación de cuestionario finalizada. Status: {self.cuestionario_status}")
            yield  # Actualizar UI

    async def generar_pdf_cuestionario(self):
        """Genera un PDF con el cuestionario."""
        if not self.cuestionario_preguntas:
            print("WARN: No hay preguntas para generar PDF")
            # Clear PDF URL if no questions are present
            self.cuestionario_pdf_url = ""
            return

        try:
            # Crear un PDF
            pdf = FPDF()
            pdf.add_page()

            # Configuración de la fuente
            # FPDF might not have 'Arial' by default depending on installation.
            # You might need to add fonts or use standard ones like 'helvetica'.
            # Assuming 'Arial' is available or a reasonable default will be used.
            try:
                pdf.set_font("Arial", "B", 16)
            except:
                 print("WARN: Font 'Arial' not found, using default.")
                 pdf.set_font("helvetica", "B", 16)


            # Título
            pdf.cell(0, 10, f"CUESTIONARIO - {self.selected_tema.upper()}", 0, 1, "C")
            try:
                pdf.set_font("Arial", "I", 12)
            except:
                 pdf.set_font("helvetica", "I", 12)

            pdf.cell(0, 10, f"Curso: {self.selected_curso} - Libro: {self.selected_libro}", 0, 1, "C")
            pdf.cell(0, 10, f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}", 0, 1, "C")

            pdf.ln(10)

            # Preguntas
            try:
                pdf.set_font("Arial", "", 12)
            except:
                pdf.set_font("helvetica", "", 12)

            for i, pregunta in enumerate(self.cuestionario_preguntas):
                # Número de pregunta y texto
                try:
                    pdf.set_font("Arial", "B", 12)
                except:
                     pdf.set_font("helvetica", "B", 12)

                # Use write instead of multi_cell for simpler cases, or ensure multi_cell fits width
                # Using multi_cell with width=0 uses page width minus margins, which is usually fine.
                pdf.multi_cell(0, 8, f"{i+1}. {pregunta.get('pregunta', '')}")
                pdf.ln(2) # Reduced space after question text

                # Display alternatives if available
                alternativas = pregunta.get("alternativas", [])
                if alternativas:
                     try:
                        pdf.set_font("Arial", "", 10) # Smaller font for alternatives
                     except:
                        pdf.set_font("helvetica", "", 10)
                     for alt in alternativas:
                         alt_text = ""
                         if isinstance(alt, dict):
                              alt_text = f"{alt.get('letra', '-')}) {alt.get('texto', '')}"
                         else:
                              alt_text = f"- {alt}"
                         pdf.multi_cell(0, 6, alt_text) # Reduced line height for alternatives
                     pdf.ln(5) # Space after alternatives list


            # Página de respuestas
            pdf.add_page()
            try:
                pdf.set_font("Arial", "B", 16)
            except:
                 pdf.set_font("helvetica", "B", 16)

            pdf.cell(0, 10, "RESPUESTAS", 0, 1, "C")
            pdf.ln(10)

            # Listar respuestas
            try:
                 pdf.set_font("Arial", "", 12)
            except:
                 pdf.set_font("helvetica", "", 12)

            for i, pregunta in enumerate(self.cuestionario_preguntas):
                respuesta = ""
                # Check for both 'correctas' (list for multiple choice) and 'correcta' (single answer)
                if pregunta.get("tipo") == "seleccion_multiple":
                    respuestas_list = pregunta.get("correctas", [])
                    respuesta = ", ".join(str(r) for r in respuestas_list) # Ensure elements are strings
                else:
                    respuesta = str(pregunta.get("correcta", "")) # Ensure it's a string

                explicacion = str(pregunta.get('explicacion', '')) # Ensure it's a string

                pdf.multi_cell(0, 8, f"{i+1}. Respuesta: {respuesta}\nExplicación: {explicacion}")
                pdf.ln(5)

            # Ensure the assets/pdfs directory exists
            output_dir = os.path.join("assets", "pdfs")
            os.makedirs(output_dir, exist_ok=True)

            # Guardar en un archivo temporal
            filename = f"cuestionario_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            filepath = os.path.join(output_dir, filename)

            pdf.output(filepath)

            # Guardar la URL del archivo para descarga
            self.cuestionario_pdf_url = f"/{filepath.replace(os.sep, '/')}" # Use forward slashes for URL
            print(f"INFO: PDF generado en {filepath}")

        except Exception as e:
            print(f"ERROR generando PDF: {e}")
            traceback.print_exc()
            # Clear PDF URL on error
            self.cuestionario_pdf_url = ""


def cuestionario_tab_content() -> rx.Component:
    """Contenido de la pestaña de Cuestionario, con estructura y estilo igual a mapa_tab."""
    return rx.vstack(
        # Encabezado con robot
        rx.center(
            rx.hstack(
                rx.heading("🧐 ¡Desafía tu Conocimiento con Cuestionarios!", size="6"),
                rx.image(src="/robot_cuestionario.png", width="80px", height="80px", ml="3em"),
                width="auto",
                justify="center",
                align_items="center",
                mb="2em",
            ),
        ),
        
        # Texto introductorio (estilo igual a mapa_tab)
        rx.text(
            "Genera pruebas personalizadas para evaluar tu comprensión y reforzar el aprendizaje.", # Texto actualizado
            color="gray.500",
            mb="2em",
            text_align="center",
            max_width="600px",
        ),

        # Formulario dentro de una Card (igual a mapa_tab)
        rx.card(
            rx.vstack(
                # Formulario para seleccionar curso, libro y tema (sin iconos en labels)
                rx.select( # Curso
                    CuestionarioState.cursos_list,
                    placeholder="Selecciona un Curso...",
                    value=CuestionarioState.selected_curso,
                    on_change=CuestionarioState.handle_curso_change,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                    name="cuestionario_curso_select",
                ),
                rx.select( # Libro
                    CuestionarioState.libros_para_curso,
                    placeholder="Selecciona un Libro...",
                    value=CuestionarioState.selected_libro,
                    on_change=CuestionarioState.handle_libro_change,
                    size="3",
                    color_scheme=PRIMARY_COLOR_SCHEME,
                    width="100%",
                    name="cuestionario_libro_select",
                    is_disabled=rx.cond(CuestionarioState.selected_curso == "", True, False),
                ),
                rx.text_area( # Cambiado de input a text_area para coincidir con la pestaña de mapas
                    placeholder="Escribe el tema para el cuestionario",
                    value=CuestionarioState.selected_tema,
                    on_change=CuestionarioState.set_selected_tema,
                    size="3",
                    min_height="100px", # Añadido para coincidir con la pestaña de mapas
                    width="100%",
                    name="cuestionario_tema_input",
                    is_disabled=rx.cond(CuestionarioState.selected_libro == "", True, False),
                ),

                # Botón para generar el cuestionario (color y estilo igual a mapa_tab)
                rx.button(
                    rx.cond(
                        CuestionarioState.cuestionario_loading,
                        rx.hstack(rx.spinner(size="2"), rx.text("Generando cuestionario...")),
                        rx.hstack(rx.icon("file-question"), rx.text("Generar Cuestionario")) # Icono relevante
                    ),
                    on_click=CuestionarioState.generar_cuestionario,
                    size="3",
                    width="100%",
                    variant="solid",
                    color_scheme="cyan", # Color correspondiente a Cuestionarios
                    is_disabled=CuestionarioState.form_incompleto,
                    margin_top="1em",
                ),
                width="100%",
                spacing="4",
                padding="2em",
            ),
            variant="surface",
            width="100%",
            max_width="500px", # Ancho igual a mapa_tab
        ),

        # Success/Error message area (positioning improved)
        rx.box(
            # Conditional rendering for success or error message
            rx.cond(
                (CuestionarioState.cuestionario_message != "") & (CuestionarioState.selected_tema != ""),
                rx.cond(
                    CuestionarioState.cuestionario_status == "EXITO",
                    # Success message
                    rx.box(
                        rx.hstack(
                            rx.icon("check-circle", color="green"),
                            rx.text(CuestionarioState.cuestionario_message),
                            spacing="2",
                        ),
                        padding="0.8em",
                        border_radius="md",
                        bg="rgba(0, 255, 0, 0.1)",  # Light green background
                        border="1px solid green",
                        width="100%",
                    ),
                    # Error message
                    rx.box(
                        error_callout(CuestionarioState.cuestionario_message),
                        width="100%",
                    )
                ),
                rx.fragment() # Nothing shown if no message or tema is empty
            ),
            width="100%",
            max_width="500px",  # Mismo ancho que el formulario
            margin_y="1.5em",
            align_self="center",  # Para asegurar que está centrado
        ),


        # Mostrar el cuestionario generado en una Card (igual a mapa_tab)
        rx.cond(
            (CuestionarioState.cuestionario_preguntas.length() > 0) & (CuestionarioState.selected_tema != ""),
            rx.card(
                rx.vstack(
                    # Título del cuestionario - centrado y mayúsculas
                    rx.heading(
                        f"CUESTIONARIO - {CuestionarioState.selected_tema.upper()}",
                        size="5",
                        mb="1em",
                        text_align="center",
                    ),

                    # Lista de preguntas (mantenemos estructura interna)
                    rx.foreach(
                        CuestionarioState.cuestionario_preguntas,
                        lambda pregunta, index: rx.box(
                            rx.heading(
                                f"Pregunta {index + 1}",
                                size="4",
                                margin_bottom="0.5em",
                            ),
                            rx.text(
                                pregunta.get("pregunta", ""),
                                margin_bottom="1em",
                                font_weight="medium",
                            ),
                            # Display answers directly below each question
                            # Consider hiding answers by default and adding a "Show Answers" button
                            # for a more typical questionnaire format if desired.
                            # For now, displaying answers as in the original code.
                            rx.box(
                                rx.text(
                                    "Respuesta:",
                                    font_weight="bold",
                                    margin_top="0.5em", # Adjusted margin
                                ),
                                rx.text(pregunta.get("explicacion", "")),
                                padding="0.5em",
                                border_radius="md",
                                bg="var(--gray-2)", # Light background for answer section
                                border="1px solid var(--gray-4)",
                                margin_top="0.5em",
                            ),
                            border="1px solid var(--gray-5)", # Adjusted border color
                            border_radius="md",
                            padding="1.5em", # Increased padding
                            margin_bottom="1.5em",
                            width="100%",
                            background_color="var(--gray-1)", # Light background for question box
                        ),
                    ),

                    # Botones de acción - Descargar PDF primero (a la izquierda)
                    rx.hstack(
                        rx.cond(
                            CuestionarioState.cuestionario_pdf_url != "",
                            rx.link(
                                rx.button(
                                    rx.hstack(
                                        rx.icon("download", mr="0.2em"),
                                        rx.text("Descargar PDF")
                                    ),
                                    size="2",
                                    variant="soft",
                                    color_scheme="green",
                                ),
                                href=CuestionarioState.cuestionario_pdf_url,
                                is_external=True,
                            ),
                            rx.fragment() # Hide download button if no PDF URL
                        ),
                        rx.button(
                            rx.icon("git-branch", mr="0.2em"),
                            "Crear Mapa",
                            # Assuming AppState.set_active_tab is defined in state.py
                            on_click=lambda: AppState.set_active_tab("mapa"),
                            variant="soft",
                            size="2",
                            color_scheme=ACCENT_COLOR_SCHEME,
                        ),
                        rx.button(
                            rx.icon("clipboard-check", mr="0.2em"),
                            "Crear Evaluación",
                             # Assuming AppState.set_active_tab is defined in state.py
                            on_click=lambda: AppState.set_active_tab("evaluacion"),
                            variant="soft",
                            size="2",
                            color_scheme="purple",
                        ),
                         rx.button(
                            rx.hstack(
                                rx.icon("file-text", mr="0.2em"),
                                "Crear Resumen"
                            ),
                            # Assuming AppState.set_active_tab is defined in state.py
                            on_click=lambda: AppState.set_active_tab("resumen"),
                            variant="soft",
                            size="2",
                            color_scheme="blue",
                        ),
                        justify="center",
                        spacing="4",
                        mt="1.5em",
                        width="100%",
                        flex_wrap="wrap", # Allow buttons to wrap on smaller screens
                    ),
                    width="100%",
                    padding="2em",
                    spacing="4",
                    align_items="center", # Centrar todo el contenido
                ),
                variant="surface",
                width="100%",
                max_width="900px", # Ancho igual a mapa_tab
                margin_top="2em",
            ),
             rx.fragment() # Nothing shown if no questions
        ),


        # Layout general de la pestaña (igual a mapa_tab)
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
        margin_top="5em", # Margen igual a mapa_tab
        padding_bottom="5em", # Add padding at the bottom
    )