#!/usr/bin/env python3
"""
Script de inicio optimizado específicamente para Railway
Evita el build de producción que causa out of memory
"""
import os
import sys
import subprocess
import time

def setup_railway_environment():
    """Configurar entorno optimizado para Railway"""
    print("=== Configurando entorno Railway optimizado ===")
    
    # Variables críticas para evitar build de producción
    os.environ['REFLEX_ENV'] = 'dev'  # FORZAR MODO DESARROLLO
    os.environ['NODE_ENV'] = 'development'  # EVITAR BUILD DE PRODUCCIÓN
    os.environ['NEXT_BUILD'] = 'false'  # DESHABILITAR BUILD
    
    # Configuración de memoria para Node.js
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=512'  # Reducir memoria Node
    
    # Puerto y host
    port = os.environ.get('PORT', '8080')
    os.environ['PORT'] = port
    os.environ['HOST'] = '0.0.0.0'
    
    # Python path
    os.environ['PYTHONPATH'] = '/app'
    
    print(f"✅ Puerto configurado: {port}")
    print(f"✅ Modo: DESARROLLO (evita build de producción)")
    print(f"✅ Memoria Node.js limitada: 512MB")

def ensure_web_directory():
    """Asegurar que existe el directorio .web básico"""
    print("📁 Verificando directorio .web...")
    
    if not os.path.exists('.web'):
        print("  Creando directorio .web...")
        os.makedirs('.web', exist_ok=True)
    
    # Crear package.json mínimo si no existe
    package_json_path = '.web/package.json'
    if not os.path.exists(package_json_path):
        print("  Creando package.json mínimo...")
        package_json_content = '''
{
  "name": "mi_app_estudio_web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "echo 'Build deshabilitado en Railway'",
    "start": "next start"
  },
  "dependencies": {
    "next": "^13.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
'''
        with open(package_json_path, 'w') as f:
            f.write(package_json_content.strip())
        print("  ✅ package.json creado")

def start_reflex_development():
    """Iniciar Reflex en modo desarrollo específico para Railway"""
    print("🚀 Iniciando Reflex en modo desarrollo para Railway...")
    
    port = os.environ.get('PORT', '8080')
    
    # Comando específico para Railway que evita build de producción
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'dev',  # MODO DESARROLLO EXPLÍCITO
        '--backend-host', '0.0.0.0',
        '--backend-port', port,
        '--frontend-port', port,
        '--no-frontend-build'  # EVITAR BUILD FRONTEND
    ]
    
    print(f"📋 Comando a ejecutar: {' '.join(cmd)}")
    
    try:
        # Ejecutar con timeout para evitar cuelgues
        subprocess.run(cmd, timeout=None)
    except subprocess.TimeoutExpired:
        print("⚠️  Proceso timeout, reintentando...")
        # Comando de respaldo más simple
        subprocess.run([
            sys.executable, '-m', 'reflex', 'run',
            '--env', 'dev'
        ])

def railway_emergency_start():
    """Inicio de emergencia ultra simple para Railway"""
    print("🆘 INICIO DE EMERGENCIA PARA RAILWAY")
    
    # Configuración mínima
    port = os.environ.get('PORT', '8080')
    os.environ['REFLEX_ENV'] = 'dev'
    os.environ['NODE_ENV'] = 'development'
    
    # Comando ultra simple
    try:
        subprocess.run([
            sys.executable, '-c',
            f"""
import reflex as rx
import os
os.environ['REFLEX_ENV'] = 'dev'
os.environ['PORT'] = '{port}'

# Configuración mínima
config = rx.Config(
    app_name="mi_app_estudio",
    env=rx.Env.DEV,
    backend_host="0.0.0.0",
    backend_port={port},
    frontend_port={port}
)

# Importar y ejecutar app
import mi_app_estudio.mi_app_estudio as app_module
app_module.app._compile()
app_module.app.run(host="0.0.0.0", port={port})
"""
        ])
    except Exception as e:
        print(f"❌ Error en inicio de emergencia: {e}")
        # Último recurso: servidor HTTP básico
        subprocess.run([
            sys.executable, '-c',
            f"""
import http.server
import socketserver
import os
os.chdir('/app')
PORT = {port}
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Servidor básico en puerto {{PORT}}")
    httpd.serve_forever()
"""
        ])

def main():
    """Función principal de inicio Railway"""
    print("🚂 === SMART STUDENT - INICIO RAILWAY OPTIMIZADO ===")
    
    try:
        # Paso 1: Configurar entorno
        setup_railway_environment()
        
        # Paso 2: Preparar directorios
        ensure_web_directory()
        
        # Paso 3: Intentar inicio normal
        start_reflex_development()
        
    except Exception as e:
        print(f"⚠️  Error en inicio normal: {e}")
        print("🔄 Cambiando a modo de emergencia...")
        railway_emergency_start()

if __name__ == "__main__":
    main()
