#!/usr/bin/env python3
"""
Script de inicio ultra-robusto para Railway con manejo de errores de compilación.
"""
import os
import sys
import subprocess
import time

def setup_environment():
    """Configurar variables de entorno optimizadas para Railway."""
    print("=== RAILWAY DEPLOYMENT - ULTRA ROBUST START (PORT-UNIFIED) ===")
    
    # Variables de entorno críticas
    port = os.environ.get("PORT", "8080")
    host = "0.0.0.0"
    
    os.environ["PORT"] = port
    os.environ["HOST"] = host
    os.environ["PYTHONPATH"] = "/app:/app/mi_app_estudio"
    
    # CRÍTICO: Configuraciones para unificar puertos
    os.environ["REFLEX_BACKEND_PORT"] = port
    os.environ["REFLEX_FRONTEND_PORT"] = port  # MISMO puerto
    os.environ["REFLEX_BACKEND_HOST"] = host
    
    # Configuraciones ultra-agresivas de memoria
    os.environ["NODE_OPTIONS"] = "--max-old-space-size=300"  # Incrementar un poco
    os.environ["NODE_ENV"] = "development"  # Forzar desarrollo
    os.environ["REFLEX_ENV"] = "dev"  # Modo desarrollo para evitar build pesado
    
    # Prevenir builds pesados y conflictos
    os.environ["NEXT_TELEMETRY_DISABLED"] = "1"
    
    print(f"PORT (unified): {port}")
    print(f"HOST: {host}")
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    print(f"REFLEX_BACKEND_PORT: {os.environ['REFLEX_BACKEND_PORT']}")
    print(f"REFLEX_FRONTEND_PORT: {os.environ['REFLEX_FRONTEND_PORT']}")
    print(f"REFLEX_ENV: {os.environ['REFLEX_ENV']}")
    print(f"Working directory: {os.getcwd()}")  # Mostrar directorio actual

def test_import():
    """Probar importación del módulo principal."""
    try:
        print("Testing app import...")
        import mi_app_estudio.mi_app_estudio
        print("✓ App import successful")
        return True
    except Exception as e:
        print(f"✗ App import failed: {e}")
        return False

def start_with_fallback():
    """Iniciar con múltiples estrategias de fallback."""
    setup_environment()
    
    if not test_import():
        print("ERROR: No se puede importar la aplicación")
        sys.exit(1)
    
    port = os.environ["PORT"]
    host = os.environ["HOST"]
    
    # CRITICAL FIX: NO cambiar de directorio - rxconfig.py está en /app
    print(f"Staying in root directory: {os.getcwd()}")
    
    # STRATEGY CRÍTICO: Solo backend que sirve frontend automáticamente
    try:
        print("STRATEGY: Backend serves frontend automatically...")
        
        # Variables de entorno específicas
        os.environ["REFLEX_BACKEND_PORT"] = port
        os.environ["REFLEX_BACKEND_HOST"] = host
        
        print(f"Unified server port: {port}")
        
        cmd = [
            sys.executable, "-m", "reflex", "run",
            "--backend-host", host,
            "--backend-port", port,
            "--env", "dev"
            # NO especificar --frontend-port
        ]
        print(f"Executing: {' '.join(cmd)}")
        
        # Usar exec directo
        os.execv(sys.executable, cmd)
        
    except Exception as e:
        print(f"Unified server failed: {e}")
        
        # Fallback: Intentar export y luego serve
        try:
            print("FALLBACK: Export and serve static...")
            
            # Primero hacer export
            export_cmd = [sys.executable, "-m", "reflex", "export"]
            subprocess.run(export_cmd, timeout=60)
            
            # Luego servir
            cmd = [
                sys.executable, "-m", "reflex", "run",
                "--backend-host", host,
                "--backend-port", port,
                "--env", "dev"
            ]
            print(f"Executing: {' '.join(cmd)}")
            os.execv(sys.executable, cmd)
            
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
    
    print("All strategies failed. Exiting.")
    sys.exit(1)

if __name__ == "__main__":
    start_with_fallback()
