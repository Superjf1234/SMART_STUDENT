import reflex as rx
import os

# Configuración optimizada para Railway
port = int(os.environ.get("PORT", "8080"))

config = rx.Config(
    app_name="mi_app_estudio",  # Nombre del módulo sin dots
    title="Smart Student",
    # Configuración unificada para Railway
    backend_host="0.0.0.0",
    backend_port=port,
    # No especificar frontend_port - usar el mismo puerto
    # Modo desarrollo para Railway
    env=rx.Env.DEV,
    # Deshabilitar tailwind para eliminar warnings
    tailwind=None,
)