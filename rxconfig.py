import reflex as rx
import os

# Configuración para Railway - Backend sirve todo
port = int(os.environ.get("PORT", "8080"))

# CRÍTICO: Cuando ejecutamos desde /app/mi_app_estudio, 
# el app_name debe ser solo "mi_app_estudio" (el archivo .py)
config = rx.Config(
    app_name="mi_app_estudio",  # Archivo mi_app_estudio.py en el directorio actual
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