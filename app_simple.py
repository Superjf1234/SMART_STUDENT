import reflex as rx

class State(rx.State):
    # Autenticación básica
    username: str = ""
    password: str = ""
    is_logged_in: bool = False
    error_message: str = ""
    
    def login(self):
        """Maneja el login básico."""
        if self.username in ["felipe", "test", "admin"] and len(self.password) > 0:
            self.is_logged_in = True
            self.error_message = ""
        else:
            self.error_message = "Usuario o contraseña inválidos"
    
    def logout(self):
        """Cierra sesión."""
        self.is_logged_in = False
        self.username = ""
        self.password = ""
        self.error_message = ""

def login_page():
    """Página de login simplificada."""
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("SMART STUDENT", size="6", text_align="center"),
                rx.text("Aprende, Crea y Destaca", color="gray", text_align="center"),
                
                rx.input(
                    placeholder="Usuario",
                    value=State.username,
                    on_change=State.set_username,
                    size="3",
                    width="100%"
                ),
                
                rx.input(
                    placeholder="Contraseña",
                    type="password",
                    value=State.password,
                    on_change=State.set_password,
                    size="3",
                    width="100%"
                ),
                
                rx.button(
                    "Iniciar Sesión",
                    on_click=State.login,
                    size="3",
                    width="100%",
                    color_scheme="blue"
                ),
                
                rx.cond(
                    State.error_message != "",
                    rx.text(State.error_message, color="red")
                ),
                
                spacing="4",
                width="100%",
                max_width="400px",
                padding="2em"
            )
        ),
        height="100vh"
    )

def dashboard():
    """Dashboard principal simplificado."""
    return rx.center(
        rx.vstack(
            rx.heading(f"¡Bienvenido, {State.username}!", size="6"),
            rx.text("La aplicación está funcionando correctamente."),
            rx.button(
                "Cerrar Sesión",
                on_click=State.logout,
                color_scheme="red"
            ),
            spacing="4",
            align="center"
        ),
        height="100vh"
    )

def index():
    """Página principal con condicional de login."""
    return rx.cond(
        State.is_logged_in,
        dashboard(),
        login_page()
    )

# Crear la aplicación
app = rx.App()
app.add_page(index)
