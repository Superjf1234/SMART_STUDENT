#!/usr/bin/env python3
"""
Script de respaldo para Railway - Configuración mínima
"""
import os
import sys
import subprocess

# Configurar variables de entorno
os.environ['PORT'] = os.environ.get('PORT', '8080')
os.environ['HOST'] = '0.0.0.0'

def main():
    port = os.environ['PORT']
    host = os.environ['HOST']
    
    print(f"[INFO] Iniciando aplicación en {host}:{port}")
    
    # Cambiar al directorio de la aplicación si existe
    if os.path.exists('mi_app_estudio'):
        os.chdir('mi_app_estudio')
        print("[INFO] Cambiado al directorio mi_app_estudio")
    
    # Comando simple de Reflex sin argumentos problemáticos
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'prod',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"[INFO] Ejecutando: {' '.join(cmd)}")
    
    # Ejecutar el comando
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error al ejecutar reflex: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
