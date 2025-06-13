"""
SMART STUDENT - VERSIÓN SIMPLIFICADA PARA RAILWAY
Sin imports complejos entre módulos
"""

import reflex as rx
import os
import sys
from typing import Dict, List, Optional, Any

# Configuración de la API
os.environ.setdefault("GEMINI_API_KEY", "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA")

# ========== ESTADO SIMPLIFICADO ==========
class AppState(rx.State):
    """Estado principal simplificado sin dependencias complejas"""
    
    # UI State
    active_tab: str = "inicio"
    is_loading: bool = False
    error_message: str = ""
    
    # Content
    message: str = "¡Bienvenido a Smart Student!"
    
    def set_active_tab(self, tab: str):
        """Cambiar tab activo"""
        self.active_tab = tab
        self.error_message = ""
    
    def show_message(self, msg: str):
        """Mostrar mensaje"""
        self.message = msg

# ========== COMPONENTES SIMPLIFICADOS ==========
def navbar() -> rx.Component:
    """Barra de navegación simplificada"""
    return rx.hstack(
        rx.heading("Smart Student", size="6"),
        rx.spacer(),
        rx.button("Inicio", on_click=lambda: AppState.set_active_tab("inicio")),
        rx.button("Estudio", on_click=lambda: AppState.set_active_tab("estudio")),
        rx.button("Ayuda", on_click=lambda: AppState.set_active_tab("ayuda")),
        width="100%",
        padding="1rem",
        bg="blue.500",
        color="white"
    )

def inicio_tab() -> rx.Component:
    """Tab de inicio simplificado"""
    return rx.container(
        rx.vstack(
            rx.heading("¡Bienvenido a Smart Student!", size="8"),
            rx.text("Tu asistente de estudio inteligente", size="4"),
            rx.text(AppState.message),
            rx.button(
                "¡Empezar a estudiar!",
                on_click=lambda: AppState.set_active_tab("estudio"),
                size="3",
                variant="solid"
            ),
            spacing="4",
            align="center",
            padding="2rem"
        ),
        height="70vh",
        display="flex",
        align_items="center",
        justify_content="center"
    )

def estudio_tab() -> rx.Component:
    """Tab de estudio simplificado"""
    return rx.container(
        rx.vstack(
            rx.heading("Área de Estudio", size="7"),
            rx.text("Aquí puedes estudiar y generar contenido educativo"),
            rx.text_area(
                placeholder="Escribe tu tema de estudio aquí...",
                height="200px",
                width="100%"
            ),
            rx.button(
                "Generar contenido",
                on_click=lambda: AppState.show_message("¡Función en desarrollo!"),
                size="2"
            ),
            spacing="4",
            padding="2rem"
        )
    )

def ayuda_tab() -> rx.Component:
    """Tab de ayuda simplificado"""
    return rx.container(
        rx.vstack(
            rx.heading("Ayuda", size="7"),
            rx.text("Smart Student es tu asistente de estudio personal"),
            rx.callout(
                "Características principales:",
                icon="info",
                size="2"
            ),
            rx.unordered_list(
                rx.list_item("Generación de contenido educativo"),
                rx.list_item("Cuestionarios interactivos"),
                rx.list_item("Evaluaciones personalizadas"),
                rx.list_item("Mapas conceptuales"),
            ),
            spacing="4",
            padding="2rem"
        )
    )

def main_content() -> rx.Component:
    """Contenido principal basado en el tab activo"""
    return rx.cond(
        AppState.active_tab == "inicio",
        inicio_tab(),
        rx.cond(
            AppState.active_tab == "estudio",
            estudio_tab(),
            ayuda_tab()
        )
    )

def index() -> rx.Component:
    """Página principal"""
    return rx.container(
        rx.vstack(
            navbar(),
            rx.cond(
                AppState.error_message != "",
                rx.callout(
                    AppState.error_message,
                    icon="triangle_alert",
                    color_scheme="red",
                    margin="1rem"
                )
            ),
            main_content(),
            spacing="0",
            width="100%"
        ),
        width="100%",
        max_width="100%",
        padding="0"
    )

# ========== CONFIGURACIÓN DE LA APP ==========
app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        scaling="100%"
    )
)
app.add_page(index, route="/")

# Para deployment
if __name__ == "__main__":
    app.run()
