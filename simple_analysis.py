#!/usr/bin/env python3

def analyze_parens():
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
        
        # Contar paréntesis solo en la función login_page
        print(f"\nAnálisis de paréntesis en función login_page:")
        in_login = False
        paren_count = 0
        
        for i, line in enumerate(lines):
            if 'def login_page():' in line:
                in_login = True
                print(f"Inicio de función en línea {i+1}")
                continue
                
            if in_login:
                if line.strip().startswith('def ') and i > 930:
                    print(f"Fin de función en línea {i+1}")
                    print(f"Paréntesis sin cerrar: {paren_count}")
                    break
                    
                # Contar paréntesis (simplificado)
                paren_count += line.count('(') - line.count(')')
                
                if i >= 1045 and i <= 1055:
                    print(f"  Línea {i+1}: balance={paren_count} | {line.rstrip()}")

if __name__ == "__main__":
    analyze_parens()
