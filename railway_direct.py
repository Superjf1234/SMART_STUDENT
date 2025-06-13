#!/usr/bin/env python3
"""
Railway Ultra Simple Start - Direct execution
"""

import os
import sys

def main():
    """Inicio ultra directo para Railway"""
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"🚀 RAILWAY ULTRA DIRECT START")
    print(f"PORT: {port}, HOST: {host}")
    
    # Detectar ambiente
    if os.path.exists('/app/mi_app_estudio'):
        app_path = '/app/mi_app_estudio'
        base_path = '/app'
    else:
        app_path = '/workspaces/SMART_STUDENT/mi_app_estudio'
        base_path = '/workspaces/SMART_STUDENT'
    
    # Configurar entorno crítico
    os.environ['PYTHONPATH'] = f'{base_path}:{app_path}'
    os.chdir(app_path)
    
    print(f"📁 Working dir: {os.getcwd()}")
    
    # Comando directo - SIN subprocess, SIN procesos padre
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port,
        '--env', 'prod',  # FORZAR modo producción
        '--no-interactive'  # Sin prompts interactivos
    ]
    
    print(f"🎯 Direct exec: {' '.join(cmd)}")
    
    # EXECVP - Reemplaza completamente este proceso
    try:
        os.execvp(sys.executable, cmd)
    except Exception as e:
        print(f"❌ Exec failed: {e}")
        # Fallback: ejecutar directamente
        import subprocess
        subprocess.run(cmd)

if __name__ == '__main__':
    main()
