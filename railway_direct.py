#!/usr/bin/env python3
"""
RAILWAY FIXED - SIN FLAGS PROBLEMÁTICOS
Archivo sobrescrito para eliminar flags incompatibles
"""

import os
import sys

def main():
    """Inicio CORREGIDO para Railway - SIN flags problemáticos"""
    
    print("🆘 RAILWAY DIRECT - VERSIÓN CORREGIDA")
    print("=" * 50)
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"� Puerto: {port}")
    print(f"🌐 Host: {host}")
    
    # GEMINI API KEY (fallback)
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("🔑 GEMINI_API_KEY configurado")
    
    # Detectar ambiente
    if os.path.exists('/app/mi_app_estudio'):
        app_path = '/app/mi_app_estudio'
        base_path = '/app'
        print("🐳 Ambiente: Railway/Docker")
    else:
        app_path = '/workspaces/SMART_STUDENT/mi_app_estudio'
        base_path = '/workspaces/SMART_STUDENT'
        print("💻 Ambiente: Local")
    
    # Configurar entorno
    os.environ['PYTHONPATH'] = f'{base_path}:{app_path}'
    os.chdir(app_path)
    print(f"📁 Directorio: {os.getcwd()}")
    
    # Verificar imports
    try:
        sys.path.insert(0, base_path)
        sys.path.insert(0, app_path)
        import mi_app_estudio.mi_app_estudio
        print("✅ Módulo importado correctamente")
    except Exception as e:
        print(f"❌ Error de import: {e}")
        sys.exit(1)
    
    # Comando CORREGIDO - SIN flags problemáticos
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
        # REMOVIDOS: --env prod, --no-interactive
    ]
    
    print(f"🚀 Comando CORREGIDO: {' '.join(cmd)}")
    print("✅ SIN flags problemáticos")
    print("=" * 50)
    
    # Ejecutar
    try:
        os.execvp(sys.executable, cmd)
    except Exception as e:
        print(f"❌ Error de ejecución: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
