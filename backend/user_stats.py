"""
Módulo para gestionar las estadísticas de usuario de manera persistente.
"""
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Directorio para almacenar los datos de usuario
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users")

def ensure_data_dir():
    """Asegura que exista el directorio de datos de usuario."""
    if not os.path.exists(USER_DATA_DIR):
        try:
            os.makedirs(USER_DATA_DIR, exist_ok=True)
            print(f"INFO (user_stats): Directorio de datos de usuario creado: {USER_DATA_DIR}")
        except Exception as e:
            print(f"ERROR (user_stats): No se pudo crear directorio de datos: {e}")
            return False
    return True

def get_user_stats_path(username: str) -> str:
    """Obtiene la ruta al archivo de estadísticas del usuario."""
    # Sanitizar el nombre de usuario para usarlo como nombre de archivo
    safe_username = "".join(c for c in username if c.isalnum() or c in "._- ").strip()
    safe_username = safe_username.replace(" ", "_").lower()
    
    if not safe_username:
        safe_username = "anonymous_user"
    
    return os.path.join(USER_DATA_DIR, f"{safe_username}_stats.json")

def load_user_stats(username: str) -> Dict[str, Any]:
    """
    Carga las estadísticas del usuario desde el archivo.
    
    Args:
        username: Nombre del usuario
        
    Returns:
        Diccionario con las estadísticas del usuario o diccionario vacío con estructura inicial
    """
    if not ensure_data_dir():
        return initialize_user_stats()
    
    stats_path = get_user_stats_path(username)
    
    try:
        if os.path.exists(stats_path):
            with open(stats_path, 'r', encoding='utf-8') as f:
                user_stats = json.load(f)
                print(f"INFO (user_stats): Estadísticas cargadas para el usuario '{username}'")
                return user_stats
    except Exception as e:
        print(f"ERROR (user_stats): Error al cargar estadísticas de usuario: {e}")
    
    # Si no hay archivo o falla al cargar, inicializar nuevas estadísticas
    return initialize_user_stats()

def initialize_user_stats() -> Dict[str, Any]:
    """
    Inicializa una estructura de estadísticas de usuario vacía.
    
    Returns:
        Diccionario con estructura base de estadísticas
    """
    return {
        "last_update": datetime.now().isoformat(),
        "creation_date": datetime.now().isoformat(),
        "maps": {
            "total_created": 0,
            "last_created": None,
            "by_theme": {}
        },
        "resumes": {
            "total_created": 0,
            "last_created": None
        },
        "quizzes": {
            "total_attempted": 0,
            "correct_answers": 0,
            "total_questions": 0
        },
        "sessions": {
            "total_count": 0,
            "last_login": None
        }
    }

def save_user_stats(username: str, stats: Dict[str, Any]) -> bool:
    """
    Guarda las estadísticas del usuario en un archivo.
    
    Args:
        username: Nombre del usuario
        stats: Diccionario con las estadísticas del usuario
        
    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    if not ensure_data_dir():
        return False
    
    stats_path = get_user_stats_path(username)
    
    try:
        # Actualizar la fecha de última actualización
        stats["last_update"] = datetime.now().isoformat()
        
        # Guardar en un archivo temporal primero para evitar corrupción de datos
        temp_path = f"{stats_path}.tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # Reemplazar el archivo original con el temporal
        if os.path.exists(stats_path):
            os.replace(temp_path, stats_path)
        else:
            os.rename(temp_path, stats_path)
        
        print(f"INFO (user_stats): Estadísticas guardadas para el usuario '{username}'")
        return True
    except Exception as e:
        print(f"ERROR (user_stats): Error al guardar estadísticas de usuario: {e}")
        return False

def increment_map_count(username: str, tema: Optional[str] = None) -> int:
    """
    Incrementa el contador de mapas conceptuales para un usuario.
    
    Args:
        username: Nombre del usuario
        tema: Tema del mapa conceptual (opcional)
        
    Returns:
        El número total de mapas creados después del incremento
    """
    stats = load_user_stats(username)
    
    # Incrementar contador general
    stats["maps"]["total_created"] += 1
    stats["maps"]["last_created"] = datetime.now().isoformat()
    
    # Registrar por tema si se proporciona
    if tema:
        tema_lower = tema.lower()
        if tema_lower not in stats["maps"]["by_theme"]:
            stats["maps"]["by_theme"][tema_lower] = 0
        stats["maps"]["by_theme"][tema_lower] += 1
    
    # Guardar los cambios
    save_user_stats(username, stats)
    
    return stats["maps"]["total_created"]

def get_total_maps(username: str) -> int:
    """
    Obtiene el número total de mapas conceptuales creados por el usuario.
    
    Args:
        username: Nombre del usuario
        
    Returns:
        El número total de mapas conceptuales creados
    """
    stats = load_user_stats(username)
    return stats["maps"]["total_created"]

def register_session(username: str) -> None:
    """
    Registra una nueva sesión para el usuario.
    
    Args:
        username: Nombre del usuario
    """
    stats = load_user_stats(username)
    
    stats["sessions"]["total_count"] += 1
    stats["sessions"]["last_login"] = datetime.now().isoformat()
    
    save_user_stats(username, stats)

def get_user_summary(username: str) -> Dict[str, Any]:
    """
    Obtiene un resumen de las estadísticas del usuario.
    
    Args:
        username: Nombre del usuario
        
    Returns:
        Diccionario con un resumen de estadísticas para mostrar en perfil
    """
    stats = load_user_stats(username)
    
    # Calcular estadísticas adicionales
    maps_count = stats["maps"]["total_created"]
    resumes_count = stats["resumes"]["total_created"]
    sessions_count = stats["sessions"]["total_count"]
    
    quiz_stats = stats["quizzes"]
    quiz_accuracy = 0
    if quiz_stats["total_questions"] > 0:
        quiz_accuracy = (quiz_stats["correct_answers"] / quiz_stats["total_questions"]) * 100
    
    # Top temas de mapas conceptuales
    top_themes = []
    if stats["maps"]["by_theme"]:
        sorted_themes = sorted(
            stats["maps"]["by_theme"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]  # Top 5 temas
        top_themes = [{"name": theme.capitalize(), "count": count} for theme, count in sorted_themes]
    
    # Construir resumen
    return {
        "maps_count": maps_count,
        "resumes_count": resumes_count,
        "sessions_count": sessions_count,
        "quiz_accuracy": round(quiz_accuracy, 1),
        "top_themes": top_themes,
        "last_activity": stats["last_update"]
    }
