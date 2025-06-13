#!/usr/bin/env python3
"""
RAILWAY ULTIMATE FIX: Crear una app autocontenida sin imports complejos
"""

import os
import sys

def main():
    print("🔥 RAILWAY ULTIMATE FIX")
    print("=" * 50)
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"🔌 Puerto: {port}")
    print(f"🌐 Host: {host}")
    
    # GEMINI API KEY (fallback)
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("🔑 GEMINI_API_KEY configurado")
    
    # Estrategia DEFINITIVA: Crear una app minimal sin imports cruzados
    app_path = '/app/mi_app_estudio'
    os.chdir(app_path)
    print(f"📁 Working dir: {os.getcwd()}")
    
    # Crear app minimal en memoria
    minimal_app_code = '''
import reflex as rx
import os

# App minimal sin imports cruzados
class SimpleState(rx.State):
    message: str = "¡Smart Student funcionando en Railway!"
    
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Smart Student", size="9"),
            rx.text(SimpleState.message),
            rx.button("Test Button", 
                     on_click=lambda: SimpleState.set_message("¡Botón funcionando!")),
            spacing="4",
            align="center"
        ),
        height="100vh",
        justify="center",
        align="center"
    )

# Crear app
app = rx.App()
app.add_page(index)
'''
    
    # Escribir la app minimal
    with open('minimal_app.py', 'w') as f:
        f.write(minimal_app_code)
    
    print("✅ Created minimal app without complex imports")
    
    # Ejecutar la app minimal
    cmd = [
        sys.executable, '-c',
        f'''
import sys
sys.path.insert(0, "{app_path}")
exec(open("minimal_app.py").read())
import subprocess
subprocess.run(["{sys.executable}", "-m", "reflex", "run", "--backend-host", "{host}", "--backend-port", "{port}"])
'''
    ]
    
    print(f"🚀 Running minimal app...")
    
    # Ejecutar
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
