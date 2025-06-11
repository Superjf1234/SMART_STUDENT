#!/usr/bin/env python3
"""
🚨 RAILWAY FIX URGENTE - SMART STUDENT
Configura GEMINI_API_KEY y corrige errores de component
"""
import os
import sys

def fix_railway_config():
    """Configura todas las variables de entorno necesarias para Railway"""
    print("🚨 RAILWAY FIX URGENTE - Configurando variables...")
    
    # 1. GEMINI_API_KEY (crítico)
    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠️ GEMINI_API_KEY no encontrada, configurando clave de desarrollo...")
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"  # Clave funcional
        print("✅ GEMINI_API_KEY configurada")
    else:
        print("✅ GEMINI_API_KEY ya configurada")
    
    # 2. Variables de Railway
    port = os.environ.get('PORT', '8080')
    os.environ['PORT'] = port
    os.environ['HOST'] = '0.0.0.0'
    os.environ['REFLEX_ENV'] = 'prod'
    os.environ['PYTHONPATH'] = '/app'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # 3. Variables para evitar errores de memoria
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=1024'
    
    print(f"✅ Puerto: {port}")
    print(f"✅ REFLEX_ENV: {os.environ['REFLEX_ENV']}")
    print(f"✅ PYTHONPATH: {os.environ['PYTHONPATH']}")
    print("=" * 60)

def run_reflex_safe():
    """Ejecuta Reflex con manejo de errores seguro"""
    import subprocess
    
    print("🚀 Iniciando SMART_STUDENT...")
    
    # Comando de Reflex optimizado
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'prod',
        '--backend-host', '0.0.0.0',
        '--backend-port', os.environ.get('PORT', '8080')
    ]
    
    print(f"📡 Comando: {' '.join(cmd)}")
    
    try:
        # Ejecutar Reflex
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando Reflex: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)

def main():
    print("🚨 RAILWAY EMERGENCY FIX - SMART STUDENT")
    print("=" * 60)
    
    # 1. Configurar variables de entorno
    fix_railway_config()
    
    # 2. Ejecutar aplicación
    run_reflex_safe()

if __name__ == "__main__":
    main()
