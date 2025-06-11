#!/usr/bin/env python3
"""
start_railway_single_port.py - Railway con UN SOLO PUERTO
Configura Reflex para usar el mismo puerto para frontend y backend
"""
import os
import sys
import subprocess
import time

def setup_environment():
    """Configurar entorno para Railway con un solo puerto"""
    # FORZAR DESARROLLO
    os.environ['REFLEX_ENV'] = 'dev'
    os.environ['NODE_ENV'] = 'development'
    os.environ['NEXT_BUILD'] = 'false'
    os.environ['SKIP_BUILD_OPTIMIZATION'] = 'true'
    os.environ['NEXT_TELEMETRY_DISABLED'] = '1'
    os.environ['DISABLE_TELEMETRY'] = '1'
    
    # GEMINI API KEY
    if 'GEMINI_API_KEY' not in os.environ or not os.environ['GEMINI_API_KEY']:
        print("⚠️ GEMINI_API_KEY no encontrada, usando clave de desarrollo")
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    
    # PYTHONPATH
    os.environ['PYTHONPATH'] = '/app:/app/mi_app_estudio'
    
    # Puerto único
    port = os.environ.get('PORT', '8080')
    
    print("🚂 RAILWAY - CONFIGURACIÓN UN SOLO PUERTO")
    print("=" * 60)
    print(f"✓ REFLEX_ENV: {os.environ['REFLEX_ENV']}")
    print(f"✓ NODE_ENV: {os.environ['NODE_ENV']}")
    print(f"✓ Puerto Único: {port} (Frontend + Backend)")
    print(f"✓ GEMINI_API_KEY: Configurada")
    print("=" * 60)
    
    return port

def start_reflex_single_port(port):
    """Iniciar Reflex con configuración de puerto único"""
    
    # Opción 1: Comando directo con mismo puerto
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'dev',
        '--host', '0.0.0.0',  # Host único
        '--port', port,       # Puerto único
        '--no-frontend'       # Desactivar servidor frontend separado
    ]
    
    print("🔥 COMANDO EJECUTADO (PUERTO ÚNICO):")
    print(" ".join(cmd))
    print("=" * 60)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error con --no-frontend, intentando método alternativo...")
        return start_reflex_alternative(port)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 1
    
    return 0

def start_reflex_alternative(port):
    """Método alternativo: servidor integrado"""
    
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'dev',
        '--backend-host', '0.0.0.0',
        '--backend-port', port,
        '--frontend-host', '0.0.0.0',
        '--frontend-port', port,
        '--loglevel', 'info'
    ]
    
    print("🔄 MÉTODO ALTERNATIVO (PUERTOS IDÉNTICOS):")
    print(" ".join(cmd))
    print("=" * 60)
    
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"❌ ERROR ALTERNATIVO: {e}")
        return 1
    
    return 0

def main():
    """Función principal"""
    port = setup_environment()
    return start_reflex_single_port(port)

if __name__ == "__main__":
    sys.exit(main())
