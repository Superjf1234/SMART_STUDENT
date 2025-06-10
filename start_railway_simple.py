#!/usr/bin/env python3
"""
Script simplificado para ejecutar SMART_STUDENT en Railway
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Configurar variables de entorno básicas"""
    # Verificar GEMINI_API_KEY
    if 'GEMINI_API_KEY' not in os.environ:
        print("ADVERTENCIA: Variable GEMINI_API_KEY no está definida")
        # Usar una clave por defecto para desarrollo
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    
    # Railway siempre usa puerto 8080
    port = os.environ.get('PORT', '8080')
    print(f"Puerto configurado: {port}")
    return port

def ensure_frontend_deps():
    """Asegurar que las dependencias del frontend estén instaladas"""
    web_dir = Path(".web")
    if not web_dir.exists():
        print("ERROR: Directorio .web no existe. Ejecute 'reflex init' primero.")
        return False
    
    package_json = web_dir / "package.json"
    node_modules = web_dir / "node_modules"
    
    if not package_json.exists():
        print("ERROR: package.json no encontrado en .web/")
        return False
    
    if not node_modules.exists():
        print("Instalando dependencias frontend...")
        try:
            result = subprocess.run(
                ["npm", "install"], 
                cwd=str(web_dir), 
                check=True, 
                timeout=300,
                capture_output=True,
                text=True
            )
            print("Dependencias frontend instaladas correctamente")
        except subprocess.TimeoutExpired:
            print("ADVERTENCIA: Instalación de dependencias tomó demasiado tiempo")
        except subprocess.CalledProcessError as e:
            print(f"ERROR instalando dependencias: {e}")
            print(f"STDERR: {e.stderr}")
            return False
    else:
        print("Dependencias frontend ya están instaladas")
    
    return True

def main():
    """Función principal"""
    print("=== Iniciando SMART_STUDENT en Railway (Simple) ===")
    
    # Configurar entorno
    port = setup_environment()
    
    # Verificar dependencias frontend
    if not ensure_frontend_deps():
        print("ERROR: No se pudieron configurar las dependencias frontend")
        sys.exit(1)
    
    # Comando simplificado para Railway
    cmd = [
        "python", "-m", "reflex", "run", 
        "--env", "prod",
        "--backend-host", "0.0.0.0", 
        "--backend-port", port
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}")
    
    try:
        # Ejecutar el comando directamente sin capturar output
        os.execvp("python", cmd)
    except Exception as e:
        print(f"ERROR ejecutando Reflex: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
