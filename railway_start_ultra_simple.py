#!/usr/bin/env python3
"""
Comando de inicio ultra simple para Railway - Evita build de producción  
"""
import os
import sys

# CONFIGURACIÓN CRÍTICA PARA EVITAR OUT OF MEMORY
os.environ['REFLEX_ENV'] = 'dev'
os.environ['NODE_ENV'] = 'development'
os.environ['NEXT_BUILD'] = 'false'
os.environ['NODE_OPTIONS'] = '--max-old-space-size=512'

# Puerto Railway
port = os.environ.get('PORT', '8080')
print(f"🚂 Iniciando en puerto Railway: {port}")

# Importar y ejecutar directamente
try:
    import reflex as rx
    
    # Configuración mínima inline
    config = rx.Config(
        app_name="mi_app_estudio",
        env=rx.Env.DEV,  # DESARROLLO FORZADO
        backend_host="0.0.0.0",
        backend_port=int(port),
        frontend_port=int(port),
        tailwind=None,
        debug=True
    )
    
    # Importar app
    from mi_app_estudio import mi_app_estudio
    
    # Ejecutar directamente sin build
    print("🚀 Ejecutando Reflex en modo desarrollo...")
    mi_app_estudio.app.run(
        host="0.0.0.0",
        port=int(port),
        debug=True
    )
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("🔄 Intentando comando básico...")
    
    # Fallback con subprocess
    import subprocess
    subprocess.run([
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'dev',
        '--backend-host', '0.0.0.0',
        '--backend-port', port
    ])
