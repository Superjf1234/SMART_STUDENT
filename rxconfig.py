import reflex as rx
import os

# Configuración minimalista para Railway
config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student",
    # Configuración básica para Railway
    backend_host="0.0.0.0",
    backend_port=int(os.environ.get("PORT", "8080")),
    # Modo dev para evitar compilación pesada
    env=rx.Env.DEV,
)