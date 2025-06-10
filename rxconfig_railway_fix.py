import reflex as rx
import os

# CONFIGURACIÓN ESPECÍFICA PARA RAILWAY - EVITA OUT OF MEMORY
# Esta configuración FUERZA el modo desarrollo para evitar el build de producción

config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student | Aprende, Crea y Destaca",
    
    # FORZAR MODO DESARROLLO - CRÍTICO PARA RAILWAY
    env=rx.Env.DEV,  # NUNCA CAMBIAR A PROD
    
    # Configuración de red
    backend_host="0.0.0.0",
    backend_port=int(os.environ.get("PORT", "8080")),
    frontend_port=int(os.environ.get("PORT", "8080")),
    
    # DESACTIVAR TODAS LAS OPTIMIZACIONES QUE CAUSAN OUT OF MEMORY
    tailwind=None,  # Sin Tailwind
    
    # EVITAR BUILD DE PRODUCCIÓN
    frontend_packages=[],  # Sin paquetes adicionales
    
    # API URL simple
    api_url=f"http://0.0.0.0:{os.environ.get('PORT', '8080')}",
    
    # CONFIGURACIONES CRÍTICAS PARA RAILWAY
    # Estos valores están optimizados para evitar out of memory
    compile_path="/.web",
    db_url=f"sqlite:///reflex.db",
    
    # MODO DESARROLLO FORZADO
    debug=True,
    
    # Configuración de tiempo de espera reducida
    timeout=30,
    
    # Sin optimizaciones adicionales
    bun_path=None,
)
