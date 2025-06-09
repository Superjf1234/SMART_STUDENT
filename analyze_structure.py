import ast
import sys

def check_file_structure(file_path):
    print(f"Analizando estructura de {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
            
        # Intenta parsear el archivo como código Python
        ast.parse(source)
        print("El archivo tiene una estructura válida de Python.")
        
        # Buscar funciones específicas y verificar su estructura
        tree = ast.parse(source)
        
        function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        print(f"Funciones encontradas: {len(function_names)}")
        print("Algunas funciones importantes:")
        
        important_funcs = ["login_page", "inicio_tab", "resumen_tab", "mapa_tab", "evaluacion_tab"]
        for func in important_funcs:
            if func in function_names:
                print(f"  ✓ {func}")
            else:
                print(f"  ✗ {func} (no encontrada)")
        
        return True
    except SyntaxError as e:
        print(f"Error de sintaxis: {e}")
        print(f"Línea: {e.lineno}, Columna: {e.offset}")
        print(f"Texto: {e.text}")
        return False
    except Exception as e:
        print(f"Error al analizar el archivo: {e}")
        return False

if __name__ == "__main__":
    target = "/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py"
    check_file_structure(target)
