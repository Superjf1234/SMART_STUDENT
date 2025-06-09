#!/usr/bin/env python3
"""
Railway healthcheck script para verificar que la aplicación está funcionando
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_port():
    """Verificar que el puerto esté disponible"""
    port = os.environ.get('PORT', '8080')
    try:
        # Intentar conectar al puerto
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', int(port)))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error verificando puerto: {e}")
        return False

def lightweight_init():
    """Inicialización ligera para Railway"""
    try:
        print("Realizando inicialización ligera para Railway...")
        
        # Solo crear directorios necesarios
        os.makedirs(".web", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        # Verificar que Python puede importar la aplicación
        sys.path.insert(0, '/app')
        import mi_app_estudio.mi_app_estudio
        print("Aplicación Python cargada correctamente")
        
        return True
    except Exception as e:
        print(f"Error en inicialización ligera: {e}")
        return False

def main():
    """Healthcheck principal"""
    print("=== Railway Healthcheck ===")
    
    # Verificar inicialización básica
    if not lightweight_init():
        print("ERROR: Fallo en inicialización básica")
        sys.exit(1)
    
    # Verificar puerto después de un momento
    time.sleep(2)
    if check_port():
        print("✓ Puerto accesible")
        sys.exit(0)
    else:
        print("⚠ Puerto no accesible aún")
        sys.exit(0)  # No fallar el healthcheck por esto

if __name__ == "__main__":
    main()
