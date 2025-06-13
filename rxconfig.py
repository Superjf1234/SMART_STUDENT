import reflex as rx
import os

config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student | Aprende, Crea y Destaca",
    tailwind=None,  # Desactivar inferencia de tailwind como sugiere la advertencia
    # Configuración específica para Railway - FORZAR DESARROLLO
    backend_host="0.0.0.0",
    backend_port=int(os.environ.get("PORT", "8080")),
    frontend_port=int(os.environ.get("PORT", "8080")),
    # FORZAR modo desarrollo para evitar build pesado
    env=rx.Env.DEV,
    # Configuraciones adicionales para prevenir errores
    api_url=f"http://0.0.0.0:{os.environ.get('PORT', '8080')}",
)