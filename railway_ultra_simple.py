#!/usr/bin/env python3
"""
Script ULTRA-SIMPLE para Railway - Solución final al conflicto de puertos
"""
import os
import sys
import subprocess

def main():
    print("🚂 RAILWAY ULTRA-SIMPLE STARTUP")
    print("=" * 50)
    
    # Configuración mínima pero efectiva
    os.environ['REFLEX_ENV'] = 'dev'
    os.environ['NODE_ENV'] = 'development'
    
    # Puerto principal de Railway
    port = os.environ.get('PORT', '8000')
    
    print(f"✓ Usando puerto: {port}")
    print(f"✓ Modo: {os.environ['REFLEX_ENV']}")
    print("=" * 50)
    
    # Comando SIMPLIFICADO - Sin especificar frontend port
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'dev',
        '--backend-host', '0.0.0.0',
        '--backend-port', port
        # NO especificamos frontend-port, dejamos que Reflex lo maneje automáticamente
    ]
    
    print("🔥 EJECUTANDO:", " ".join(cmd))
    print("=" * 50)
    
    # Ejecutar directamente
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Detenido")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
