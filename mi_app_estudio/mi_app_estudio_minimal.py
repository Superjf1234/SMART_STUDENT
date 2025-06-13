"""
Aplicación SMART_STUDENT - Versión Minimal para Railway
"""

import reflex as rx
from mi_app_estudio.state import AppState, PRIMARY_COLOR_SCHEME, error_callout

# Crear una clase EvaluationState simplificada temporal
class EvaluationState(AppState):
    is_eval_active: bool = False
    eval_error_message: str = ""
    
    @rx.var
    def get_score_color_tier(self) -> str:
        return "var(--blue-9)"

# Función temporal para vista_pregunta_activa
def vista_pregunta_activa():
    return rx.text("Evaluación en desarrollo...")

# Función de evaluación simplificada
def evaluacion_tab():
    return rx.vstack(
        rx.heading("📝 Evaluaciones", size="6"),
        rx.text("Funcionalidad en desarrollo", color="gray.500"),
        error_callout(EvaluationState.eval_error_message),
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
    )

# Resto del contenido mínimo...
def login_page():
    return rx.center(
        rx.vstack(
            rx.heading("SMART STUDENT", size="8"),
            rx.text("Aplicación Educativa", color="gray.500"),
            rx.input(placeholder="Usuario", size="3"),
            rx.input(placeholder="Contraseña", type="password", size="3"),
            rx.button("Iniciar Sesión", size="3", color_scheme="blue"),
            spacing="4",
            align="center",
        ),
        height="100vh"
    )

def main_dashboard():
    return rx.vstack(
        rx.heading("Dashboard", size="6"),
        rx.text("Bienvenido a SMART STUDENT"),
        evaluacion_tab(),
        width="100%",
        spacing="4",
        align_items="center",
        padding="1em",
    )

# Configuración de la app
app = rx.App()

@app.add_page
def index() -> rx.Component:
    return rx.cond(
        AppState.is_logged_in, 
        main_dashboard(), 
        login_page()
    )
