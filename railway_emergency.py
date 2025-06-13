#!/usr/bin/env python3
"""
RAILWAY EMERGENCY START - Solución definitiva
"""
import os
import sys
import shutil

print("🚨 RAILWAY EMERGENCY START")
print("=" * 50)

# Configurar entorno
port = os.environ.get('PORT', '8080')
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA")

print(f"🔌 Puerto: {port}")
print(f"📁 Directorio: {os.getcwd()}")

# Asegurar que estamos en /app
if not os.getcwd().endswith('/app'):
    os.chdir('/app')
    print(f"📁 Cambiado a: {os.getcwd()}")

# Estrategia 1: Usar main.py directamente
if os.path.exists('/app/main.py'):
    print("✅ Archivo main.py encontrado - usando aplicación simplificada")
    
    # Copiar configuración correcta
    if os.path.exists('/app/rxconfig_main.py'):
        shutil.copy('/app/rxconfig_main.py', '/app/rxconfig.py')
        print("✅ Configuración copiada")
    
    # Ejecutar aplicación
    cmd = [sys.executable, '-m', 'reflex', 'run', '--backend-host', '0.0.0.0', '--backend-port', port]
    print(f"🚀 Ejecutando: {' '.join(cmd)}")
    
    os.execv(sys.executable, cmd)

else:
    print("❌ main.py no encontrado")
    sys.exit(1)
