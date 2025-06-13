import reflex as rx
import os

# Configuración optimizada para Railway
port = int(os.environ.get("PORT", "8080"))

config = rx.Config(
    app_name="app",  # Nombre simple que coincide con app.py
    title="Smart Student",
    # Configuración unificada para Railway
    backend_host="0.0.0.0",
    backend_port=port,
    # No especificar frontend_port - usar el mismo puerto
    # Modo desarrollo para Railway
    env=rx.Env.PROD,
    # Deshabilitar tailwind para eliminar warnings
    tailwind=None,
)