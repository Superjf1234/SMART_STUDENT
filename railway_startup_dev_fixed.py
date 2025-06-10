#!/usr/bin/env python3
"""
Script de inicio FIJO para Railway - Evita errores de NextRouter
Soluciona el problema de NextRouter not mounted y errores de build en producción
"""
import os
import sys
import subprocess
import time

def main():
    print("🚂 RAILWAY STARTUP - SMART STUDENT (FIXED)")
    print("=" * 60)
    
    # FORZAR MODO DESARROLLO (esto soluciona NextRouter error)
    os.environ['REFLEX_ENV'] = 'dev'
    os.environ['NODE_ENV'] = 'development'
    os.environ['NEXT_BUILD'] = 'false'
    os.environ['SKIP_BUILD_OPTIMIZATION'] = 'true'
    os.environ['NEXT_TELEMETRY_DISABLED'] = '1'
    os.environ['DISABLE_TELEMETRY'] = '1'
    
    # Configuración de memoria optimizada
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=512 --no-warnings'
    
    # Puerto de Railway
    port = os.environ.get('PORT', '8000')
    
    # PYTHONPATH para Railway
    current_dir = '/app'
    os.environ['PYTHONPATH'] = f'{current_dir}:{current_dir}/mi_app_estudio'
    
    print(f"✓ REFLEX_ENV: {os.environ['REFLEX_ENV']} (DESARROLLO)")
    print(f"✓ NODE_ENV: {os.environ['NODE_ENV']} (DESARROLLO)")  
    print(f"✓ Puerto: {port}")
    print(f"✓ PYTHONPATH: {os.environ['PYTHONPATH']}")
    print(f"✓ NODE_OPTIONS: {os.environ['NODE_OPTIONS']}")
    print("=" * 60)
    
    # Comando CORRECTO - FUERZA MODO DEV CON PUERTOS SEPARADOS
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'dev',  # ← ESTO ES CLAVE - EVITA NextRouter ERROR!
        '--backend-host', '0.0.0.0',
        '--backend-port', port,
        '--frontend-port', str(int(port) + 1)  # ← PUERTO SEPARADO PARA FRONTEND
    ]
    
    print("🔥 COMANDO EJECUTADO:")
    print(" ".join(cmd))
    print("=" * 60)
    
    try:
        # Ejecutar sin capturar output para ver logs en Railway
        result = subprocess.run(cmd)
        return result.returncode
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario")
        return 0
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
