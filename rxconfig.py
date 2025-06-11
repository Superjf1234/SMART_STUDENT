import reflex as rx
import os

# RAILWAY FIX: Puerto único para frontend y backend
RAILWAY_PORT = int(os.environ.get("PORT", "8080"))

# Configuración FORZADA en modo desarrollo para Railway
# Evita completamente el build de producción que causa out of memory
config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student | Aprende, Crea y Destaca",
    tailwind=None,  # Desactivar tailwind completamente
    
    # Configuración de red - RAILWAY FIX: Mismo puerto para ambos servicios
    backend_host="0.0.0.0",
    backend_port=RAILWAY_PORT,
    frontend_port=RAILWAY_PORT,  # ← MISMO PUERTO para Railway healthcheck
    
    # FORZAR MODO DESARROLLO - Evita build de producción
    env=rx.Env.DEV,  # SIEMPRE desarrollo, incluso en Railway
    
    # Optimizaciones críticas para Railway
    api_url=f"http://0.0.0.0:{RAILWAY_PORT}",
    
    # Configuraciones para prevenir errores
    telemetry_enabled=False,
    db_url="sqlite:///student_stats.db",
    loglevel="error",
    
    # Configuraciones adicionales para Railway
    timeout=300,
    cors_allowed_origins=["*"],
)
