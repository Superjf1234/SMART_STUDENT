#!/bin/bash
# Script para arreglar el problema específico de rx.cond en resumen_tab

echo "===== FINAL RAILWAY FIX ====="
echo "Creando arreglo para el error de AssertionError en rx.cond de resumen_tab"

# Crear un archivo simple con la implementación correcta
cat > railway_direct_fix.py << EOL
"""
Script de arranque optimizado para Railway que resuelve el problema específico con rx.cond
"""

import reflex as rx
import sys, os
import importlib.util
import importlib

def fix_import_issues():
    """
    Configura el entorno para importar correctamente los módulos en Railway.
    """
    # Asegurarse de que la carpeta mi_app_estudio esté en el path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

    # Asegurarse de que la carpeta backend esté en el path
    backend_dir = os.path.join(current_dir, "backend")
    if os.path.exists(backend_dir):
        sys.path.insert(0, backend_dir)

def fix_resumen_tab():
    """
    Corrige el problema en resumen_tab() donde hay un uso incorrecto de rx.cond()
    """
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mi_app_estudio", "mi_app_estudio.py")
    
    if not os.path.exists(file_path):
        print(f"ERROR: No se pudo encontrar el archivo {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la zona problemática en resumen_tab
        if "def resumen_tab():" not in content:
            print("ERROR: No se encontró la función resumen_tab() en el archivo")
            return False
        
        # Corregir cualquier uso de rx.cond sin componentes válidos
        fixed_content = content.replace(
            "rx.cond(\n            (AppState.resumen_content != \"\") | (AppState.puntos_content != \"\"),",
            "rx.cond(\n            (AppState.resumen_content != \"\") | (AppState.puntos_content != \"\"), rx.fragment("
        )
        
        # Asegurarnos de cerrar el paréntesis adicional del rx.fragment()
        fixed_content = fixed_content.replace(
            "        ),\n    )",
            "        )),\n    )"
        )
        
        # Guardar el archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"INFO: Archivo {file_path} corregido exitosamente")
        return True
    
    except Exception as e:
        print(f"ERROR: Ocurrió un error al corregir el archivo: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_all_cond_usages():
    """
    Busca y corrige todos los usos de rx.cond que no tienen componentes válidos
    """
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mi_app_estudio", "mi_app_estudio.py")
    
    if not os.path.exists(file_path):
        print(f"ERROR: No se pudo encontrar el archivo {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        fixed_count = 0
        i = 0
        
        while i < len(lines):
            line = lines[i]
            # Buscar líneas con rx.cond seguido por una condición sin componente
            if "rx.cond(" in line and i + 1 < len(lines):
                next_line = lines[i + 1]
                if "," in next_line and not any(x in next_line for x in ["rx.", "fragment(", "box(", "text(", "vstack("]):
                    # Esta condición parece no tener un componente después de la coma
                    fixed_line = next_line.replace(",", ", rx.fragment(", 1)
                    lines[i + 1] = fixed_line
                    # Buscar el cierre del cond para agregar el paréntesis de cierre del fragment
                    j = i + 2
                    depth = 1
                    while j < len(lines) and depth > 0:
                        if "(" in lines[j]:
                            depth += lines[j].count("(")
                        if ")" in lines[j]:
                            depth -= lines[j].count(")")
                        j += 1
                    
                    if j - 1 >= 0 and j - 1 < len(lines):
                        lines[j - 1] = lines[j - 1].replace(")", "))")
                    
                    fixed_count += 1
            
            i += 1
        
        if fixed_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"INFO: Se corrigieron {fixed_count} instancias de rx.cond en {file_path}")
        else:
            print("INFO: No se encontraron instancias de rx.cond para corregir")
        
        return True
    
    except Exception as e:
        print(f"ERROR: Ocurrió un error al corregir los usos de rx.cond: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Función principal que realiza todas las correcciones
    """
    fix_import_issues()
    
    # Intentar la corrección específica primero
    if fix_resumen_tab():
        print("✅ Corrección específica en resumen_tab() aplicada correctamente")
    else:
        print("❌ No se pudo aplicar la corrección específica")
    
    # Intentar la corrección general de todos los rx.cond
    if fix_all_cond_usages():
        print("✅ Corrección general de rx.cond aplicada correctamente")
    else:
        print("❌ No se pudo aplicar la corrección general")
    
    print("\nEjecutando la aplicación Reflex para Railway...")
    os.system("reflex init && reflex run --env prod --backend-only")

if __name__ == "__main__":
    main()
EOL

# Crear el nuevo Procfile para Railway
cat > Procfile << EOL
web: python railway_direct_fix.py
EOL

echo "✅ Archivos creados correctamente"
echo "Procfile actualizado para ejecutar el script de corrección"

# Añadir los archivos a git y hacer commit
git add Procfile railway_direct_fix.py
git commit -m "Fix: Solución para error AssertionError en rx.cond - Both arguments must be components"

echo "✅ Cambios guardados en Git"
echo "Para desplegar a Railway, ejecuta: git push railway main"
