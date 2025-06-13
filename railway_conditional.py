#!/usr/bin/env python3
"""
RAILWAY CONDITIONAL IMPORTS: Intentar imports absolutos, si fallan usar relativos
"""

import os
import sys

def setup_imports():
    """Configurar imports de forma inteligente"""
    
    # Agregar paths necesarios
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Agregar tanto el directorio actual como el padre
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    return current_dir, parent_dir

def test_imports():
    """Probar diferentes estrategias de import"""
    
    print("🧪 Testing import strategies...")
    
    # Estrategia 1: Import absoluto
    try:
        import mi_app_estudio.mi_app_estudio
        print("✅ Absolute import works")
        return True
    except ImportError as e:
        print(f"❌ Absolute import failed: {e}")
    
    # Estrategia 2: Import simple del módulo
    try:
        import mi_app_estudio
        print("✅ Simple module import works")
        return True
    except ImportError as e:
        print(f"❌ Simple import failed: {e}")
    
    # Estrategia 3: Import local
    try:
        # Cambiar al directorio de la app y probar import local
        app_dir = '/app/mi_app_estudio'
        if os.path.exists(app_dir):
            os.chdir(app_dir)
            # Import del archivo principal sin package
            exec(open('mi_app_estudio.py').read())
            print("✅ Local file execution works")
            return True
    except Exception as e:
        print(f"❌ Local execution failed: {e}")
    
    return False

def main():
    print("🔧 RAILWAY CONDITIONAL IMPORTS")
    print("=" * 50)
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"🔌 Puerto: {port}")
    print(f"🌐 Host: {host}")
    
    # GEMINI API KEY (fallback)
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("🔑 GEMINI_API_KEY configurado")
    
    # Setup imports
    current_dir, parent_dir = setup_imports()
    print(f"📁 Current: {current_dir}")
    print(f"📁 Parent: {parent_dir}")
    
    # Test imports
    if not test_imports():
        print("❌ All import strategies failed")
        return
    
    # Cambiar al directorio de la app para reflex
    app_dir = '/app/mi_app_estudio'
    os.chdir(app_dir)
    print(f"📁 Working dir: {os.getcwd()}")
    
    # Comando
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}")
    
    # Ejecutar
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
