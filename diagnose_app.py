#!/usr/bin/env python3
"""
Script para ejecutar la aplicación y capturar errores
"""

import subprocess
import sys
import os

def run_reflex_check():
    """Ejecuta reflex init para verificar la configuración."""
    try:
        print("=== EJECUTANDO REFLEX INIT ===")
        result = subprocess.run(
            [sys.executable, "-m", "reflex", "init"],
            cwd="/workspaces/SMART_STUDENT",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout ejecutando reflex init")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando reflex init: {e}")
        return False

def check_syntax_with_ast():
    """Verifica la sintaxis usando AST."""
    try:
        print("=== VERIFICANDO SINTAXIS CON AST ===")
        import ast
        
        with open("/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        ast.parse(content)
        print("✅ Sintaxis correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}")
        if e.text:
            print(f"Texto: {e.text.strip()}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("=== DIAGNÓSTICO DE LA APLICACIÓN ===")
    
    # Verificar sintaxis primero
    syntax_ok = check_syntax_with_ast()
    
    if syntax_ok:
        # Si la sintaxis está bien, probar reflex init
        reflex_ok = run_reflex_check()
        
        if reflex_ok:
            print("✅ Aplicación lista para ejecutar")
        else:
            print("❌ Problemas con reflex init")
    else:
        print("❌ Problemas de sintaxis - revisar el archivo")
