#!/usr/bin/env python3
"""
Diagnóstico de archivos que Railway podría estar ejecutando
"""

import os
import glob

def buscar_scripts_problema():
    print("🔍 DIAGNÓSTICO: Buscando scripts con flags problemáticos")
    print("=" * 60)
    
    archivos_python = glob.glob("*.py")
    problematicos = []
    
    for archivo in archivos_python:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
                if '--no-interactive' in contenido and 'REMOVIDOS' not in contenido:
                    print(f"❌ {archivo}: Contiene --no-interactive")
                    problematicos.append(archivo)
                elif '--env prod' in contenido and 'REMOVIDOS' not in contenido and 'CORREGIDO' not in contenido:
                    print(f"⚠️ {archivo}: Contiene --env prod")
                    problematicos.append(archivo)
                else:
                    print(f"✅ {archivo}: Limpio")
                    
        except Exception as e:
            print(f"❓ {archivo}: Error leyendo - {e}")
    
    print("\n📋 RESUMEN:")
    if problematicos:
        print(f"❌ {len(problematicos)} archivos con flags problemáticos:")
        for archivo in problematicos:
            print(f"   - {archivo}")
    else:
        print("✅ Todos los archivos Python están limpios")
    
    # Verificar configuraciones de Railway
    print("\n🚢 CONFIGURACIONES DE RAILWAY:")
    
    if os.path.exists("Procfile"):
        with open("Procfile", "r") as f:
            procfile = f.read().strip()
            print(f"📄 Procfile: {procfile}")
    
    # Buscar posibles start commands
    start_files = [f for f in archivos_python if 'start' in f.lower() or 'railway' in f.lower()]
    print(f"\n🚀 Scripts de inicio encontrados ({len(start_files)}):")
    for archivo in start_files:
        print(f"   - {archivo}")

if __name__ == "__main__":
    buscar_scripts_problema()
