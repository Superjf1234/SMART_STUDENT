#!/usr/bin/env python3
"""
Script de inicio ultra-simple para Railway - AUTO-CONTENIDO SIN DEPENDENCIAS
"""
import os
import sys
import subprocess

print("===== RAILWAY EMERGENCY START SCRIPT =====")

# Forzar el directorio de trabajo a /app (raíz del proyecto)
os.chdir("/app")
print(f"Forzado directorio a: {os.getcwd()}")

# Imprimir el contenido del directorio
print(f"Contenido de {os.getcwd()}: {os.listdir('.')}")

# Verificar si existe rxconfig.py
if not os.path.exists("rxconfig.py"):
    print("❌ ERROR: rxconfig.py no encontrado en /app")
    
    # Si no existe, intentar crear uno básico
    with open("rxconfig.py", "w") as f:
        f.write("""
import reflex as rx
import os

config = rx.Config(
    app_name="app_main",
    title="Smart Student | Aprende, Crea y Destaca",
    
    # Eliminar warnings de Tailwind
    tailwind=None,
    
    # Forzar desarrollo
    env=rx.Env.DEV,
    
    # Configuración de red
    backend_host="0.0.0.0",
    backend_port=int(os.environ.get("PORT", "8080")),
    frontend_port=int(os.environ.get("PORT", "8080")),
    
    # API URL para Railway
    api_url=f"http://0.0.0.0:{os.environ.get('PORT', '8080')}",
    
    # Configuraciones adicionales
    timeout=120,
    
    # Plugins vacíos
    plugins=[],
)
""")
    print("✅ rxconfig.py creado en /app")
else:
    print("✅ rxconfig.py encontrado en /app")

# Establecer variables de entorno críticas
port = os.environ.get("PORT", "8080")
os.environ["PYTHONPATH"] = "/app"  # ¡Solo /app, no incluir /app/mi_app_estudio!
os.environ["NODE_OPTIONS"] = "--max-old-space-size=256"
os.environ["REFLEX_ENV"] = "dev"
os.environ["NODE_ENV"] = "development"

print(f"PYTHONPATH establecido a: {os.environ['PYTHONPATH']}")
print(f"Directorio de trabajo: {os.getcwd()}")

# Ejecutar Reflex directamente desde aquí, NO a través de subprocess
try:
    # Asegurarse de que estamos en /app
    if os.getcwd() != "/app":
        print(f"⚠️ Cambiando directorio a /app desde {os.getcwd()}")
        os.chdir("/app")
    
    # Comando de Reflex
    cmd = [
        sys.executable, "-m", "reflex", "run",
        "--env", "dev",  # Forzar modo desarrollo para mejor depuración
        "--backend-host", "0.0.0.0",
        "--backend-port", port
    ]
    
    print(f"Ejecutando: {' '.join(cmd)} en {os.getcwd()}")
    
    # Ejecutar sin usar create_new_process_group para evitar comportamientos extraños
    subprocess.run(cmd, check=True)
    
except Exception as e:
    print(f"❌ ERROR ejecutando Reflex: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
