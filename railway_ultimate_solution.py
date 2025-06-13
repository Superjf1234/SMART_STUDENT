#!/usr/bin/env python3
"""
RAILWAY ULTIMATE SOLUTION - Solución definitiva sin conflictos de módulos
"""
import os
import sys
import shutil

def create_simple_app():
    """Crea una aplicación Reflex simple en el directorio raíz"""
    print("🚀 RAILWAY ULTIMATE SOLUTION")
    print("=" * 50)
    
    # Configurar entorno
    port = os.environ.get('PORT', '8080')
    os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA")
    
    print(f"🌐 Puerto: {port}")
    print(f"📁 Working from: /app")
    
    os.chdir('/app')
    
    # Crear aplicación simple
    app_content = '''import reflex as rx
import os
from typing import List

# Variables de entorno
os.environ.setdefault("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

class StudyState(rx.State):
    """Estado de la aplicación de estudio"""
    user_name: str = ""
    study_topic: str = ""
    current_page: str = "home"
    message: str = "¡Bienvenido a SMART STUDENT!"
    questions: List[str] = []
    score: int = 0
    
    def set_name(self, name: str):
        self.user_name = name
        
    def set_topic(self, topic: str):
        self.study_topic = topic
        
    def start_study(self):
        if self.user_name and self.study_topic:
            self.current_page = "study"
            self.message = f"¡Hola {self.user_name}! Vamos a estudiar {self.study_topic}"
        else:
            self.message = "Por favor completa todos los campos"
            
    def go_home(self):
        self.current_page = "home"
        
    def generate_quiz(self):
        self.questions = [
            f"¿Qué es {self.study_topic}?",
            f"¿Cómo se aplica {self.study_topic}?",
            f"¿Cuáles son los beneficios de {self.study_topic}?"
        ]
        self.current_page = "quiz"
        self.message = f"Quiz generado sobre {self.study_topic}"

def navbar():
    return rx.hstack(
        rx.heading("🎓 SMART STUDENT", color="white"),
        rx.spacer(),
        rx.text("Railway Deployment", color="whiteAlpha.800"),
        bg="blue.600",
        px="4",
        py="3",
        w="100%"
    )

def home_page():
    return rx.vstack(
        rx.heading("¡Bienvenido a SMART STUDENT!", size="2xl", mb="6"),
        rx.text("Tu asistente de estudio inteligente", color="gray.600", mb="8"),
        
        rx.card(
            rx.vstack(
                rx.input(
                    placeholder="Tu nombre",
                    value=StudyState.user_name,
                    on_change=StudyState.set_name,
                    mb="4"
                ),
                rx.input(
                    placeholder="Tema de estudio",
                    value=StudyState.study_topic,
                    on_change=StudyState.set_topic,
                    mb="4"
                ),
                rx.button(
                    "Comenzar Estudio",
                    on_click=StudyState.start_study,
                    color_scheme="blue",
                    size="lg",
                    w="100%"
                ),
                spacing="4"
            ),
            p="6",
            max_w="400px"
        ),
        
        rx.cond(
            StudyState.message != "¡Bienvenido a SMART STUDENT!",
            rx.alert(StudyState.message, status="info", mt="4")
        ),
        
        align="center",
        spacing="6",
        py="8"
    )

def study_page():
    return rx.vstack(
        rx.heading(f"Estudiando: {StudyState.study_topic}", size="xl", mb="6"),
        
        rx.card(
            rx.vstack(
                rx.button(
                    "📝 Generar Quiz",
                    on_click=StudyState.generate_quiz,
                    color_scheme="green",
                    size="lg",
                    w="100%",
                    mb="4"
                ),
                rx.button(
                    "🏠 Volver al Inicio",
                    on_click=StudyState.go_home,
                    color_scheme="gray",
                    size="lg",
                    w="100%"
                ),
                spacing="4"
            ),
            p="6",
            max_w="400px"
        ),
        
        align="center",
        spacing="6",
        py="8"
    )

def quiz_page():
    return rx.vstack(
        rx.heading("Quiz de Estudio", size="xl", mb="6"),
        
        rx.card(
            rx.vstack(
                rx.foreach(
                    StudyState.questions,
                    lambda q: rx.text(f"• {q}", mb="2")
                ),
                rx.button(
                    "Volver al Estudio",
                    on_click=lambda: StudyState.set_page("study"),
                    color_scheme="blue",
                    mt="4"
                ),
                spacing="4"
            ),
            p="6",
            max_w="600px"
        ),
        
        align="center",
        spacing="6",
        py="8"
    )

def index():
    return rx.vstack(
        navbar(),
        rx.container(
            rx.cond(
                StudyState.current_page == "home",
                home_page(),
                rx.cond(
                    StudyState.current_page == "study",
                    study_page(),
                    rx.cond(
                        StudyState.current_page == "quiz",
                        quiz_page(),
                        home_page()
                    )
                )
            ),
            max_w="1200px",
            p="4"
        ),
        spacing="0",
        min_h="100vh",
        bg="gray.50"
    )

# Crear aplicación
app = rx.App()
app.add_page(index, route="/", title="SMART STUDENT")
'''
    
    # Escribir aplicación
    with open('/app/app.py', 'w') as f:
        f.write(app_content)
    print("✅ Aplicación creada: app.py")
    
    # Crear rxconfig.py simple
    config_content = f'''import reflex as rx
import os

port = int(os.environ.get("PORT", "8080"))

config = rx.Config(
    app_name="app",
    backend_host="0.0.0.0",
    backend_port=port,
    frontend_port=3000,
    tailwind=None,
)
'''
    
    with open('/app/rxconfig.py', 'w') as f:
        f.write(config_content)
    print("✅ Configuración creada: rxconfig.py")
    
    return True

def start_reflex():
    """Iniciar Reflex"""
    print("\n🚀 INICIANDO REFLEX")
    print("=" * 30)
    
    port = os.environ.get('PORT', '8080')
    print(f"🌐 Puerto: {port}")
    
    # Verificar archivos
    files_ok = True
    for file in ['/app/app.py', '/app/rxconfig.py']:
        if os.path.exists(file):
            print(f"✅ {file} encontrado")
        else:
            print(f"❌ {file} no encontrado")
            files_ok = False
    
    if not files_ok:
        return False
    
    # Iniciar Reflex
    cmd = [sys.executable, '-m', 'reflex', 'run', '--backend-host', '0.0.0.0', '--backend-port', port]
    print(f"🚀 Comando: {' '.join(cmd)}")
    print("⏳ Iniciando...")
    
    os.execv(sys.executable, cmd)

def main():
    print("🎯 RAILWAY ULTIMATE SOLUTION")
    print("Objetivo: Crear app simple sin conflictos de módulos")
    print("=" * 50)
    
    if create_simple_app():
        start_reflex()
    else:
        print("❌ Error creando aplicación")
        sys.exit(1)

if __name__ == "__main__":
    main()
