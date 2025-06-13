#!/usr/bin/env python3
"""
RAILWAY START SCRIPT - NO FLAGS VERSION
Script principal para Railway que evita usar flags incompatibles
"""

import os
import sys

print("🚀 SMART STUDENT - RAILWAY START")
print("=" * 50)

# Setup básico
port = os.environ.get("PORT", "8080")
print(f"🔌 Puerto: {port}")

# GEMINI API KEY con fallback
os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
print("🔑 GEMINI_API_KEY configurado")

# Python path
os.environ["PYTHONPATH"] = "/app:/app/mi_app_estudio"
print(f"🐍 PYTHONPATH: {os.environ['PYTHONPATH']}")

# Cambiar directorio
os.chdir("/app/mi_app_estudio")
print(f"📁 Directorio: {os.getcwd()}")

# Verificar que el módulo se puede importar
try:
    sys.path.insert(0, "/app")
    sys.path.insert(0, "/app/mi_app_estudio")
    import mi_app_estudio.mi_app_estudio
    print("✅ Módulo importado correctamente")
except Exception as e:
    print(f"❌ Error al importar: {e}")
    sys.exit(1)

# Comando Reflex SIN flags problemáticos
cmd = [
    sys.executable, "-m", "reflex", "run",
    "--backend-host", "0.0.0.0", 
    "--backend-port", port
]

print(f"🚀 Ejecutando: {' '.join(cmd)}")
print("=" * 50)

# Ejecutar
os.execv(sys.executable, cmd)
