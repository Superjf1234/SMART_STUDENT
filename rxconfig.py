import reflex as rx
import os

# Configuración para Railway - Todo en el mismo puerto
port = int(os.environ.get("PORT", "8080"))

config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student",
    # Configuración unificada para Railway
    backend_host="0.0.0.0",
    backend_port=port,
    frontend_port=port,  # Usar el mismo puerto para frontend
    # Modo producción para Railway
    env=rx.Env.PROD,
    # Deshabilitar tailwind para eliminar warning
    tailwind=None,
    # API URL para Railway - dejar que Reflex maneje automáticamente
    # api_url se configurará automáticamente
)