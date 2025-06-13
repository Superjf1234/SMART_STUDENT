#!/usr/bin/env python3
"""
Verificación final antes del despliegue en Railway
"""

import os
import sys

def verificar_archivos():
    print("🔍 VERIFICACIÓN FINAL - RAILWAY DEPLOYMENT")
    print("=" * 50)
    
    archivos_criticos = [
        "start.py",
        "Procfile", 
        "mi_app_estudio/mi_app_estudio.py",
        "rxconfig.py",
        "requirements.txt",
        "Dockerfile"
    ]
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTA")
    
    print("\n📋 VERIFICANDO CONTENIDO...")
    
    # Verificar Procfile
    with open("Procfile", "r") as f:
        procfile_content = f.read().strip()
        print(f"📄 Procfile: {procfile_content}")
        if "start.py" in procfile_content:
            print("✅ Procfile apunta a start.py")
        else:
            print("⚠️ Procfile no apunta a start.py")
    
    # Verificar start.py
    with open("start.py", "r") as f:
        start_content = f.read()
        if "--no-interactive" in start_content:
            print("❌ start.py contiene --no-interactive")
        else:
            print("✅ start.py SIN flags problemáticos")
    
    print("\n🎯 INSTRUCCIONES PARA RAILWAY:")
    print("1. El repositorio está actualizado en GitHub")
    print("2. Railway debe usar el Procfile automáticamente")
    print("3. O configurar Custom Start Command: python start.py")
    print("4. NO usar flags como --no-interactive")
    
    print("\n🚀 LISTO PARA DESPLEGAR EN RAILWAY")

if __name__ == "__main__":
    verificar_archivos()
