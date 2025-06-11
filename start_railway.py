#!/usr/bin/env python3
"""
start_railway.py - VERSIÓN FORZADA DESARROLLO
IGNORA CUALQUIER CONFIGURACIÓN DE PRODUCCIÓN
"""
import os
import sys
import subprocess

def main():
    print("🚂 RAILWAY STARTUP - DESARROLLO FORZADO")
    print("=" * 60)
    
    # FORZAR DESARROLLO - SOBRESCRIBIR TODO
    os.environ['REFLEX_ENV'] = 'dev'
    os.environ['NODE_ENV'] = 'development'
    os.environ['NEXT_BUILD'] = 'false'
    os.environ['SKIP_BUILD_OPTIMIZATION'] = 'true'
    os.environ['NEXT_TELEMETRY_DISABLED'] = '1'
    os.environ['DISABLE_TELEMETRY'] = '1'
    
    # Puerto de Railway
    port = os.environ.get('PORT', '8000')
    
    print(f"✓ REFLEX_ENV: {os.environ['REFLEX_ENV']} (FORZADO A DESARROLLO)")
    print(f"✓ NODE_ENV: {os.environ['NODE_ENV']} (FORZADO A DESARROLLO)")
    print(f"✓ Puerto: {port}")
    print("=" * 60)
    print("⚠️ NOTA: Este script FUERZA modo desarrollo, ignora configuración externa")
    print("=" * 60)
    
    # COMANDO FORZADO - NUNCA USAR PRODUCCIÓN
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'dev',  # ← HARDCODED - NUNCA CAMBIAR A PROD
        '--backend-host', '0.0.0.0',
        '--backend-port', port,
        '--frontend-port', str(int(port) + 1)
    ]
    
    print("🔥 COMANDO EJECUTADO (DESARROLLO FORZADO):")
    print(" ".join(cmd))
    print("=" * 60)
    
    # Ejecutar
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
