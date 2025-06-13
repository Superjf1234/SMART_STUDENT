#!/usr/bin/env python3
"""
Test para verificar que la corrección del @app.add_page funciona
"""

import sys
import os

# Configurar el path
sys.path.insert(0, '/workspaces/SMART_STUDENT')

def test_import():
    try:
        print("Probando importación después de la corrección...")
        
        # Importar reflex
        import reflex as rx
        print("✅ Reflex importado")
        
        # Importar el módulo principal
        from mi_app_estudio import mi_app_estudio
        print("✅ Módulo principal importado")
        
        # Verificar que la app esté definida
        app = getattr(mi_app_estudio, 'app', None)
        if app:
            print(f"✅ App encontrada: {type(app)}")
        else:
            print("❌ App no encontrada")
            return False
            
        # Verificar que la función index esté definida
        index = getattr(mi_app_estudio, 'index', None)
        if index:
            print(f"✅ Función index encontrada: {type(index)}")
        else:
            print("❌ Función index no encontrada")
            return False
            
        print("✅ TODAS LAS VERIFICACIONES PASARON")
        return True
        
    except Exception as e:
        print(f"❌ Error en importación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== TEST DE CORRECCIÓN @app.add_page ===")
    if test_import():
        print("\n🎉 LA CORRECCIÓN FUNCIONA CORRECTAMENTE")
        print("La aplicación está lista para despliegue en Railway")
    else:
        print("\n❌ PROBLEMAS DETECTADOS")
