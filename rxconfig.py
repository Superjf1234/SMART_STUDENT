import reflex as rx
import os

# Configuración para Railway - Backend sirve todo
port = int(os.environ.get("PORT", "8080"))

config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student",
    # Configuración para Railway - un solo puerto
    backend_host="0.0.0.0",
    backend_port=port,
    # NO especificar frontend_port - que Reflex use el mismo
    # Modo desarrollo para Railway
    env=rx.Env.DEV,
    # Deshabilitar tailwind para eliminar warning
    tailwind=None,
)