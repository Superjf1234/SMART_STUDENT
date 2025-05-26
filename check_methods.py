#!/usr/bin/env python3
"""
Script para verificar los métodos implementados en AppState
"""

import importlib.util
import inspect
import sys

# Importar AppState sin ejecutar el código completo
def import_module_without_init_execution(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    # Cargar state.py directamente
    state_module = import_module_without_init_execution("state", "/workspaces/SMART_STUDENT/mi_app_estudio/state.py")
    AppState = getattr(state_module, "AppState")

    # Verificar métodos críticos
    critical_methods = [
        "generate_summary", 
        "download_pdf", 
        "download_resumen_pdf", 
        "download_map_pdf", 
        "download_cuestionario_pdf"
    ]

    print("\n🔍 Verificando métodos críticos en AppState:")
    all_ok = True
    for method_name in critical_methods:
        if hasattr(AppState, method_name):
            method = getattr(AppState, method_name)
            if inspect.iscoroutinefunction(method) or inspect.isgeneratorfunction(method):
                print(f"✅ {method_name}: Implementado correctamente como método asíncrono")
            else:
                print(f"⚠️ {method_name}: Implementado pero NO es asíncrono")
        else:
            print(f"❌ {method_name}: NO implementado")
            all_ok = False

    if all_ok:
        print("\n🟢 Todos los métodos críticos están implementados correctamente.")
        sys.exit(0)
    else:
        print("\n🔴 Faltan implementaciones de métodos críticos.")
        sys.exit(1)

except Exception as e:
    print(f"\n❌ Error al verificar métodos: {e}")
    sys.exit(2)
