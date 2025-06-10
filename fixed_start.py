#!/usr/bin/env python3
"""
Script de inicio Railway - Corrección de rutas
Resuelve problemas de importación del backend
"""

import os
import sys
import subprocess
import time

def setup_python_path():
    """Configura el PYTHONPATH para las importaciones"""
    current_dir = os.getcwd()
    
    # Agregar el directorio raíz al PYTHONPATH
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Agregar el directorio mi_app_estudio al PYTHONPATH
    app_dir = os.path.join(current_dir, 'mi_app_estudio')
    if os.path.exists(app_dir) and app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    
    # Configurar variable de entorno PYTHONPATH
    python_path = os.pathsep.join([current_dir, app_dir])
    os.environ['PYTHONPATH'] = python_path
    
    print(f"[INFO] PYTHONPATH configurado: {python_path}")

def main():
    print("=== RAILWAY DEPLOYMENT - PATH FIXED VERSION ===")
    
    # Configurar rutas de Python
    setup_python_path()
    
    # Variables de entorno
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"[INFO] Puerto: {port}, Host: {host}")
    print(f"[INFO] Directorio actual: {os.getcwd()}")
    
    # Verificar estructura de archivos
    required_files = [
        'mi_app_estudio/mi_app_estudio.py',
        'backend/__init__.py',
        'requirements.txt'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"[✓] {file_path} encontrado")
        else:
            print(f"[✗] {file_path} NO encontrado")
            return 1
    
    # Cambiar al directorio de la aplicación MANTENIENDO el PYTHONPATH
    app_dir = 'mi_app_estudio'
    os.chdir(app_dir)
    print(f"[INFO] Cambiado a directorio: {os.getcwd()}")
    
    # Verificar que las importaciones funcionen
    try:
        print("[INFO] Probando importaciones...")
        subprocess.run([
            sys.executable, '-c', 
            'import reflex; from backend import db_logic; print("Importaciones OK")'
        ], check=True, cwd='..')
        print("[✓] Importaciones verificadas")
    except subprocess.CalledProcessError as e:
        print(f"[✗] Error en importaciones: {e}")
        # Continuar de todos modos
    
    # Comando de Reflex con PYTHONPATH configurado
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join([os.path.abspath('..'), os.getcwd()])
    
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'prod',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"[INFO] Ejecutando: {' '.join(cmd)}")
    print(f"[INFO] Con PYTHONPATH: {env.get('PYTHONPATH')}")
    
    # Ejecutar con el entorno corregido
    try:
        process = subprocess.Popen(
            cmd, 
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Mostrar output en tiempo real
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.rstrip())
        
        return_code = process.poll()
        print(f"[INFO] Proceso terminó con código: {return_code}")
        return return_code
        
    except Exception as e:
        print(f"[ERROR] Fallo al ejecutar comando: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
