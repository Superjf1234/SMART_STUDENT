#!/usr/bin/env python3
"""
Script para verificar solo la sintaxis de nuestro código, ignorando librerías externas
"""
import ast
import os
import sys

def check_file_syntax(file_path):
    """Verifica la sintaxis de un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f'Línea {e.lineno}: {e.msg}'
    except Exception as e:
        return False, str(e)

def main():
    """Función principal"""
    print("🔍 Verificando sintaxis de archivos del proyecto SMART_STUDENT...")
    
    # Archivos principales a verificar
    files_to_check = [
        'mi_app_estudio/mi_app_estudio.py',
        'mi_app_estudio/state.py',
        'mi_app_estudio/utils.py',
        'mi_app_estudio/translations.py',
        'mi_app_estudio/help_translations.py',
        'mi_app_estudio/shared.py',
        'mi_app_estudio/cuestionario.py',
        'mi_app_estudio/evaluaciones.py',
        'mi_app_estudio/review_components.py',
        'backend/config_logic.py',
        'backend/db_logic.py',
        'backend/login_logic.py',
        'backend/resumen_logic.py',
        'backend/map_logic.py',
        'backend/eval_logic.py',
        'rxconfig.py'
    ]
    
    errors_found = False
    files_checked = 0
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            is_valid, error = check_file_syntax(file_path)
            if is_valid:
                print(f'✅ {file_path}')
            else:
                print(f'❌ {file_path}: {error}')
                errors_found = True
            files_checked += 1
        else:
            print(f'⚠️  {file_path}: Archivo no encontrado')
    
    print(f"\n📊 Resumen: {files_checked} archivos verificados")
    
    if not errors_found:
        print("🎉 ¡Todos los archivos tienen sintaxis válida!")
        return 0
    else:
        print("❌ Se encontraron errores de sintaxis.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
