#!/usr/bin/env python3
"""
Script de prueba para verificar que la aplicación Reflex funciona correctamente
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, '/workspaces/SMART_STUDENT')

def test_app_loading():
    """Prueba que la aplicación se puede cargar sin errores."""
    try:
        print("Intentando importar reflex...")
        import reflex as rx
        print("✅ Reflex importado correctamente")
        
        print("Intentando importar el módulo de la aplicación...")
        from mi_app_estudio import mi_app_estudio
        print("✅ Módulo de aplicación importado correctamente")
        
        print("Verificando que la app esté definida...")
        app = mi_app_estudio.app
        print(f"✅ App definida: {type(app)}")
        
        print("Verificando que AppState esté definido...")
        AppState = mi_app_estudio.AppState
        print(f"✅ AppState definido: {type(AppState)}")
        
        print("Verificando funciones principales...")
        main_dashboard = mi_app_estudio.main_dashboard
        login_page = mi_app_estudio.login_page
        index = mi_app_estudio.index
        print("✅ Funciones principales definidas")
        
        print("✅ TODAS LAS VERIFICACIONES PASARON")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_component_creation():
    """Prueba que los componentes se puedan crear."""
    try:
        print("Probando creación de componentes...")
        from mi_app_estudio import mi_app_estudio
        
        # Intentar crear el componente index
        index_component = mi_app_estudio.index()
        print(f"✅ Componente index creado: {type(index_component)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear componentes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== PRUEBA DE CARGA DE APLICACIÓN ===")
    
    if test_app_loading():
        print("\n=== PRUEBA DE CREACIÓN DE COMPONENTES ===")
        if test_component_creation():
            print("\n🎉 TODAS LAS PRUEBAS PASARON - LA APLICACIÓN ESTÁ LISTA")
        else:
            print("\n❌ PROBLEMAS CON LA CREACIÓN DE COMPONENTES")
    else:
        print("\n❌ PROBLEMAS CON LA CARGA DE LA APLICACIÓN")
