#!/usr/bin/env python3
"""
RAILWAY EMERGENCY FIX: Aplicación principal en directorio raíz
Esta es la solución definitiva para Railway
"""
import reflex as rx
import os

# Configuración de variables de entorno
os.environ.setdefault("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"))

class State(rx.State):
    """Estado principal de la aplicación"""
    message: str = "¡Bienvenido a SMART STUDENT!"
    counter: int = 0
    
    def increment_counter(self):
        """Incrementa el contador"""
        self.counter += 1
        self.message = f"¡Aplicación funcionando! Contador: {self.counter}"
    
    def reset_counter(self):
        """Resetea el contador"""
        self.counter = 0
        self.message = "¡Bienvenido a SMART STUDENT!"

def index() -> rx.Component:
    """Página principal"""
    return rx.container(
        rx.vstack(
            # Header
            rx.heading(
                "🎓 SMART STUDENT", 
                size="3xl",
                color_scheme="blue",
                text_align="center",
                margin_bottom="8"
            ),
            
            # Status Card
            rx.card(
                rx.vstack(
                    rx.badge(
                        "✅ APLICACIÓN FUNCIONANDO EN RAILWAY",
                        color_scheme="green",
                        size="lg"
                    ),
                    rx.text(
                        State.message,
                        font_size="xl",
                        text_align="center",
                        font_weight="bold"
                    ),
                    rx.text(
                        f"Contador: {State.counter}",
                        font_size="lg",
                        color="gray.600"
                    ),
                    spacing="4"
                ),
                padding="6",
                width="100%"
            ),
            
            # Buttons
            rx.hstack(
                rx.button(
                    "➕ Incrementar",
                    on_click=State.increment_counter,
                    color_scheme="blue",
                    size="lg"
                ),
                rx.button(
                    "🔄 Resetear",
                    on_click=State.reset_counter,
                    color_scheme="gray",
                    size="lg"
                ),
                spacing="4",
                justify="center"
            ),
            
            # Info Section
            rx.divider(margin_y="6"),
            rx.vstack(
                rx.heading("📊 Información del Sistema", size="lg"),
                rx.text(f"🐍 Python: Funcionando"),
                rx.text(f"🚀 Reflex: Funcionando"),
                rx.text(f"☁️ Railway: Funcionando"),
                rx.text(f"🔑 API Key: {'Configurada' if os.getenv('GEMINI_API_KEY') else 'No configurada'}"),
                spacing="2",
                align="start"
            ),
            
            # Footer
            rx.divider(margin_y="6"),
            rx.text(
                "🎉 ¡Deployment exitoso en Railway!",
                color="green.500",
                font_weight="bold",
                text_align="center"
            ),
            
            spacing="6",
            align="center",
            min_height="100vh",
            justify="center",
            padding="8"
        ),
        max_width="600px",
        margin="0 auto"
    )

def about() -> rx.Component:
    """Página acerca de"""
    return rx.container(
        rx.vstack(
            rx.heading("📖 Acerca de SMART STUDENT", size="2xl"),
            rx.text(
                "Esta es una aplicación educativa desarrollada con Reflex y desplegada en Railway.",
                font_size="lg"
            ),
            rx.link(
                rx.button("🏠 Volver al inicio", color_scheme="blue"),
                href="/"
            ),
            spacing="4",
            align="center",
            min_height="100vh",
            justify="center"
        ),
        max_width="600px",
        margin="0 auto"
    )

# Crear la aplicación
app = rx.App(
    state=State,
    theme=rx.theme(
        accent_color="blue",
        gray_color="slate",
        radius="medium",
    )
)

# Agregar páginas
app.add_page(index, route="/")
app.add_page(about, route="/about")

# Compilar la aplicación
if __name__ == "__main__":
    app.compile()
