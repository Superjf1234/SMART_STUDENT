#!/usr/bin/env python3
"""
Script súper simple para Railway - SMART_STUDENT
Solo ejecuta reflex con los parámetros correctos
"""
import os
import sys

def main():
    print("=== SMART_STUDENT para Railway ===", flush=True)
    
    # Configurar variables de entorno básicas
    if 'GEMINI_API_KEY' not in os.environ:
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    
    # Puerto de Railway
    port = os.environ.get('PORT', '8080')
    print(f"Puerto: {port}", flush=True)
    
    # Comando simplificado sin --frontend-host
    cmd = [
        "python", "-m", "reflex", "run",
        "--env", "prod",
        "--backend-host", "0.0.0.0",
        "--backend-port", port,
        "--frontend-port", port
    ]
    
    print(f"Comando: {' '.join(cmd)}", flush=True)
    
    # Ejecutar directamente
    os.execvp("python", cmd)

if __name__ == "__main__":
    main()
