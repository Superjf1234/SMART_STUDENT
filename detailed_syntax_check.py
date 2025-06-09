#!/usr/bin/env python3
"""
Script detallado para encontrar problemas de sintaxis en mi_app_estudio.py
"""

import ast
import sys

def check_syntax_detailed(filename):
    """
    Verifica la sintaxis del archivo Python y proporciona información detallada sobre errores.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Intentar parsear el código
        ast.parse(source_code, filename=filename)
        print(f"✅ {filename} tiene sintaxis válida")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en {filename}:")
        print(f"   Línea {e.lineno}: {e.text.strip() if e.text else 'N/A'}")
        print(f"   Posición: {e.offset}")
        print(f"   Error: {e.msg}")
        
        # Mostrar contexto alrededor del error
        print(f"\n📍 Contexto alrededor de la línea {e.lineno}:")
        lines = source_code.split('\n')
        start = max(0, e.lineno - 6)
        end = min(len(lines), e.lineno + 5)
        
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1:4d}: {lines[i]}")
            
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def find_unclosed_brackets(filename):
    """
    Busca paréntesis, corchetes y llaves sin cerrar.
    """
    print(f"\n🔍 Buscando brackets sin cerrar en {filename}...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    stack = []
    bracket_pairs = {'(': ')', '[': ']', '{': '}'}
    
    for line_num, line in enumerate(lines, 1):
        for pos, char in enumerate(line):
            if char in bracket_pairs:
                stack.append((char, line_num, pos, bracket_pairs[char]))
            elif char in bracket_pairs.values():
                if stack and stack[-1][3] == char:
                    stack.pop()
                else:
                    print(f"❌ Bracket de cierre inesperado '{char}' en línea {line_num}, posición {pos}")
                    
    # Mostrar brackets sin cerrar
    if stack:
        print(f"❌ Brackets sin cerrar encontrados:")
        for bracket, line_num, pos, expected_close in stack:
            print(f"   '{bracket}' abierto en línea {line_num}, posición {pos} (esperando '{expected_close}')")
            # Mostrar la línea
            print(f"   {line_num:4d}: {lines[line_num-1].rstrip()}")
            print(f"        {' ' * pos}^")
    else:
        print("✅ Todos los brackets están balanceados")

if __name__ == "__main__":
    filename = "mi_app_estudio/mi_app_estudio.py"
    
    print("🔧 Verificación detallada de sintaxis")
    print("=" * 50)
    
    # Verificar sintaxis
    is_valid = check_syntax_detailed(filename)
    
    if not is_valid:
        # Si hay errores de sintaxis, buscar brackets sin cerrar
        find_unclosed_brackets(filename)
