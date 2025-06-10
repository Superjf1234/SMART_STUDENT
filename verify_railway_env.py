#!/usr/bin/env python3
"""
Verificador de variables de entorno para Railway
Ejecutar esto para confirmar que las variables están configuradas correctamente
"""
import os

def verify_railway_environment():
    """Verificar que todas las variables críticas estén configuradas"""
    
    print("🔍 VERIFICANDO CONFIGURACIÓN DE RAILWAY")
    print("=" * 50)
    
    # Variables críticas que deben estar configuradas
    critical_vars = {
        'REFLEX_ENV': 'dev',
        'REFLEX_DEBUG': 'false', 
        'REFLEX_DISABLE_TELEMETRY': 'true',
        'REFLEX_SKIP_COMPILE': 'true',
        'REFLEX_NO_BUILD': 'true',
        'NODE_OPTIONS': '--max-old-space-size=64',
        'PYTHONUNBUFFERED': '1',
        'PYTHONDONTWRITEBYTECODE': '1',
        'NEXT_TELEMETRY_DISABLED': '1'
    }
    
    # Variables importantes de Railway
    railway_vars = ['PORT', 'RAILWAY_ENVIRONMENT', 'GEMINI_API_KEY']
    
    print("🎯 VARIABLES CRÍTICAS:")
    all_good = True
    
    for var, expected in critical_vars.items():
        current = os.environ.get(var, 'NOT_SET')
        status = "✅" if current == expected else "❌"
        print(f"{status} {var}: {current} (esperado: {expected})")
        if current != expected:
            all_good = False
    
    print("\n🏗️ VARIABLES DE RAILWAY:")
    for var in railway_vars:
        current = os.environ.get(var, 'NOT_SET')
        status = "✅" if current != 'NOT_SET' else "⚠️"
        print(f"{status} {var}: {current}")
    
    print("\n📊 RESUMEN:")
    if all_good:
        print("✅ TODAS LAS VARIABLES CRÍTICAS ESTÁN CONFIGURADAS CORRECTAMENTE")
        print("🚀 La aplicación debería funcionar sin problemas de memoria")
    else:
        print("❌ ALGUNAS VARIABLES CRÍTICAS NO ESTÁN CONFIGURADAS")
        print("⚠️ Esto causará errores de memoria y build de producción")
        print("\n📋 ACCIÓN REQUERIDA:")
        print("1. Ir a Railway Dashboard > Variables")
        print("2. Configurar las variables marcadas con ❌")
        print("3. Hacer Deploy para aplicar cambios")
    
    print("\n🔧 CONFIGURACIÓN ACTUAL DE NODE:")
    print(f"NODE_OPTIONS: {os.environ.get('NODE_OPTIONS', 'NOT_SET')}")
    
    print("\n🐍 CONFIGURACIÓN ACTUAL DE PYTHON:")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT_SET')}")
    print(f"PYTHONUNBUFFERED: {os.environ.get('PYTHONUNBUFFERED', 'NOT_SET')}")
    
    return all_good

if __name__ == "__main__":
    verify_railway_environment()
