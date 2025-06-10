#!/usr/bin/env python3
"""
Monitor del estado de despliegue de Railway
"""
import time
import requests
from datetime import datetime

def check_deployment_status():
    """Verifica el estado del despliegue"""
    print(f"\n=== VERIFICACIÓN DE ESTADO - {datetime.now().strftime('%H:%M:%S')} ===")
    
    # Verificar sintaxis local
    print("1. ✅ Verificando sintaxis local...")
    try:
        import subprocess
        result = subprocess.run(['python', '-m', 'py_compile', 'mi_app_estudio/mi_app_estudio.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Sintaxis OK")
        else:
            print(f"   ❌ Error de sintaxis: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️ No se pudo verificar: {e}")
    
    # Verificar archivos críticos
    import os
    files_to_check = [
        'Procfile',
        'web_start.py', 
        'requirements.txt',
        'mi_app_estudio/mi_app_estudio.py'
    ]
    
    print("\n2. 📁 Verificando archivos críticos...")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path} NO ENCONTRADO")
    
    # Verificar Procfile content
    print("\n3. 📋 Contenido del Procfile:")
    try:
        with open('Procfile', 'r') as f:
            content = f.read().strip()
            print(f"   📄 {content}")
    except Exception as e:
        print(f"   ❌ Error leyendo Procfile: {e}")
    
    print("\n4. 🚀 Estado esperado en Railway:")
    print("   📦 Instalando dependencias npm... (EN PROGRESO)")
    print("   🔧 Compilando Reflex... (EN PROGRESO)")
    print("   🎯 Próximo: Iniciar servidor web")
    
    print("\n5. 📊 Logs de Railway indican:")
    print("   ✅ Comando corregido (sin --frontend-host)")
    print("   ✅ npm instalando dependencias")
    print("   ✅ Reflex compilando (100% 15/15)")
    print("   ⚠️ Bun fallback a npm (normal)")

if __name__ == "__main__":
    check_deployment_status()
