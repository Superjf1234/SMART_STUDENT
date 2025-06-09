#!/usr/bin/env python3

def analyze_login_function_detailed():
    with open('/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar la función login_page
    start_line = None
    end_line = None
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def login_page():'):
            start_line = i
        elif start_line is not None and line.strip().startswith('def ') and 'login_page' not in line:
            end_line = i
            break
    
    if start_line is None:
        print("No se encontró la función login_page()")
        return
        
    print(f"Función login_page() encontrada desde línea {start_line + 1} hasta línea {end_line}")
    
    # Analizar paréntesis en la función
    paren_count = 0
    bracket_count = 0
    brace_count = 0
    
    paren_stack = []
    bracket_stack = []
    brace_stack = []
    
    for i in range(start_line, end_line):
        line = lines[i]
        line_num = i + 1
        
        for j, char in enumerate(line):
            if char == '(':
                paren_count += 1
                paren_stack.append((line_num, j + 1, line.rstrip()))
            elif char == ')':
                paren_count -= 1
                if paren_stack:
                    paren_stack.pop()
            elif char == '[':
                bracket_count += 1
                bracket_stack.append((line_num, j + 1, line.rstrip()))
            elif char == ']':
                bracket_count -= 1
                if bracket_stack:
                    bracket_stack.pop()
            elif char == '{':
                brace_count += 1
                brace_stack.append((line_num, j + 1, line.rstrip()))
            elif char == '}':
                brace_count -= 1
                if brace_stack:
                    brace_stack.pop()
    
    print(f"\nBalance final:")
    print(f"Paréntesis: {paren_count} (debe ser 0)")
    print(f"Corchetes: {bracket_count} (debe ser 0)")
    print(f"Llaves: {brace_count} (debe ser 0)")
    
    if paren_stack:
        print(f"\nParéntesis sin cerrar ({len(paren_stack)}):")
        for line_num, pos, line_content in paren_stack[-5:]:  # Mostrar solo los últimos 5
            print(f"  Línea {line_num}, posición {pos}: {line_content.strip()}")
    
    if bracket_stack:
        print(f"\nCorchetes sin cerrar ({len(bracket_stack)}):")
        for line_num, pos, line_content in bracket_stack[-5:]:
            print(f"  Línea {line_num}, posición {pos}: {line_content.strip()}")
    
    if brace_stack:
        print(f"\nLlaves sin cerrar ({len(brace_stack)}):")
        for line_num, pos, line_content in brace_stack[-5:]:
            print(f"  Línea {line_num}, posición {pos}: {line_content.strip()}")
    
    # Mostrar las últimas líneas de la función
    print(f"\nÚltimas 10 líneas de la función (líneas {end_line-9} a {end_line}):")
    for i in range(max(start_line, end_line-10), end_line):
        print(f"{i+1:4d}: {lines[i].rstrip()}")

if __name__ == "__main__":
    analyze_login_function_detailed()
