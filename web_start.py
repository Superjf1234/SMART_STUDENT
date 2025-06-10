#!/usr/bin/env python3
"""
Script de despliegue web para Railway - Versión actualizada
Este script reemplaza completamente los scripts anteriores para evitar problemas de caché
"""

import os
import sys
import subprocess
import time

def log_message(message):
    """Imprime mensaje con timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_command_safe(cmd, description, critical=True):
    """Ejecuta un comando de forma segura con logging detallado"""
    log_message(f"INICIANDO: {description}")
    log_message(f"Comando: {' '.join(cmd)}")
    
    try:
        # Ejecutar comando
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Mostrar output en tiempo real
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            log_message(f"ÉXITO: {description}")
            return True
        else:
            log_message(f"ERROR: {description} - Código de salida: {process.returncode}")
            if critical:
                sys.exit(1)
            return False
            
    except Exception as e:
        log_message(f"EXCEPCIÓN en {description}: {str(e)}")
        if critical:
            sys.exit(1)
        return False

def setup_environment():
    """Configura el entorno de Railway"""
    log_message("=== CONFIGURACIÓN DEL ENTORNO ===")
    
    # Variables de entorno para Railway
    os.environ['PORT'] = os.environ.get('PORT', '8080')
    os.environ['HOST'] = '0.0.0.0'
    
    log_message(f"Puerto configurado: {os.environ['PORT']}")
    log_message(f"Host configurado: {os.environ['HOST']}")

def main():
    """Función principal de despliegue"""
    log_message("=== INICIANDO DESPLIEGUE EN RAILWAY ===")
    log_message(f"Directorio de trabajo: {os.getcwd()}")
    log_message(f"Python version: {sys.version}")
    
    # Configurar entorno
    setup_environment()
    
    # Paso 1: Instalar dependencias Python
    run_command_safe(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Instalación de dependencias Python"
    )
    
    # Paso 2: Ir al directorio de la aplicación
    app_dir = "/app/mi_app_estudio"
    if os.path.exists("mi_app_estudio"):
        os.chdir("mi_app_estudio")
        log_message("Cambiado al directorio mi_app_estudio")
    else:
        log_message("Directorio mi_app_estudio no encontrado, continuando en directorio actual")
    
    # Paso 3: Inicializar Reflex
    run_command_safe(
        [sys.executable, "-m", "reflex", "init"],
        "Inicialización de Reflex",
        critical=False
    )
    
    # Paso 4: Exportar frontend (generar archivos web)
    run_command_safe(
        [sys.executable, "-m", "reflex", "export"],
        "Exportación del frontend",
        critical=False
    )
    
    # Paso 5: Iniciar la aplicación
    port = os.environ.get('PORT', '8080')
    host = os.environ.get('HOST', '0.0.0.0')
    
    cmd = [
        sys.executable, "-m", "reflex", "run",
        "--env", "prod",
        "--backend-host", host,
        "--backend-port", port
    ]
    
    log_message("=== INICIANDO APLICACIÓN ===")
    run_command_safe(cmd, f"Iniciando aplicación Reflex en {host}:{port}")

if __name__ == "__main__":
    main()
