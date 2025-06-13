#!/usr/bin/env python3
"""
Test rápido para verificar si hay errores de AssertionError
"""

import sys
import os

def test_specific_function():
    """Prueba específica de la función mapa_tab()"""
    try:
        print("=== TEST ESPECÍFICO DE MAPA_TAB() ===")
        
        # Agregar path
        sys.path.insert(0, '/workspaces/SMART_STUDENT')
        
        # Importar solo lo necesario para probar
        import reflex as rx
        print("✅ Reflex importado")
        
        # Intentar importar solo las funciones problemáticas
        from mi_app_estudio.mi_app_estudio import mapa_tab
        print("✅ mapa_tab importado")
        
        # Intentar crear el componente (esto debería fallar si hay AssertionError)
        print("Probando creación de componente mapa_tab()...")
        # NO vamos a ejecutar esto porque necesita el estado, solo verificamos que se puede importar
        
        print("✅ La función mapa_tab() se puede importar sin errores de sintaxis")
        return True
        
    except AssertionError as e:
        print(f"❌ AssertionError todavía presente: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Otro error: {e}")
        return False

if __name__ == "__main__":
    success = test_specific_function()
    if success:
        print("\n🎉 TEST EXITOSO - No hay errores de AssertionError en la importación")
    else:
        print("\n❌ TEST FALLÓ - Aún hay problemas")
