#!/usr/bin/env python3
"""
Script para analizar específicamente la función login_page()
"""

def analyze_login_function():
    with open('/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar el inicio de la función login_page
    start_line = None
    end_line = None
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def login_page('):
            start_line = i
            print(f"Función login_page() comienza en línea {i + 1}: {line.strip()}")
            break
    
    if start_line is None:
        print("No se encontró la función login_page()")
        return
    
    # Encontrar la siguiente función
    for i in range(start_line + 1, len(lines)):
        line = lines[i].strip()
        if line.startswith('def ') and not line.startswith('def _'):
            end_line = i
            print(f"Siguiente función encontrada en línea {i + 1}: {line}")
            break
    
    if end_line is None:
        print("No se encontró el final de la función login_page()")
        return
    
    print(f"\nLa función login_page() debería estar entre las líneas {start_line + 1} y {end_line}")
    
    # Analizar paréntesis solo en esa función
    function_lines = lines[start_line:end_line]
    stack = []
    
    for i, line in enumerate(function_lines):
        line_num = start_line + i + 1
        for j, char in enumerate(line):
            if char in '([{':
                stack.append((char, line_num, j + 1))
            elif char in ')]}':
                if not stack:
                    print(f"❌ Paréntesis de cierre inesperado '{char}' en línea {line_num}, posición {j + 1}")
                    continue
                
                open_char, open_line, open_pos = stack.pop()
                expected_close = {'(': ')', '[': ']', '{': '}'}[open_char]
                
                if char != expected_close:
                    print(f"❌ Tipo de paréntesis incorrecto: '{open_char}' abierto en línea {open_line}, pero cerrado con '{char}' en línea {line_num}")
    
    # Verificar si quedan paréntesis sin cerrar
    if stack:
        print(f"❌ Paréntesis sin cerrar en la función login_page():")
        for char, line_num, pos in stack:
            print(f"   '{char}' abierto en línea {line_num}, posición {pos}")
            print(f"      {lines[line_num-1].rstrip()}")
            print(f"      {' ' * (pos-1)}^")
    else:
        print("✅ Todos los paréntesis están balanceados en la función login_page()")

if __name__ == "__main__":
    analyze_login_function()
