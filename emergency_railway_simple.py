#!/usr/bin/env python3
"""
Script de emergencia para Railway - Evita todos los errores de Rich/Markup
"""
import os
import sys

# Configuración mínima
os.environ['PORT'] = os.environ.get('PORT', '8080')
os.environ['HOST'] = '0.0.0.0'
os.environ['REFLEX_ENV'] = 'dev'
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['REFLEX_DISABLE_TELEMETRY'] = 'true'
os.environ['REFLEX_DEBUG'] = 'false'

try:
    print("🚀 Iniciando Smart Student...")
    
    # Importar directamente sin usar subprocess
    import reflex as rx
    print("✓ Reflex importado")
    
    # Importar la app
    from mi_app_estudio.mi_app_estudio import app
    print("✓ App importada")
    
    # Ejecutar directamente
    print(f"🌐 Servidor iniciando en puerto {os.environ.get('PORT', '8080')}")
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', '8080')),
        debug=False
    )
    
except Exception as e:
    print(f"❌ Error crítico: {e}")
    sys.exit(1)
