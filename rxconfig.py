import reflex as rx
import os

# Configuración optimizada para Railway con manejo de errores Rich
config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student | Aprende, Crea y Destaca",
    tailwind=None,  # Desactivar tailwind para reducir memoria
    
    # Configuración de red
    backend_host="0.0.0.0",
    backend_port=int(os.environ.get("PORT", "8080")),
    frontend_port=int(os.environ.get("PORT", "8080")),
    
    # Configuración de entorno
    env=rx.Env.PROD if os.environ.get("RAILWAY_ENVIRONMENT") == "production" else rx.Env.DEV,
    
    # Optimizaciones para Railway
    api_url=f"http://0.0.0.0:{os.environ.get('PORT', '8080')}",
    
    # Configuraciones adicionales para prevenir errores
    telemetry_enabled=False,
    db_url="sqlite:///student_stats.db",
    
    # Configuración específica para evitar errores de Rich/Markup
    loglevel="ERROR",  # Reducir verbosidad para evitar problemas con Rich
)