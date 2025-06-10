#!/usr/bin/env python3
"""
Script para analizar específicamente los paréntesis en la función login_page
"""

def analyze_login_parentheses():
    with open('mi_app_estudio/mi_app_estudio.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar inicio y fin de login_page
    start_line = None
    end_line = None
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def login_page():'):
            start_line = i
        elif start_line is not None and line.strip().startswith('def ') and not line.strip().startswith('def login_page()'):
            end_line = i
            break
    
    if start_line is None:
        print("No se encontró la función login_page()")
        return
    
    if end_line is None:
        end_line = len(lines)
    
    print(f"Función login_page() desde línea {start_line + 1} hasta {end_line}")
    
    # Analizar paréntesis línea por línea
    open_parens = 0
    paren_stack = []
    
    for i in range(start_line, end_line):
        line = lines[i]
        line_num = i + 1
        
        for j, char in enumerate(line):
            if char == '(':
                open_parens += 1
                paren_stack.append((line_num, j + 1, char))
            elif char == ')':
                if paren_stack:
                    paren_stack.pop()
                    open_parens -= 1
                else:
                    print(f"⚠️  Paréntesis de cierre sin apertura en línea {line_num}, posición {j + 1}")
    
    print(f"\nResultado del análisis:")
    print(f"Paréntesis abiertos sin cerrar: {open_parens}")
    
    if paren_stack:
        print(f"\nParéntesis sin cerrar:")
        for line_num, pos, char in paren_stack:
            line_content = lines[line_num - 1].strip()
            print(f"   Línea {line_num}, posición {pos}: '{char}'")
            print(f"      {line_content}")
            if pos <= len(line_content):
                print(f"      {' ' * (pos - 1)}^")
    
    # Mostrar las últimas 10 líneas de la función
    print(f"\nÚltimas líneas de la función (líneas {max(start_line + 1, end_line - 10)}-{end_line}):")
    for i in range(max(start_line, end_line - 10), end_line):
        line_num = i + 1
        line_content = lines[i].rstrip()
        print(f"   {line_num:4d}: {line_content}")

if __name__ == "__main__":
    analyze_login_parentheses()
