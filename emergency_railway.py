#!/usr/bin/env python3
"""
EMERGENCY Railway Script - Último recurso
Script de emergencia si todo lo demás falla
"""

import os
import sys

def main():
    print("=== EMERGENCY RAILWAY SCRIPT ===")
    
    # Configuración mínima
    port = os.environ.get('PORT', '8080')
    
    # PYTHONPATH mínimo
    os.environ['PYTHONPATH'] = '/app:/app/mi_app_estudio'
    
    # Variables anti-SIGBUS
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=128'
    os.environ['NODE_ENV'] = 'development'
    
    # Cambiar al directorio
    os.chdir('mi_app_estudio')
    
    print(f"Starting on port {port}")
    
    # Comando mínimo absoluto
    cmd = [sys.executable, '-m', 'reflex', 'run', '--backend-host', '0.0.0.0', '--backend-port', port]
    
    print(f"Emergency command: {' '.join(cmd)}")
    
    # Ejecutar directamente
    os.execvpe(cmd[0], cmd, os.environ)

if __name__ == '__main__':
    main()
