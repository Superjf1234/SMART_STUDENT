import reflex as rx
import os

# Configuración FORZADA en modo desarrollo para Railway
# Evita completamente el build de producción que causa out of memory
config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student | Aprende, Crea y Destaca",
    tailwind=None,  # Desactivar tailwind completamente
    
    # Configuración de red
    backend_host="0.0.0.0",
    backend_port=int(os.environ.get("BACKEND_PORT", os.environ.get("PORT", "8080"))),
    frontend_port=int(os.environ.get("FRONTEND_PORT", "3000")),
    
    # FORZAR MODO DESARROLLO - Evita build de producción
    env=rx.Env.DEV,  # SIEMPRE desarrollo, incluso en Railway
    
    # Optimizaciones críticas para Railway
    api_url=f"http://0.0.0.0:{os.environ.get('BACKEND_PORT', os.environ.get('PORT', '8080'))}",
    
    # Configuraciones para prevenir errores
    telemetry_enabled=False,
    db_url="sqlite:///student_stats.db",
    loglevel="error",
    
    # Configuraciones adicionales para Railway
    timeout=300,
    cors_allowed_origins=["*"],
)
