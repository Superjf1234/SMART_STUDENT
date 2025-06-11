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
    
    # VERIFICAR Y CONFIGURAR GEMINI_API_KEY
    if 'GEMINI_API_KEY' not in os.environ or not os.environ['GEMINI_API_KEY']:
        print("⚠️ GEMINI_API_KEY no encontrada, usando clave de desarrollo")
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    else:
        print("✓ GEMINI_API_KEY encontrada en variables de entorno")
    
    # Puerto de Railway
    port = os.environ.get('PORT', '8000')
    
    # PYTHONPATH para Railway
    os.environ['PYTHONPATH'] = '/app:/app/mi_app_estudio'
    
    print(f"✓ REFLEX_ENV: {os.environ['REFLEX_ENV']} (FORZADO A DESARROLLO)")
    print(f"✓ NODE_ENV: {os.environ['NODE_ENV']} (FORZADO A DESARROLLO)")
    print(f"✓ GEMINI_API_KEY: {'Configurada' if os.environ.get('GEMINI_API_KEY') else 'NO ENCONTRADA'}")
    print(f"✓ Puerto Frontend/Backend: {port} (MISMO PUERTO PARA RAILWAY HEALTHCHECK)")
    print(f"✓ PYTHONPATH: {os.environ['PYTHONPATH']}")
    print("=" * 60)
    print("⚠️ NOTA: Este script FUERZA modo desarrollo, ignora configuración externa")
    print("🚂 RAILWAY: Frontend y Backend usan el MISMO puerto para healthcheck")
    print("=" * 60)
    
    # COMANDO CORREGIDO - SIN OPCIONES INVÁLIDAS
    # ⚠️ RAILWAY FIX: Solo usar opciones válidas de Reflex
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'dev',  # ← HARDCODED - NUNCA CAMBIAR A PROD
        '--backend-host', '0.0.0.0',
        '--backend-port', port
        # ← REMOVIDO: --frontend-host y --frontend-port (opciones inválidas)
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
