#!/usr/bin/env python3
"""
Script para resolver problemas de imports de Railway moviendo archivos clave al nivel raíz.
Esto resuelve el problema "No module named 'mi_app_estudio.cuestionario'; 'mi_app_estudio' is not a package"
"""

import os
import shutil

def main():
    print("🔧 Resolviendo problemas de imports para Railway...")
    
    # Directorio raíz del proyecto
    root_dir = "/workspaces/SMART_STUDENT"
    mi_app_dir = os.path.join(root_dir, "mi_app_estudio")
    
    # Archivos principales que necesitan estar disponibles
    key_files = [
        "cuestionario.py",
        "state.py", 
        "review_components.py",
        "utils.py",
        "evaluaciones.py",
        "shared.py",
        "help_translations.py",
        "translations.py"
    ]
    
    print("📁 Moviendo archivos clave al directorio raíz...")
    
    for file_name in key_files:
        src_path = os.path.join(mi_app_dir, file_name)
        dst_path = os.path.join(root_dir, file_name)
        
        if os.path.exists(src_path):
            try:
                # Crear backup si ya existe
                if os.path.exists(dst_path):
                    backup_path = dst_path + ".backup"
                    shutil.copy2(dst_path, backup_path)
                    print(f"📋 Backup created: {backup_path}")
                
                # Mover archivo
                shutil.copy2(src_path, dst_path)
                print(f"✅ Moved: {file_name}")
                
            except Exception as e:
                print(f"❌ Error moving {file_name}: {e}")
        else:
            print(f"⚠️ File not found: {src_path}")
    
    # Copiar el archivo principal de la app
    main_app_src = os.path.join(mi_app_dir, "mi_app_estudio.py")
    main_app_dst = os.path.join(root_dir, "app_main.py")
    
    if os.path.exists(main_app_src):
        try:
            shutil.copy2(main_app_src, main_app_dst)
            print(f"✅ Main app copied to: app_main.py")
        except Exception as e:
            print(f"❌ Error copying main app: {e}")
    
    print("🔄 Actualizando imports en app_main.py...")
    
    # Actualizar imports en app_main.py
    try:
        with open(main_app_dst, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar imports relativos con imports directos
        content = content.replace('from .cuestionario import', 'from cuestionario import')
        content = content.replace('from .review_components import', 'from review_components import')
        content = content.replace('from .state import', 'from state import')
        content = content.replace('from .utils import', 'from utils import')
        
        with open(main_app_dst, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Imports actualizados en app_main.py")
        
    except Exception as e:
        print(f"❌ Error actualizando imports: {e}")
    
    print("🔧 Actualizando startup script...")
    
    # Actualizar ultra_robust_start.py para usar app_main.py
    startup_script = os.path.join(root_dir, "ultra_robust_start.py")
    try:
        with open(startup_script, 'r', encoding='utf-8') as f:
            startup_content = f.read()
        
        # Reemplazar referencia al módulo
        startup_content = startup_content.replace(
            'app_module = "mi_app_estudio.mi_app_estudio"',
            'app_module = "app_main"'
        )
        
        with open(startup_script, 'w', encoding='utf-8') as f:
            f.write(startup_content)
        
        print("✅ Startup script actualizado")
        
    except Exception as e:
        print(f"❌ Error actualizando startup script: {e}")
    
    print("\n🎉 Fix aplicado. Los archivos ahora están en el directorio raíz y no dependen de la estructura de paquetes.")
    print("📝 El archivo principal es ahora: app_main.py")
    print("🚀 Railway debería poder importar todos los módulos correctamente.")

if __name__ == "__main__":
    main()
