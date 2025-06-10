#!/usr/bin/env python3
"""
Diagnóstico completo para Railway deployment
"""

import os
import sys
import subprocess

def check_file(filepath, description):
    """Verifica si un archivo existe y su tamaño"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {description}: {filepath} ({size} bytes)")
        return True
    else:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False

def check_python_imports():
    """Verifica las importaciones críticas"""
    print("\n=== VERIFICANDO IMPORTACIONES ===")
    
    imports_to_test = [
        "import reflex",
        "import os, sys, subprocess",
        "from mi_app_estudio import mi_app_estudio"
    ]
    
    for import_test in imports_to_test:
        try:
            exec(import_test)
            print(f"✅ {import_test}")
        except Exception as e:
            print(f"❌ {import_test} - Error: {e}")

def main():
    print("=== RAILWAY DEPLOYMENT DIAGNOSTIC ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    # Verificar archivos críticos
    print("\n=== VERIFICANDO ARCHIVOS CRÍTICOS ===")
    critical_files = [
        ("Procfile", "Railway process file"),
        ("requirements.txt", "Python dependencies"),
        ("ultra_simple_start.py", "Deployment script"),
        ("mi_app_estudio/mi_app_estudio.py", "Main application"),
        ("backend/__init__.py", "Backend module"),
        ("rxconfig.py", "Reflex configuration")
    ]
    
    all_files_ok = True
    for filepath, description in critical_files:
        if not check_file(filepath, description):
            all_files_ok = False
    
    # Verificar contenido del Procfile
    print("\n=== VERIFICANDO PROCFILE ===")
    try:
        with open("Procfile", "r") as f:
            procfile_content = f.read().strip()
            print(f"Procfile content: {procfile_content}")
    except Exception as e:
        print(f"❌ Error reading Procfile: {e}")
        all_files_ok = False
    
    # Verificar importaciones
    check_python_imports()
    
    # Verificar estructura de directorios
    print("\n=== VERIFICANDO ESTRUCTURA ===")
    required_dirs = ["mi_app_estudio", "backend", "assets"]
    for dirname in required_dirs:
        if os.path.exists(dirname) and os.path.isdir(dirname):
            files_count = len(os.listdir(dirname))
            print(f"✅ Directory {dirname}/ ({files_count} files)")
        else:
            print(f"❌ Directory {dirname}/ NOT FOUND")
            all_files_ok = False
    
    # Verificar sintaxis del archivo principal
    print("\n=== VERIFICANDO SINTAXIS ===")
    try:
        result = subprocess.run([
            sys.executable, "-m", "py_compile", "mi_app_estudio/mi_app_estudio.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Syntax check passed")
        else:
            print(f"❌ Syntax error: {result.stderr}")
            all_files_ok = False
    except Exception as e:
        print(f"❌ Could not check syntax: {e}")
    
    # Resumen final
    print("\n=== RESUMEN FINAL ===")
    if all_files_ok:
        print("🎉 ¡TODO LISTO PARA RAILWAY!")
        print("El deployment debería funcionar correctamente.")
        print("\nPróximos pasos esperados en Railway:")
        print("1. Instalar dependencias de requirements.txt")
        print("2. Ejecutar ultra_simple_start.py")
        print("3. Inicializar Reflex")
        print("4. Iniciar servidor en puerto $PORT")
    else:
        print("⚠️  HAY PROBLEMAS QUE RESOLVER")
        print("Revisar los errores arriba antes del deployment.")
    
    return 0 if all_files_ok else 1

if __name__ == "__main__":
    sys.exit(main())
