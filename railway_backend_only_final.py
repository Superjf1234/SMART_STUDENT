#!/usr/bin/env python3
"""
Railway Backend-Only Start - Estrategia final
Servir solo backend que maneja archivos estáticos automáticamente
"""

import os
import sys
import subprocess
import signal
import time

def setup_environment():
    """Configurar entorno para backend-only"""
    print("=== RAILWAY BACKEND-ONLY STRATEGY ===")
    
    port = os.environ.get("PORT", "8080")
    host = "0.0.0.0"
    
    # Variables críticas
    os.environ["PORT"] = port
    os.environ["HOST"] = host
    os.environ["PYTHONPATH"] = "/app:/app/mi_app_estudio"
    
    # Configuración de memoria
    os.environ["NODE_OPTIONS"] = "--max-old-space-size=400"
    os.environ["NODE_ENV"] = "development"
    
    # Variables específicas para backend-only
    os.environ["REFLEX_BACKEND_HOST"] = host
    os.environ["REFLEX_BACKEND_PORT"] = port
    
    print(f"PORT: {port}")
    print(f"HOST: {host}")
    print(f"MODE: Backend-only (serves static files)")
    
    return port, host

def test_import():
    """Test de importación"""
    try:
        print("Testing import...")
        os.chdir("/app/mi_app_estudio")
        sys.path.insert(0, "/app")
        sys.path.insert(0, "/app/mi_app_estudio")
        import mi_app_estudio.mi_app_estudio
        print("✓ Import successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def start_backend_only(port, host):
    """Estrategia: Solo backend que sirve todo"""
    
    print("🎯 Starting BACKEND-ONLY mode...")
    
    # Cambiar al directorio de la app
    os.chdir("/app/mi_app_estudio")
    
    # ESTRATEGIA 1: Reflex export + servir archivos estáticos
    try:
        print("STEP 1: Building static files...")
        
        # Primero hacer export para generar archivos estáticos
        export_cmd = [
            sys.executable, "-m", "reflex", "export",
            "--backend-host", host,
            "--backend-port", port
        ]
        
        print(f"Export command: {' '.join(export_cmd)}")
        result = subprocess.run(export_cmd, timeout=120, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Export successful")
        else:
            print(f"Export failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("Export timeout - continuing with regular backend...")
    except Exception as e:
        print(f"Export error: {e}")
    
    # ESTRATEGIA 2: Backend regular con configuración simplificada
    try:
        print("STEP 2: Starting backend server...")
        
        # Solo backend - sin frontend separado
        cmd = [
            sys.executable, "-m", "reflex", "run",
            "--backend-host", host,
            "--backend-port", port,
            "--env", "dev",
            "--no-frontend"  # Intentar sin frontend
        ]
        
        print(f"Backend command: {' '.join(cmd)}")
        os.execv(sys.executable, cmd)
        
    except Exception as e:
        print(f"Backend-only failed: {e}")
        
        # FALLBACK: Regular run pero forzar binding específico
        try:
            print("FALLBACK: Regular run with port binding...")
            
            # Forzar que use solo el puerto especificado
            os.environ["REFLEX_FRONTEND_PORT"] = str(int(port) + 1)  # Frontend en puerto diferente
            
            cmd = [
                sys.executable, "-m", "reflex", "run",
                "--backend-host", host,
                "--backend-port", port,
                "--env", "dev"
            ]
            
            print(f"Fallback command: {' '.join(cmd)}")
            os.execv(sys.executable, cmd)
            
        except Exception as e2:
            print(f"All strategies failed: {e2}")
            return 1

def signal_handler(signum, frame):
    """Handle termination signals"""
    print(f"Received signal {signum}")
    sys.exit(0)

def main():
    """Main function"""
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        port, host = setup_environment()
        
        if not test_import():
            print("Cannot proceed without successful import")
            return 1
        
        return start_backend_only(port, host)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
