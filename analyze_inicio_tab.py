#!/usr/bin/env python3

def analyze_inicio_tab():
    with open('/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py', 'r') as f:
        content = f.read()
    
    # Intentar compilar
    try:
        compile(content, 'mi_app_estudio.py', 'exec')
        print("✅ El archivo compila correctamente")
        return
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e.msg} en línea {e.lineno}")
        
        # Mostrar contexto del error
        lines = content.split('\n')
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        
        print(f"\nContexto del error (líneas {start+1}-{end}):")
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1:4}: {lines[i]}")
        
        # Encontrar función inicio_tab y analizar paréntesis
        in_function = False
        paren_count = 0
        function_start = None
        
        for i, line in enumerate(lines):
            if 'def inicio_tab():' in line:
                in_function = True
                function_start = i + 1
                print(f"\n📍 Función inicio_tab() encontrada en línea {function_start}")
                continue
                
            if in_function:
                if line.strip().startswith('def ') and i > function_start + 5:
                    print(f"🔚 Fin de función en línea {i+1}")
                    print(f"📊 Paréntesis sin cerrar en inicio_tab(): {paren_count}")
                    
                    # Mostrar las últimas líneas de la función
                    print(f"\n📋 Últimas líneas de la función:")
                    for j in range(max(function_start, i-10), i):
                        balance_info = ""
                        if j >= 1055:  # Mostrar balance cerca del error
                            line_parens = lines[j].count('(') - lines[j].count(')')
                            paren_count += line_parens
                            balance_info = f" [balance: {paren_count}]"
                        print(f"    {j+1:4}: {lines[j].rstrip()}{balance_info}")
                    break
                    
                # Solo contar paréntesis si estamos en la función
                paren_count += line.count('(') - line.count(')')

if __name__ == "__main__":
    analyze_inicio_tab()
