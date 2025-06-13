#!/usr/bin/env python3
"""
RAILWAY EMERGENCY FIX - Aplicación principal en directorio raíz
"""
import reflex as rx
import os

# Configurar variables de entorno
os.environ.setdefault("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"))

class AppState(rx.State):
    """Estado principal de la aplicación"""
    message: str = "🎓 Bienvenido a SMART STUDENT"
    status: str = "✅ Aplicación funcionando correctamente en Railway"
    
    def update_status(self):
        """Actualizar estado de la aplicación"""
        self.status = "🚀 ¡Sistema operativo y funcionando!"
        self.message = "📚 SMART STUDENT - Plataforma de Estudio Inteligente"

def index() -> rx.Component:
    """Página principal de la aplicación"""
    return rx.container(
        rx.vstack(
            # Header
            rx.heading(
                "🎓 SMART STUDENT",
                size="2xl",
                color_scheme="blue",
                text_align="center",
                margin_bottom="4"
            ),
            
            # Estado actual
            rx.card(
                rx.vstack(
                    rx.text(
                        AppState.message,
                        font_size="xl",
                        font_weight="bold",
                        color="blue.600"
                    ),
                    rx.text(
                        AppState.status,
                        font_size="lg",
                        color="green.500"
                    ),
                    rx.button(
                        "🔄 Actualizar Estado",
                        on_click=AppState.update_status,
                        color_scheme="green",
                        size="lg",
                        margin_top="4"
                    ),
                    spacing="3",
                    align="center"
                ),
                padding="6",
                margin="4"
            ),
            
            # Información del sistema
            rx.card(
                rx.vstack(
                    rx.heading("📊 Estado del Sistema", size="lg", color="gray.700"),
                    rx.hstack(
                        rx.badge("✅ Backend: Activo", color_scheme="green"),
                        rx.badge("✅ Frontend: Activo", color_scheme="green"),
                        rx.badge("✅ Railway: Desplegado", color_scheme="blue"),
                        spacing="2"
                    ),
                    rx.text(
                        f"🔌 Puerto: {os.environ.get('PORT', '8080')}",
                        font_size="sm",
                        color="gray.600"
                    ),
                    rx.text(
                        "🌐 Servidor: Railway Platform",
                        font_size="sm",
                        color="gray.600"
                    ),
                    spacing="3",
                    align="center"
                ),
                padding="4",
                margin="4"
            ),
            
            # Funcionalidades disponibles
            rx.card(
                rx.vstack(
                    rx.heading("🚀 Funcionalidades", size="lg", color="gray.700"),
                    rx.grid(
                        rx.button(
                            "📝 Evaluaciones",
                            color_scheme="blue",
                            variant="outline",
                            size="lg"
                        ),
                        rx.button(
                            "📚 Cuestionarios",
                            color_scheme="purple",
                            variant="outline",
                            size="lg"
                        ),
                        rx.button(
                            "🤖 IA Asistente",
                            color_scheme="green",
                            variant="outline",
                            size="lg"
                        ),
                        rx.button(
                            "📊 Progreso",
                            color_scheme="orange",
                            variant="outline",
                            size="lg"
                        ),
                        columns="2",
                        spacing="3"
                    ),
                    spacing="4",
                    align="center"
                ),
                padding="4",
                margin="4"
            ),
            
            # Footer
            rx.divider(),
            rx.text(
                "🎉 ¡Aplicación SMART STUDENT desplegada exitosamente en Railway!",
                color="green.600",
                font_weight="bold",
                text_align="center",
                margin_top="4"
            ),
            
            spacing="4",
            align="center",
            min_height="100vh",
            justify="center"
        ),
        max_width="900px",
        margin="0 auto",
        padding="4"
    )

# Crear la aplicación Reflex
app = rx.App(
    state=AppState,
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="blue",
    ),
    style={
        "font_family": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "min_height": "100vh",
    }
)

# Agregar la página principal
app.add_page(index, route="/", title="SMART STUDENT - Plataforma de Estudio")

# Compatibilidad con Railway
if __name__ == "__main__":
    app.compile()
