#!/usr/bin/env python3
"""
Script de inicialización y despliegue para Railway
Incluye inicialización completa de Reflex
"""

import os
import sys
import subprocess

def run_command(cmd, description):
    """Ejecuta un comando y maneja errores"""
    print(f"\n=== {description} ===")
    print(f"Ejecutando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR en {description}: {e}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        return False

def main():
    print("=== SMART_STUDENT Railway Init & Deploy ===")
    
    # Variables de entorno
    port = os.environ.get('PORT', '8080')
    print(f"Puerto: {port}")
    
    # 1. Verificar estructura del proyecto
    if not os.path.exists('mi_app_estudio'):
        print("ERROR: Directorio mi_app_estudio no encontrado")
        sys.exit(1)
    
    # 2. Inicializar Reflex (esto creará .web/)
    if not run_command(['python', '-m', 'reflex', 'init'], "Inicializando Reflex"):
        print("Continuando sin inicialización...")
    
    # 3. Exportar (preparar para producción)
    if not run_command(['python', '-m', 'reflex', 'export'], "Exportando aplicación"):
        print("Continuando sin exportación...")
    
    # 4. Ejecutar aplicación con argumentos CORREGIDOS
    cmd = [
        'python', '-m', 'reflex', 'run',
        '--env', 'prod',
        '--backend-host', '0.0.0.0',
        '--backend-port', port
        # ❌ REMOVIDO: '--frontend-host', '0.0.0.0' (no existe en Reflex)
    ]
    
    print(f"\n=== Iniciando aplicación ===")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR al ejecutar aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
