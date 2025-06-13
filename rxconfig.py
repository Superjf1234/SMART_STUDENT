import reflex as rx
import os

# Configuración para Railway - Unified ports
port = int(os.environ.get("PORT", "8080"))

config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student",
    # Configuración para Railway
    backend_host="0.0.0.0",
    backend_port=port,
    frontend_port=port,
    # Modo producción para Railway
    env=rx.Env.PROD,
    # Deshabilitar tailwind para eliminar warning
    tailwind=None,
)