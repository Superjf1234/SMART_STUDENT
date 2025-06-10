#!/usr/bin/env python3

try:
    import ast
    with open('mi_app_estudio/mi_app_estudio.py', 'r') as f:
        content = f.read()
    
    ast.parse(content)
    print("✅ Archivo sin errores de sintaxis")
    
except SyntaxError as e:
    print(f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}")
    print(f"   Texto: {e.text.strip() if e.text else 'N/A'}")
    print(f"   Posición: {' ' * (e.offset - 1)}^")
except Exception as e:
    print(f"❌ Error: {e}")
