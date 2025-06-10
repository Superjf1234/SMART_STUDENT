#!/usr/bin/env python3
"""
Script de despliegue Railway - Versión de emergencia
Versión ultra-simplificada para resolver problemas de healthcheck
"""

import os
import sys
import subprocess
import time

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

def main():
    log("=== INICIANDO DESPLIEGUE RAILWAY (EMERGENCY VERSION) ===")
    
    # Configurar variables de entorno
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    log(f"Puerto: {port}, Host: {host}")
    log(f"Directorio actual: {os.getcwd()}")
    log(f"Contenido del directorio: {os.listdir('.')}")
    
    # Verificar estructura
    if os.path.exists('mi_app_estudio'):
        log("Directorio mi_app_estudio encontrado")
        if os.path.exists('mi_app_estudio/mi_app_estudio.py'):
            log("Archivo principal encontrado")
        else:
            log("ERROR: Archivo principal no encontrado")
            return
    else:
        log("ERROR: Directorio mi_app_estudio no encontrado")
        return
    
    # Cambiar al directorio de la aplicación
    os.chdir('mi_app_estudio')
    log(f"Cambiado a: {os.getcwd()}")
    
    # Instalar reflex si no está disponible
    try:
        log("Verificando Reflex...")
        result = subprocess.run([sys.executable, '-c', 'import reflex'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            log("Instalando Reflex...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'reflex>=0.3.6'], 
                         check=True)
    except Exception as e:
        log(f"Error con Reflex: {e}")
    
    # Inicializar Reflex (solo si es necesario)
    if not os.path.exists('.web'):
        log("Inicializando Reflex...")
        try:
            subprocess.run([sys.executable, '-m', 'reflex', 'init'], 
                         check=True, timeout=60)
        except Exception as e:
            log(f"Error en reflex init: {e}")
    
    # Comando de inicio más simple
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'prod',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    log(f"Ejecutando comando: {' '.join(cmd)}")
    
    # Ejecutar con timeout de healthcheck
    try:
        # Ejecutar el proceso
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT, universal_newlines=True)
        
        # Mostrar output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                # Verificar si el servidor está listo
                if 'App running' in output or 'Server started' in output:
                    log("✅ Servidor iniciado correctamente")
        
        return_code = process.poll()
        if return_code != 0:
            log(f"❌ Proceso terminó con código: {return_code}")
        
    except KeyboardInterrupt:
        log("Proceso interrumpido")
    except Exception as e:
        log(f"❌ Error ejecutando comando: {e}")
        # Fallback a comando aún más simple
        log("Intentando comando de emergencia...")
        try:
            subprocess.run([
                sys.executable, 'mi_app_estudio.py'
            ], check=True)
        except Exception as e2:
            log(f"❌ Comando de emergencia también falló: {e2}")

if __name__ == '__main__':
    main()
