import reflex as rx
import os

# Configuración optimizada para Railway
port = int(os.environ.get("PORT", "8080"))

config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student | Aprende, Crea y Destaca",
    tailwind=None,  # Eliminar warning de tailwind
    # Configuración para Railway
    backend_host="0.0.0.0",
    backend_port=port,
    frontend_port=port,
    # Usar desarrollo para evitar problemas de build
    env=rx.Env.DEV,
    # URL del API
    api_url=f"http://0.0.0.0:{port}",
    # Configuraciones adicionales para Railway
    timeout=120,
    deploy_url=f"https://web-production-b9571.up.railway.app"
)