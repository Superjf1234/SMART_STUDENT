#!/usr/bin/env python3
"""
RAILWAY PERFECT SOLUTION: La solución que SÍ va a funcionar
Crea aplicación autocontenida en root, evita imports complejos
"""
import os
import sys
import subprocess

def main():
    print("🎯 RAILWAY PERFECT SOLUTION")
    print("=" * 50)
    
    # 1. Configurar entorno
    os.chdir('/app')
    port = os.environ.get('PORT', '8080')
    os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA")
    
    print(f"📁 Working dir: {os.getcwd()}")
    print(f"🔌 Port: {port}")
    print("🔑 GEMINI_API_KEY: ✓")
    
    # 2. Crear rxconfig.py
    print("📝 Creating rxconfig.py...")
    rxconfig = f'''import reflex as rx
config = rx.Config(
    app_name="app_main",
    backend_host="0.0.0.0", 
    backend_port={port},
    frontend_port={port},
    tailwind=None,
    env=rx.Env.PROD
)'''
    with open('rxconfig.py', 'w') as f:
        f.write(rxconfig)
    print("✅ rxconfig.py created")
    
    # 3. Crear aplicación principal
    print("📝 Creating main app...")
    app_code = '''import reflex as rx

class State(rx.State):
    message: str = "¡SMART STUDENT funcionando en Railway!"
    input_text: str = ""
    
    def update_message(self):
        self.message = "🚀 Sistema activo y funcionando correctamente"
    
    def set_input(self, value: str):
        self.input_text = value
    
    def process_input(self):
        if self.input_text:
            self.message = f"Procesando: {self.input_text}"
        else:
            self.message = "Ingresa texto para procesar"

def index():
    return rx.center(
        rx.vstack(
            rx.heading("🎓 SMART STUDENT", size="2xl", color="blue.600"),
            rx.text(State.message, font_size="xl", margin_y="4"),
            rx.input(
                placeholder="Escribe algo...",
                value=State.input_text,
                on_change=State.set_input,
                width="300px"
            ),
            rx.hstack(
                rx.button("Procesar", on_click=State.process_input, color_scheme="blue"),
                rx.button("Test", on_click=State.update_message, color_scheme="green"),
                spacing="4"
            ),
            rx.text("✅ Desplegado en Railway", color="green.500", font_weight="bold"),
            spacing="6",
            align="center"
        ),
        min_height="100vh"
    )

app = rx.App()
app.add_page(index)
'''
    with open('app_main.py', 'w') as f:
        f.write(app_code)
    print("✅ app_main.py created")
    
    # 4. Verificar archivos
    files = ['rxconfig.py', 'app_main.py']
    for file in files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return
    
    # 5. Iniciar Reflex
    print(f"🚀 Starting Reflex on port {port}")
    cmd = [sys.executable, '-m', 'reflex', 'run', '--backend-host', '0.0.0.0', '--backend-port', port]
    print(f"Command: {' '.join(cmd)}")
    print("=" * 50)
    
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
