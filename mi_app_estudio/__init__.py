"""
Módulo de inicialización para la aplicación SMART_STUDENT.
"""

# Importar el app principal
try:
    from .mi_app_estudio import app
    __all__ = ['app']
    print("✅ SMART_STUDENT app module loaded successfully")
except ImportError as e:
    print(f"❌ Error loading app module: {e}")
    app = None
    __all__ = []
