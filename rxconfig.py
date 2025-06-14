import reflex as rx
import os

config = rx.Config(
    app_name="app_main",
    title="Smart Student | Aprende, Crea y Destaca",
    
    # Eliminar warnings
    tailwind=None,
    
    # Configuración para Railway - Desarrollo forzado
    env=rx.Env.DEV,
    
    # Configuración de red
    backend_host="0.0.0.0",
    backend_port=int(os.environ.get("PORT", "8080")),
    frontend_port=int(os.environ.get("PORT", "8080")),
    
    # API URL para Railway
    api_url=f"http://0.0.0.0:{os.environ.get('PORT', '8080')}",
    
    # Configuraciones adicionales de memoria
    timeout=120,
    
    # Plugins (vacío para evitar overhead)
    plugins=[],
)