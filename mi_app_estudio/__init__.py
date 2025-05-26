"""
Módulo de inicialización para la aplicación SMART_STUDENT.
"""
# Importación explícita de la aplicación desde el módulo
try:
    from mi_app_estudio.mi_app_estudio import app
except ImportError:
    # Intenta una importación relativa como alternativa
    from .mi_app_estudio import app
