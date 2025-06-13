import reflex as rx
import os

# Configuración para Railway
port = int(os.environ.get("PORT", "8080"))

config = rx.Config(
    app_name="main",  # Archivo main.py en el directorio raíz
    api_url=f"http://0.0.0.0:{port}",
    backend_host="0.0.0.0", 
    backend_port=port,
    frontend_port=3000,
    deploy_url=None,
    tailwind=None,  # Deshabilitar para evitar warnings
    env=rx.Env.PROD,  # Modo producción para Railway
)
