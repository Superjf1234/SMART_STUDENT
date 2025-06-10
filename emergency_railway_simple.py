#!/usr/bin/env python3
"""
Script de emergencia para Railway - Máxima simplicidad
"""
import os
import sys

# Configuración mínima obligatoria
os.environ['PORT'] = os.environ.get('PORT', '8080')
os.environ['HOST'] = '0.0.0.0'
os.environ['REFLEX_ENV'] = 'dev'  # Usar dev para evitar builds complejos
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['REFLEX_DISABLE_TELEMETRY'] = 'true'

print("🚀 Smart Student - Iniciando...")
print(f"📡 Puerto: {os.environ.get('PORT', '8080')}")

try:
    # Importar sin verificaciones adicionales
    import reflex as rx
    from mi_app_estudio.mi_app_estudio import app
    
    print("✅ Módulos cargados correctamente")
    
    # Ejecutar directamente con configuración mínima
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', '8080')),
        debug=False
    )
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("🔧 Intentando importación alternativa...")
    
    # Fallback básico
    try:
        sys.path.insert(0, '/app')
        import reflex as rx
        from mi_app_estudio.mi_app_estudio import app
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8080')))
    except Exception as e2:
        print(f"❌ Fallback falló: {e2}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error general: {e}")
    sys.exit(1)
