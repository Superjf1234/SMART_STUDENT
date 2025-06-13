import reflex as rx
import os

# Configuración para Railway - Backend sirve todo
port = int(os.environ.get("PORT", "8080"))

# Detectar desde dónde se ejecuta para ajustar app_name
current_dir = os.getcwd()
if current_dir.endswith('/mi_app_estudio'):
    # Si ejecutamos desde /app/mi_app_estudio, el módulo principal es directamente mi_app_estudio
    app_module = "mi_app_estudio"
else:
    # Si ejecutamos desde /app, el módulo es mi_app_estudio.mi_app_estudio
    app_module = "mi_app_estudio.mi_app_estudio"

print(f"DEBUG: Current dir: {current_dir}")
print(f"DEBUG: App module: {app_module}")

config = rx.Config(
    app_name=app_module,
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
