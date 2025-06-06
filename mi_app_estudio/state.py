# Archivo: mi_app_estudio/state.py
# ¡VERSIÓN COMPLETA FINAL Y VERIFICADA!

"""
Módulo de estado base para SMART_STUDENT.
Contiene la definición de AppState que es usada por otros módulos.
"""

import reflex as rx
import sys, os, datetime, traceback, re
from typing import Dict, List, Optional, Set, Union, Any
import random
from .translations import get_translations
from .help_translations import get_help_questions

# --- IMPORTACIONES EXTERNAS Y BACKEND ---
# ¡NO DEBE HABER importaciones de .evaluaciones ni de .state aquí!
BACKEND_AVAILABLE = False
try:
    # Asume que la carpeta 'backend' está en la raíz del proyecto
    from backend import (
        config_logic,
        db_logic,
        login_logic,
        resumen_logic,
        map_logic,
        eval_logic,
    )
    # Initialize DB if function exists
    if hasattr(db_logic, "inicializar_db") and callable(db_logic.inicializar_db):
        db_logic.inicializar_db()
        print("INFO: Base de datos inicializada.")
    else:
        print("WARN: Función 'inicializar_db' no encontrada en db_logic.")
    print("INFO: Módulos de backend importados correctamente.")
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(
        f"ERROR CRITICO: No se pueden importar módulos del backend: {e}.",
        file=sys.stderr,
    )
    print(
        "Verifique: 1) Ejecutar desde raíz, 2) 'backend/__init__.py' existe, 3) No hay errores internos en backend/*.py.",
        file=sys.stderr,
    )

    # --- Mock Logic (Solo si el backend falla) ---
    class MockLogic:
        def __getattr__(self, name):
            def _mock_func(*args, **kwargs):
                print(f"ADVERTENCIA: Usando Mock para '{name}({args=}, {kwargs=})'.")
                mock_data = {
                    "CURSOS": {"Mock Curso": {"Mock Libro": "mock.pdf"}},
                    "verificar_login": lambda u, p: (u == "test" and p == "123") or (u == "felipe" and p == "1234"),
                    "generar_resumen_logica": lambda *a, **kw: {"status": "EXITO", "resumen": "Resumen Mock...", "puntos": "1. Punto Mock...", "message": "Generado con Mock"},
                    "generar_resumen_pdf_bytes": lambda *a, **kw: b"%PDF...",
                    "generar_nodos_localmente": lambda *a, **kw: {"status": "EXITO", "nodos": [{"titulo": "Nodo Central", "subnodos": ["Subnodo A", "Subnodo B"]}, {"titulo": "Otro Nodo"}]},
                    "generar_mermaid_code": lambda *a, **kw: ("graph TD A[Centro]-->B(Nodo 1);...", None),
                    "generar_visualizacion_html": lambda *a, **kw: "data:text/html,<html><body>Mock</body></html>",
                    "generar_evaluacion": lambda curso, libro, tema: {
                        "status": "EXITO",
                        "preguntas": [
                            {
                                "pregunta": f"Pregunta {i+1}: ¿Es esto correcto?",
                                "tipo": "verdadero_falso",
                                "opciones": [
                                    {"letra": "Verdadero", "texto": "Verdadero"},
                                    {"letra": "Falso", "texto": "Falso"}
                                ],
                                "respuesta_correcta": random.choice(["Verdadero", "Falso"]),
                                "explicacion": f"Respuesta para la pregunta {i+1}."
                            } if (i % 3 == 0) else {
                                "pregunta": f"Pregunta {i+1}: Selecciona la opción correcta.",
                                "tipo": "alternativas",
                                "opciones": [
                                    {"letra": "a", "texto": "Opción A"},
                                    {"letra": "b", "texto": "Opción B"},
                                    {"letra": "c", "texto": "Opción C"}
                                ],
                                "respuesta_correcta": random.choice(["a", "b", "c"]),
                                "explicacion": f"Respuesta para la pregunta {i+1}."
                            }
                            for i in range(15)  # Generar 15 preguntas
                        ]
                    },
                    "obtener_estadisticas_usuario": lambda *a, **kw: [{"curso": "Mock C", "libro": "Mock L", "tema": "Mock T", "puntuacion": 85.0, "fecha": "Hoy"}],
                    "guardar_resultado_evaluacion": lambda *a, **kw: print("Mock: Guardando resultado..."),
                }
                return (
                    mock_data.get(name, lambda *a, **kw: None)(*args, **kwargs)
                    if callable(mock_data.get(name))
                    else mock_data.get(name)
                )
            return _mock_func
    # --- Fin Mock Logic ---

    config_logic = login_logic = db_logic = resumen_logic = map_logic = eval_logic = MockLogic()
    print("ADVERTENCIA: Usando Mocks para la lógica del backend.", file=sys.stderr)
# --- FIN IMPORTACIONES ---

# --- UTILIDADES PARA VARIABLES REACTIVAS ---
def resolve_file_path(url_or_path):
    """
    Resuelve una URL o ruta de archivo a una ruta de sistema de archivos.
    
    Args:
        url_or_path: URL o ruta a resolver
        
    Returns:
        Tupla (ruta_resuelta, mensaje_error) donde ruta_resuelta es la ruta
        del sistema de archivos o None si no se pudo resolver, y mensaje_error
        es un mensaje explicativo de cualquier error encontrado.
    """
    import os
    
    if not url_or_path:
        return None, "Ruta vacía"
        
    # Eliminar cualquier parte de URL como '?query'
    clean_path = url_or_path.split('?')[0]
    
    # Casos a manejar:
    # 1. URLs externas (http/https) - No podemos acceder localmente
    if clean_path.startswith(('http://', 'https://')):
        return None, f"URL externa no accesible localmente: {clean_path}"
        
    # 2. Rutas absolutas del sistema de archivos
    if os.path.isabs(clean_path):
        if os.path.exists(clean_path):
            if os.path.isfile(clean_path):
                return clean_path, ""
            return None, f"La ruta existe pero no es un archivo: {clean_path}"
        return None, f"Ruta absoluta no encontrada: {clean_path}"
        
    # 3. URLs relativas (empiezan con /)
    if clean_path.startswith('/'):
        # Quitar la barra inicial para tratarla como ruta relativa
        rel_path = clean_path.lstrip('/')
        # Verificar si existe como ruta relativa desde el directorio actual
        if os.path.exists(rel_path):
            if os.path.isfile(rel_path):
                return rel_path, ""
            return None, f"La ruta relativa existe pero no es un archivo: {rel_path}"
            
        # Verificar si existe como ruta absoluta (considerando que el / inicial era parte de la ruta)
        # Esto es para sistemas Unix donde / es la raíz
        if os.path.exists(clean_path) and os.path.isfile(clean_path):
            return clean_path, ""
            
        return None, f"Ruta relativa no encontrada: {rel_path}"
        
    # 4. Rutas relativas (sin / inicial)
    if os.path.exists(clean_path):
        if os.path.isfile(clean_path):
            return clean_path, ""
        return None, f"La ruta existe pero no es un archivo: {clean_path}"
        
    return None, f"Archivo no encontrado: {clean_path}"

def get_safe_var_value(var, default=None):
    """
    Obtiene de manera segura el valor de una variable reactiva de Reflex.
    Convierte la variable reactiva a un valor Python estándar.
    
    Args:
        var: Variable reactiva de Reflex (rx.Var)
        default: Valor por defecto si no se puede obtener el valor
        
    Returns:
        El valor Python estándar de la variable reactiva, o default si no se puede obtener
    """
    if var is None:
        return default
        
    try:
        # Intentar obtener _var_value directamente (el valor subyacente)
        if hasattr(var, "_var_value"):
            return var._var_value
    except:
        pass
        
    try:
        # Intentar conversión con str()
        val = str(var)
        # Limpiar cualquier resto de Var en la representación de cadena
        if "<reflex.Var>" in val:
            val = val.split("</reflex.Var>")[-1]
        return val
    except:
        pass
        
    # Si todo falla, devolvemos el valor por defecto
    return default


def get_safe_var_list(var_list, default=None):
    """
    Obtiene de manera segura los valores de una lista reactiva de Reflex.
    Convierte la lista reactiva a una lista Python estándar.
    
    Args:
        var_list: Lista reactiva de Reflex
        default: Valor por defecto si no se puede obtener la lista ([] por defecto)
        
    Returns:
        Una lista Python estándar con los valores de la lista reactiva
    """
    if default is None:
        default = []
        
    if var_list is None:
        print("DEBUG: var_list es None, devolviendo lista por defecto")
        return default
        
    result = default
    error_found = False
    
    # Método 1: Acceder directamente a _var_value
    try:
        if hasattr(var_list, "_var_value"):
            val = var_list._var_value
            if isinstance(val, list):
                print(f"DEBUG: Lista obtenida via _var_value con {len(val)} elementos")
                return val
    except Exception as e:
        print(f"DEBUG: Error al acceder a _var_value: {e}")
        error_found = True
        
    # Método 2: Acceder a los elementos individuales, que luego podemos combinar en una lista
    try:
        # Intentamos acceder al primer elemento para ver si podemos iterar
        first_item = var_list[0]
        # Si llegamos aquí, podemos intentar construir la lista elemento por elemento
        items = []
        i = 0
        try:
            # Vamos accediendo a elementos hasta que falle
            while True:
                item = var_list[i]
                if hasattr(item, "_var_value"):
                    items.append(item._var_value)
                else:
                    items.append(item)
                i += 1
        except IndexError:
            # Llegamos al final de la lista
            pass
        except Exception as e:
            print(f"DEBUG: Error al iterar elemento {i}: {e}")
            
        if items:
            print(f"DEBUG: Lista construida elemento por elemento con {len(items)} elementos")
            return items
    except Exception as e:
        print(f"DEBUG: Error accediendo al primer elemento: {e}")
        error_found = True
        
    # Método 3: Intentar convertir a lista explícitamente
    try:
        val = list(var_list)
        if isinstance(val, list) and val:
            print(f"DEBUG: Lista obtenida via list() con {len(val)} elementos")
            return val
    except Exception as e:
        print(f"DEBUG: Error al convertir con list(): {e}")
        error_found = True
        
    # Método 4: Intentar obtener como dict y verificar si es una lista
    try:
        if hasattr(var_list, "to_dict"):
            val = var_list.to_dict()
            if isinstance(val, list):
                print(f"DEBUG: Lista obtenida via to_dict() con {len(val)} elementos")
                return val
    except Exception as e:
        print(f"DEBUG: Error al obtener via to_dict(): {e}")
        error_found = True
        
    # Método 5: Último recurso, evaluar la representación como string
    try:
        str_val = str(var_list)
        if str_val.startswith("[") and str_val.endswith("]"):
            import ast
            try:
                # Intentar interpretar como una lista literal de Python
                parsed_list = ast.literal_eval(str_val)
                if isinstance(parsed_list, list):
                    print(f"DEBUG: Lista obtenida via ast.literal_eval con {len(parsed_list)} elementos")
                    return parsed_list
            except:
                pass
    except Exception as e:
        print(f"DEBUG: Error evaluando string representation: {e}")
        error_found = True
    
    if error_found:
        print(f"DEBUG: No se pudo obtener la lista reactiva después de varios intentos, retornando {default}")
    
    # Si todo falla, devolvemos la lista vacía o el valor por defecto
    return default


# --- IMPORTACIONES DE SUB-ESTADOS ---
# Importar CuestionarioState para poder obtener su instancia
try:
    from .cuestionario import CuestionarioState
except ImportError:
    CuestionarioState = None # Handle case where file might not exist yet

# --- CONSTANTES ---
PRIMARY_COLOR_SCHEME = "blue"
ACCENT_COLOR_SCHEME = "amber"
FONT_FAMILY = "Poppins, sans-serif"
GOOGLE_FONT_STYLESHEET = [
    "https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap"
]
# --- FIN CONSTANTES ---


# --- FUNCIONES HELPER ---
def _curso_sort_key(curso: str) -> tuple:
    try:
        num_str = curso.split()[0]
        sufijos = ["ro", "do", "to", "vo", "mo"]
        for sufijo in sufijos:
            num_str = num_str.replace(sufijo, "")
        num = int(num_str) if num_str.isdigit() else 99
        nivel = "1" if "Básico" in curso else "2" if "Medio" in curso else "9"
        return (nivel, num)
    except Exception as e:
        print(f"Error en _curso_sort_key para '{curso}': {e}")
        return ("9", 99)

def error_callout(message: rx.Var[str]):
    """Componente UI para mostrar errores."""
    return rx.cond(
        message != "",
        rx.callout.root(
            rx.callout.icon(rx.icon("triangle-alert")),
            rx.callout.text(message),
            color_scheme="red",
            role="alert",
            w="100%",
            my="1em",
            size="2",
        ),
    )
# --- FIN FUNCIONES HELPER ---


# --- ESTADO CENTRAL: AppState ---
class AppState(rx.State):
    """Estado central de la aplicación SMART_STUDENT Web."""
    
    @classmethod
    def get_instance(cls):
        """Obtiene una instancia del estado principal para acceder desde subclases."""
        # Primero intentamos obtener la instancia principal (no subclase)
        for state in rx.State._get_current_app().state_manager._states.values():
            if type(state) == AppState:  # Solo coincidencia exacta, no subclases
                return state
        
        # Si no encontramos la instancia principal, buscamos cualquier instancia de AppState
        for state in rx.State._get_current_app().state_manager._states.values():
            if isinstance(state, AppState) and not isinstance(state, (CuestionarioState)):
                return state
        return None

    # Autenticación / Usuario
    username_input: str = ""
    password_input: str = ""
    is_logged_in: bool = False
    login_error_message: str = ""
    logged_in_username: str = ""
    
    # Language settings
    current_language: str = "es"  # Default language is Spanish
    
    def toggle_language(self):
        """Cambia entre español e inglés."""
        if self.current_language == "es":
            self.current_language = "en"
        else:
            self.current_language = "es"
    
    # Contadores de actividades
    resumenes_generados_count: int = 0  # Contador de resúmenes generados
    mapas_creados_count: int = 0  # Contador de mapas creados

    # Selección de Contenido
    try:
        _cursos_data = getattr(config_logic, "CURSOS", {})
        cursos_dict: Dict[str, Any] = _cursos_data if isinstance(_cursos_data, dict) else {}
        cursos_list: List[str] = sorted(
            [str(c) for c in cursos_dict.keys() if isinstance(c, str) and c != "Error"],
            key=_curso_sort_key,
        )
    except Exception as e:
        print(f"ERROR Cargando CURSOS al inicializar estado: {e}", file=sys.stderr)
        cursos_dict: Dict[str, Any] = {"Error": {"Carga": "error.pdf"}}
        cursos_list: List[str] = ["Error al Cargar Cursos"]

    selected_curso: str = ""
    selected_libro: str = ""
    selected_tema: str = ""

    # Estados Funcionalidades (Generales)
    is_generating_resumen: bool = False
    resumen_content: str = ""
    puntos_content: str = ""
    include_puntos: bool = False
    is_generating_mapa: bool = False
    mapa_mermaid_code: str = ""
    mapa_image_url: str = ""
    mapa_orientacion_horizontal: bool = True
    is_loading_stats: bool = False
    is_loading_profile_data: bool = False  # Added missing attribute
    stats_history: List[Dict[str, Any]] = []
    error_message_ui: str = ""
    active_tab: str = "inicio"
    
    # Paginación de historial de evaluaciones
    historial_evaluaciones_pagina_actual: int = 1
    historial_evaluaciones_por_pagina: int = 10
    
    # Estado para la pestaña de ayuda
    ayuda_search_query: str = ""
    show_contact_form: bool = False
    ayuda_pregunta_abierta: int = -1  # Índice de la pregunta abierta (-1 significa ninguna abierta)
    
    # Preguntas hardcodeadas para usar solo si algo falla con la carga dinámica
    _default_help_questions: List[Dict[str, str]] = []
    
    @rx.var
    def ayuda_preguntas_respuestas(self) -> List[Dict[str, str]]:
        """
        Devuelve las preguntas de ayuda en el idioma actual.
        Usa get_help_questions para obtener las traducciones adecuadas.
        """
        try:
            return get_help_questions(self.current_language)
        except Exception as e:
            print(f"ERROR: No se pudieron cargar las preguntas de ayuda: {e}")
            return self._default_help_questions

    # --- Computed Vars ---
    @rx.var
    def libros_para_curso(self) -> List[str]:
        if not self.selected_curso or self.selected_curso == "Error al Cargar Cursos":
            return []
        try:
            return list(self.cursos_dict.get(self.selected_curso, {}).keys())
        except Exception as e:
            print(f"Error obteniendo libros: {e}")
            return []

    @rx.var
    def pdf_url(self) -> str:
        if not self.selected_curso or not self.selected_libro:
            return ""
        try:
            curso = self.selected_curso.lower().replace(" ", "_")
            archivo = self.cursos_dict[self.selected_curso][self.selected_libro]
            return f"/pdfs/{curso}/{archivo}"
        except Exception as e:
            print(f"ERROR generando URL PDF: {e}")
            return ""
            
    @rx.var
    def user_stats(self) -> List[Dict[str, Any]]:
        """Obtiene las estadísticas del usuario para mostrar en la pestaña de perfil."""
        if not self.logged_in_username or not BACKEND_AVAILABLE:
            # Mock data para demostración cuando no hay backend o usuario
            return [
                {
                    "nombre": "Examen Final",
                    "curso": "Historia",
                    "libro": "Historia universal tomo 1",
                    "tema": "La Edad Media",
                    "puntuacion": 8.5,
                    "fecha": "15/04/2024"
                }
            ]
        
        try:
            if not hasattr(db_logic, "obtener_estadisticas_usuario"):
                print("WARN: No se encontró la función obtener_estadisticas_usuario")
                return []
                
            stats_raw = db_logic.obtener_estadisticas_usuario(self.logged_in_username)
            
            # Handle different return types
            if isinstance(stats_raw, list):
                stats = stats_raw
            elif isinstance(stats_raw, dict):
                print(f"INFO: Convirtiendo estadísticas de diccionario a lista: {stats_raw}")
                # If it's a dictionary with items, convert it to a list of one item
                if stats_raw:
                    stats = [stats_raw]
                else:
                    stats = []
            else:
                print(f"WARN: Las estadísticas obtenidas no son ni lista ni diccionario: {type(stats_raw)}")
                return []
                
            # Asegurarse de que cada ítem tenga todas las claves necesarias
            formatted_stats = []
            for stat in stats:
                if isinstance(stat, dict):
                    # Por defecto, usar 'Evaluación' como nombre si no está especificado
                    if "nombre" not in stat:
                        stat["nombre"] = "Examen Final"
                    formatted_stats.append(stat)
            
            return formatted_stats
        except Exception as e:
            print(f"ERROR obteniendo estadísticas: {e}")
            return []
            
    @rx.var
    def promedio_calificaciones(self) -> str:
        """Calcula el promedio de calificaciones del usuario para mostrar en la pestaña de perfil.
        Solo considera las materias con valores mayores a 0%."""
        
        # Obtener los progresos de cada materia
        progress_values = [
            self.matematicas_progress,
            self.ciencias_progress,
            self.historia_progress,
            self.lenguaje_progress
        ]
        
        # Filtrar valores mayores a 0
        valid_progress = [value for value in progress_values if value > 0]
        
        # Si no hay ningún valor válido, devolver 0.0
        if not valid_progress:
            return "0.0"
        
        # Calcular el promedio de los valores válidos
        promedio = sum(valid_progress) / len(valid_progress)
        return f"{promedio:.1f}"
    
    @rx.var
    def stats_count(self) -> int:
        """Devuelve el número de evaluaciones realizadas por el usuario."""
        if not self.stats_history:
            return 0
        return len(self.stats_history)
        
    @rx.var
    def contar_mapas_creados(self) -> int:
        """Cuenta el número de mapas conceptuales creados por el usuario actual."""
        if not self.logged_in_username or not BACKEND_AVAILABLE:
            return 0
            
        try:
            # Usamos el contador directo de mapas creados
            if hasattr(self, "mapas_creados_count") and isinstance(self.mapas_creados_count, int):
                return self.mapas_creados_count
            
            # Fallback al método anterior si el contador no está disponible
            # Verificar si la carpeta de mapas existe
            mapas_dir = os.path.join("assets", "mapas")
            if not os.path.exists(mapas_dir) or not os.path.isdir(mapas_dir):
                print("WARN: Directorio de mapas no encontrado")
                return 0
                
            # Contar archivos .mmd en la carpeta de mapas
            # Por simplicidad, contamos todos los mapas para el usuario actual
            # En una implementación más completa, habría que filtrar por usuario
            map_files = [f for f in os.listdir(mapas_dir) if f.endswith('.mmd')]
            return len(map_files)
        except Exception as e:
            print(f"ERROR contando mapas: {e}")
            return 0
            
    @rx.var
    def contar_resumenes_generados(self) -> int:
        """Cuenta el número de resúmenes generados por el usuario actual."""
        if not self.logged_in_username or not BACKEND_AVAILABLE:
            return 0
            
        try:
            # Usamos el contador directo de resúmenes generados
            if hasattr(self, "resumenes_generados_count") and isinstance(self.resumenes_generados_count, int):
                # Usamos el contador real más el valor base
                return self.resumenes_generados_count + 3  # +3 por resúmenes básicos iniciales
                
            # Fallback al método anterior si el contador no está disponible
            if self.stats_history and isinstance(self.stats_history, list):
                # Contamos cuántas evaluaciones diferentes por tema hay
                temas_unicos = set()
                for eval_item in self.stats_history:
                    if isinstance(eval_item, dict) and "tema" in eval_item:
                        temas_unicos.add(eval_item["tema"])
                
                # Asumimos que cada tema evaluado tiene un resumen generado
                return len(temas_unicos) + 3  # +3 por resúmenes básicos iniciales
            
            # Fallback si stats_history no está disponible
            # Usamos estadísticas básicas - aproximadamente la mitad + 3 básicos
            stats = db_logic.obtener_estadisticas_usuario(self.logged_in_username)
            if isinstance(stats, dict) and "total_evaluaciones" in stats:
                return max(3, stats["total_evaluaciones"] // 2 + 3)  # Estimación simple
            
            # Si todo falla, mostramos un valor razonable por defecto
            return 5
        except Exception as e:
            print(f"ERROR contando resúmenes: {e}")
            return 3
        
    @rx.var
    def historial_evaluaciones_paginado(self) -> List[Dict[str, Any]]:
        """Retorna una página del historial de evaluaciones para la vista de perfil."""
        if not self.stats_history:
            return []
            
        # Calcular índices de inicio y fin para la paginación
        inicio = (self.historial_evaluaciones_pagina_actual - 1) * self.historial_evaluaciones_por_pagina
        fin = inicio + self.historial_evaluaciones_por_pagina
        
        # Devolver la porción correspondiente a la página actual
        evaluaciones_pagina = self.stats_history[inicio:fin]
        
        # Asegurar que cada evaluación tenga todos los campos necesarios para la UI
        for evaluacion in evaluaciones_pagina:
            # Formatear la fecha para mostrar en hora local y formato amigable
            if "fecha" in evaluacion and evaluacion["fecha"]:
                try:
                    # Verificar si la fecha ya está en formato DD-MM-YYYY
                    fecha_str = evaluacion["fecha"]
                    if "-" in fecha_str and len(fecha_str.split("-")[0]) == 2:
                        # Ya está en formato local, no hacer nada
                        pass
                    else:
                        try:
                            # Convertir el string ISO a objeto datetime
                            fecha_dt = datetime.datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                            
                            # Ajustar la hora (-4 horas para Chile/Santiago)
                            fecha_local = fecha_dt - datetime.timedelta(hours=4)
                            
                            # Formatear para mostrar en formato militar (24 horas)
                            evaluacion["fecha"] = fecha_local.strftime("%d-%m-%Y %H:%M hrs")
                        except Exception as e:
                            print(f"Error al formatear fecha: {e}")
                            # Si hay un error, usar el formato original
                            evaluacion["fecha"] = fecha_str
                except Exception as e:
                    # Si hay un error, mantener el formato original
                    print(f"ERROR: No se pudo formatear la fecha {evaluacion.get('fecha')}: {e}")
                    
            # Intentar extraer información de respuestas correctas del metadatos
            if "metadata" in evaluacion and evaluacion["metadata"]:
                try:
                    metadata = evaluacion["metadata"]
                    print(f"DEBUG: Procesando metadata: '{metadata}'")
                    if "Correctas:" in metadata:
                        # Formato esperado: "Correctas: X/Y"
                        correctas_part = metadata.split("Correctas:")[1].strip()
                        if "/" in correctas_part:
                            correctas, total = correctas_part.split("/")
                            evaluacion["respuestas_correctas"] = int(correctas)
                            evaluacion["total_preguntas"] = int(total)
                            print(f"DEBUG: Extraídas respuestas_correctas={correctas}/{total} de metadata")
                except Exception as e:
                    print(f"ERROR: No se pudo extraer metadata {evaluacion.get('metadata')}: {e}")
            
            # Asegurarse que tenemos campos consistentes (algunos pueden venir como calificacion, otros como nota)
            if "calificacion" not in evaluacion and "puntuacion" in evaluacion:
                try:
                    # Garantizar que la puntuación esté en el rango 0-100%
                    puntuacion = float(evaluacion["puntuacion"])
                    evaluacion["calificacion"] = max(0, min(100, round(puntuacion)))
                except (ValueError, TypeError):
                    evaluacion["calificacion"] = 0
            elif "calificacion" not in evaluacion and "nota" in evaluacion:
                try:
                    # Convertir nota del sistema 1.0-7.0 de vuelta a porcentaje 0-100%
                    nota = float(evaluacion["nota"])
                    if nota <= 1.0:  # Si la nota es menor o igual a 1.0, sabemos que es 0%
                        evaluacion["calificacion"] = 0
                    else:
                        # Aplicar fórmula inversa: porcentaje = (nota - 1.0) / 6.0 * 100
                        porcentaje = int((nota * 100) / 7.0)
                        # Garantizar que el porcentaje esté en el rango 0-100%
                        evaluacion["calificacion"] = max(0, min(100, porcentaje))
                        print(f"DEBUG: Convertida nota {nota} a porcentaje {porcentaje}%")
                except (ValueError, TypeError) as e:
                    print(f"ERROR: No se pudo convertir nota {evaluacion.get('nota')}: {e}")
                    evaluacion["calificacion"] = 0
            elif "calificacion" not in evaluacion:
                evaluacion["calificacion"] = 0
                
            # Asegurarse que calificación sea un número válido entre 0-100
            try:
                if "calificacion" in evaluacion:
                    evaluacion["calificacion"] = max(0, min(100, round(float(evaluacion["calificacion"]))))
                    
                    # Si tiene respuestas_correctas en 0, entonces la calificación debe ser 0%
                    if "respuestas_correctas" in evaluacion and evaluacion["respuestas_correctas"] == 0 and evaluacion["total_preguntas"] > 0:
                        evaluacion["calificacion"] = 0
                        
                # Recalcular porcentaje de calificación si tenemos respuestas_correctas y total_preguntas
                if ("respuestas_correctas" in evaluacion and 
                    "total_preguntas" in evaluacion and 
                    evaluacion["total_preguntas"] > 0):
                    # Calcular correctamente el porcentaje como (correctas / total) * 100
                    porcentaje_correcto = round((evaluacion["respuestas_correctas"] / evaluacion["total_preguntas"]) * 100)
                    # Actualizar la calificación con el porcentaje correcto
                    evaluacion["calificacion"] = porcentaje_correcto
                    print(f"DEBUG: Recalculado porcentaje: {evaluacion['respuestas_correctas']}/{evaluacion['total_preguntas']} = {porcentaje_correcto}%")
                        
                # Asegurar formato de puntuación para mostrar en UI (Ej: 95 -> "95%")
                if "puntuacion" in evaluacion and isinstance(evaluacion["puntuacion"], (int, float)):
                    # Si la puntuación no tiene el símbolo %, añadirlo
                    if not str(evaluacion["puntuacion"]).endswith('%'):
                        evaluacion["puntuacion_display"] = f"{evaluacion['puntuacion']}%"
                    else:
                        evaluacion["puntuacion_display"] = str(evaluacion["puntuacion"])
                elif "calificacion" in evaluacion:
                    evaluacion["puntuacion_display"] = f"{evaluacion['calificacion']}%"
                else:
                    evaluacion["puntuacion_display"] = "0%"
                    
                # Manejar el caso de "0/0" puntos
                if "respuestas_correctas" in evaluacion and "total_preguntas" in evaluacion:
                    # Solo ajustar si tenemos una puntuación válida pero no hay preguntas registradas
                    if evaluacion["total_preguntas"] == 0 and evaluacion.get("calificacion", 0) > 0:
                        # Estimamos el número total de preguntas basado en el porcentaje
                        # Asumimos un estándar de 10 preguntas para evaluaciones sin datos detallados
                        evaluacion["total_preguntas"] = 10
                        # Calculamos respuestas correctas basado en la calificación
                        evaluacion["respuestas_correctas"] = round(evaluacion["total_preguntas"] * evaluacion["calificacion"] / 100)
            except (ValueError, TypeError):
                evaluacion["calificacion"] = 0
                evaluacion["puntuacion_display"] = "0%"
                
            # Asegurar que tenemos conteo de respuestas para mostrar en UI
            if "respuestas_correctas" not in evaluacion:
                evaluacion["respuestas_correctas"] = 0
            if "total_preguntas" not in evaluacion:
                evaluacion["total_preguntas"] = 0
                
        return evaluaciones_pagina

    # --- Book Progress Variables ---
    @rx.var
    def matematicas_progress(self) -> int:
        """Retorna el progreso (porcentaje) más alto obtenido en evaluaciones de Matemáticas."""
        if not self.stats_history:
            # Si no hay historial, mostramos 0%
            return 0
        
        # Buscar evaluaciones relacionadas con matemáticas
        matematicas_evaluaciones = []
        for eval_item in self.stats_history:
            if not isinstance(eval_item, dict):
                continue
                
            # Verificar si es una evaluación de matemáticas por el nombre del libro/curso
            is_matematicas = False
            
            # Verificar en el libro
            libro = eval_item.get("libro", "").lower() if isinstance(eval_item.get("libro", ""), str) else ""
            if libro and any(term in libro for term in ["mat", "matemática", "álgebra", "geometría", "aritmética", "cálculo"]):
                is_matematicas = True
                
            # Verificar en el curso si aún no se ha detectado
            if not is_matematicas:
                curso = eval_item.get("curso", "").lower() if isinstance(eval_item.get("curso", ""), str) else ""
                if curso and any(term in curso for term in ["mat", "matemática", "álgebra"]):
                    is_matematicas = True
                    
            # Verificar en el tema si aún no se ha detectado
            if not is_matematicas:
                tema = eval_item.get("tema", "").lower() if isinstance(eval_item.get("tema", ""), str) else ""
                if tema and any(term in tema for term in ["mat", "matemática", "álgebra", "geometría", "aritmética", "número", "ecuación", "función", "cálculo", "trigonometría"]):
                    is_matematicas = True
            
            if is_matematicas:
                matematicas_evaluaciones.append(eval_item)
                print(f"DEBUG: Evaluación de matemáticas encontrada: {eval_item.get('tema')} - {eval_item.get('calificacion')}%")
        
        if not matematicas_evaluaciones:
            # Si no hay evaluaciones específicas de matemáticas, retornar 0%
            return 0
            
        # Extraer las calificaciones
        calificaciones = []
        for eval_item in matematicas_evaluaciones:
            # Primero intentamos usar la calificación calculada
            if "calificacion" in eval_item:
                try:
                    calificacion = float(eval_item["calificacion"])
                    calificaciones.append(calificacion)
                    print(f"DEBUG: Añadida calificación: {calificacion}%")
                except (ValueError, TypeError):
                    pass
            # Si no hay calificación, intentamos con puntuacion
            elif "puntuacion" in eval_item:
                try:
                    puntuacion_str = str(eval_item["puntuacion"])
                    # Eliminar el símbolo % si existe
                    puntuacion_str = puntuacion_str.replace("%", "").strip()
                    puntuacion = float(puntuacion_str)
                    calificaciones.append(puntuacion)
                    print(f"DEBUG: Añadida puntuación: {puntuacion}%")
                except (ValueError, TypeError):
                    pass
            # Si hay nota en escala 1-7, convertirla a porcentaje
            elif "nota" in eval_item:
                try:
                    nota = float(eval_item["nota"])
                    # Verificar si la nota está en escala 1.0-7.0 (sistema chileno)
                    if 1.0 <= nota <= 7.0:
                        # Convertir a porcentaje (1.0 = 0%, 7.0 = 100%)
                        porcentaje = ((nota - 1.0) / 6.0) * 100
                        calificaciones.append(porcentaje)
                        print(f"DEBUG: Añadida nota convertida: {nota} -> {porcentaje}%")
                    else:
                        # Asumir que ya es un porcentaje
                        calificaciones.append(nota)
                        print(f"DEBUG: Añadida nota como porcentaje: {nota}%")
                except (ValueError, TypeError):
                    pass
            # O intentamos recalcular a partir de respuestas correctas
            elif "respuestas_correctas" in eval_item and "total_preguntas" in eval_item and eval_item["total_preguntas"] > 0:
                try:
                    correctas = int(eval_item["respuestas_correctas"])
                    total = int(eval_item["total_preguntas"])
                    porcentaje = round((correctas / total) * 100)
                    calificaciones.append(porcentaje)
                    print(f"DEBUG: Añadida calificación calculada: {correctas}/{total} = {porcentaje}%")
                except (ValueError, TypeError, ZeroDivisionError):
                    pass
            # Si hay metadata con información de respuestas correctas
            elif "metadata" in eval_item and eval_item["metadata"]:
                try:
                    metadata = eval_item["metadata"]
                    if "Correctas:" in metadata:
                        # Formato esperado: "Correctas: X/Y"
                        correctas_part = metadata.split("Correctas:")[1].strip()
                        if "/" in correctas_part:
                            correctas, total = correctas_part.split("/")
                            correctas = int(correctas)
                            total = int(total)
                            if total > 0:
                                porcentaje = (correctas / total) * 100
                                calificaciones.append(porcentaje)
                                print(f"DEBUG: Añadida calificación desde metadata: {correctas}/{total} = {porcentaje}%")
                except Exception:
                    pass
        
        # Si no pudimos extraer ninguna calificación, retornar 0%
        if not calificaciones:
            return 0
                
        # Devolver la calificación más alta
        mejor_calificacion = max(calificaciones)
        print(f"DEBUG: Mejor calificación: {mejor_calificacion}%")
        return round(mejor_calificacion)
        
    @rx.var
    def ciencias_progress(self) -> int:
        """Retorna el progreso (porcentaje) más alto obtenido en evaluaciones de Ciencias."""
        if not self.stats_history:
            # Si no hay historial, mostramos 0%
            return 0
        
        # Buscar evaluaciones relacionadas con ciencias
        ciencias_evaluaciones = []
        for eval_item in self.stats_history:
            if not isinstance(eval_item, dict):
                continue
                
            # Verificar si es una evaluación de ciencias por el nombre del libro/curso/tema
            is_ciencias = False
            
            # Verificar en el libro
            libro = eval_item.get("libro", "").lower() if isinstance(eval_item.get("libro", ""), str) else ""
            if libro and any(term in libro for term in ["cien", "biología", "biolog", "química", "quimic", "física", "fisic", "natural", "ecología", "ecolog", "ambiente"]):
                is_ciencias = True
                
            # Verificar en el curso si aún no se ha detectado
            if not is_ciencias:
                curso = eval_item.get("curso", "").lower() if isinstance(eval_item.get("curso", ""), str) else ""
                if curso and any(term in curso for term in ["cien", "biología", "biolog", "química", "quimic", "física", "fisic", "natural"]):
                    is_ciencias = True
                    
            # Verificar en el tema si aún no se ha detectado
            if not is_ciencias:
                tema = eval_item.get("tema", "").lower() if isinstance(eval_item.get("tema", ""), str) else ""
                if tema and any(term in tema for term in ["cien", "célula", "celula", "biolog", "quimic", "fisic", "natural", "quánt", "átomo", "atomo", "molécula", "molecula", "genética", "tejido", "fuerza", "energía", "planeta", "sistema", "fotosíntesis", "fotosintesis"]):
                    is_ciencias = True
            
            if is_ciencias:
                ciencias_evaluaciones.append(eval_item)
                print(f"DEBUG: Evaluación de ciencias encontrada: {eval_item.get('tema')} - {eval_item.get('calificacion')}%")
        
        if not ciencias_evaluaciones:
            # Si no hay evaluaciones específicas de ciencias, retornar 0%
            return 0
            
        # Extraer las calificaciones
        calificaciones = []
        for eval_item in ciencias_evaluaciones:
            # Primero intentamos usar la calificación calculada
            if "calificacion" in eval_item:
                try:
                    calificacion = float(eval_item["calificacion"])
                    calificaciones.append(calificacion)
                    print(f"DEBUG: Añadida calificación: {calificacion}%")
                except (ValueError, TypeError):
                    pass
            # Si no hay calificación, intentamos con puntuacion
            elif "puntuacion" in eval_item:
                try:
                    puntuacion_str = str(eval_item["puntuacion"])
                    # Eliminar el símbolo % si existe
                    puntuacion_str = puntuacion_str.replace("%", "").strip()
                    puntuacion = float(puntuacion_str)
                    calificaciones.append(puntuacion)
                    print(f"DEBUG: Añadida puntuación: {puntuacion}%")
                except (ValueError, TypeError):
                    pass
            # Si hay nota en escala 1-7, convertirla a porcentaje
            elif "nota" in eval_item:
                try:
                    nota = float(eval_item["nota"])
                    # Verificar si la nota está en escala 1.0-7.0 (sistema chileno)
                    if 1.0 <= nota <= 7.0:
                        # Convertir a porcentaje (1.0 = 0%, 7.0 = 100%)
                        porcentaje = ((nota - 1.0) / 6.0) * 100
                        calificaciones.append(porcentaje)
                        print(f"DEBUG: Añadida nota convertida: {nota} -> {porcentaje}%")
                    else:
                        # Asumir que ya es un porcentaje
                        calificaciones.append(nota)
                        print(f"DEBUG: Añadida nota como porcentaje: {nota}%")
                except (ValueError, TypeError):
                    pass
            # O intentamos recalcular a partir de respuestas correctas
            elif "respuestas_correctas" in eval_item and "total_preguntas" in eval_item and eval_item["total_preguntas"] > 0:
                try:
                    correctas = int(eval_item["respuestas_correctas"])
                    total = int(eval_item["total_preguntas"])
                    porcentaje = round((correctas / total) * 100)
                    calificaciones.append(porcentaje)
                    print(f"DEBUG: Añadida calificación calculada: {correctas}/{total} = {porcentaje}%")
                except (ValueError, TypeError, ZeroDivisionError):
                    pass
            # Si hay metadata con información de respuestas correctas
            elif "metadata" in eval_item and eval_item["metadata"]:
                try:
                    metadata = eval_item["metadata"]
                    if "Correctas:" in metadata:
                        # Formato esperado: "Correctas: X/Y"
                        correctas_part = metadata.split("Correctas:")[1].strip()
                        if "/" in correctas_part:
                            correctas, total = correctas_part.split("/")
                            correctas = int(correctas)
                            total = int(total)
                            if total > 0:
                                porcentaje = (correctas / total) * 100
                                calificaciones.append(porcentaje)
                                print(f"DEBUG: Añadida calificación desde metadata: {correctas}/{total} = {porcentaje}%")
                except Exception:
                    pass
        
        # Si no pudimos extraer ninguna calificación, retornar 0%
        if not calificaciones:
            return 0
                
        # Devolver la calificación más alta
        mejor_calificacion = max(calificaciones)
        print(f"DEBUG: Mejor calificación en ciencias: {mejor_calificacion}%")
        return round(mejor_calificacion)

    @rx.var
    def historia_progress(self) -> int:
        """Retorna el progreso (porcentaje) más alto obtenido en evaluaciones de Historia."""
        if not self.stats_history:
            # Si no hay historial, mostramos 0%
            return 0
        
        # Buscar evaluaciones relacionadas con historia
        historia_evaluaciones = []
        for eval_item in self.stats_history:
            if not isinstance(eval_item, dict):
                continue
                
            # Verificar si es una evaluación de historia por el nombre del libro/curso/tema
            is_historia = False
            
            # Verificar en el libro
            libro = eval_item.get("libro", "").lower() if isinstance(eval_item.get("libro", ""), str) else ""
            if libro and any(term in libro for term in ["hist", "geograf", "social", "civiliz", "mundo", "socied", "cultura"]):
                is_historia = True
                
            # Verificar en el curso si aún no se ha detectado
            if not is_historia:
                curso = eval_item.get("curso", "").lower() if isinstance(eval_item.get("curso", ""), str) else ""
                if curso and any(term in curso for term in ["hist", "geograf", "social", "socied"]):
                    is_historia = True
                    
            # Verificar en el tema si aún no se ha detectado
            if not is_historia:
                tema = eval_item.get("tema", "").lower() if isinstance(eval_item.get("tema", ""), str) else ""
                if tema and any(term in tema for term in ["hist", "geograf", "social", "cultur", "edad media", "siglo", "guerra", "revoluci", "civiliz", "imperio", "antiguo", "politica", "polític", "gobierno", "democracia", "independencia"]):
                    is_historia = True
            
            if is_historia:
                historia_evaluaciones.append(eval_item)
                print(f"DEBUG: Evaluación de historia encontrada: {eval_item.get('tema')} - {eval_item.get('calificacion')}%")
        
        if not historia_evaluaciones:
            # Si no hay evaluaciones específicas de historia, retornar 0%
            return 0
            
        # Extraer las calificaciones
        calificaciones = []
        for eval_item in historia_evaluaciones:
            # Primero intentamos usar la calificación calculada
            if "calificacion" in eval_item:
                try:
                    calificacion = float(eval_item["calificacion"])
                    calificaciones.append(calificacion)
                    print(f"DEBUG: Añadida calificación: {calificacion}%")
                except (ValueError, TypeError):
                    pass
            # Si no hay calificación, intentamos con puntuacion
            elif "puntuacion" in eval_item:
                try:
                    puntuacion_str = str(eval_item["puntuacion"])
                    # Eliminar el símbolo % si existe
                    puntuacion_str = puntuacion_str.replace("%", "").strip()
                    puntuacion = float(puntuacion_str)
                    calificaciones.append(puntuacion)
                    print(f"DEBUG: Añadida puntuación: {puntuacion}%")
                except (ValueError, TypeError):
                    pass
            # Si hay nota en escala 1-7, convertirla a porcentaje
            elif "nota" in eval_item:
                try:
                    nota = float(eval_item["nota"])
                    # Verificar si la nota está en escala 1.0-7.0 (sistema chileno)
                    if 1.0 <= nota <= 7.0:
                        # Convertir a porcentaje (1.0 = 0%, 7.0 = 100%)
                        porcentaje = ((nota - 1.0) / 6.0) * 100
                        calificaciones.append(porcentaje)
                        print(f"DEBUG: Añadida nota convertida: {nota} -> {porcentaje}%")
                    else:
                        # Asumir que ya es un porcentaje
                        calificaciones.append(nota)
                        print(f"DEBUG: Añadida nota como porcentaje: {nota}%")
                except (ValueError, TypeError):
                    pass
            # O intentamos recalcular a partir de respuestas correctas
            elif "respuestas_correctas" in eval_item and "total_preguntas" in eval_item and eval_item["total_preguntas"] > 0:
                try:
                    correctas = int(eval_item["respuestas_correctas"])
                    total = int(eval_item["total_preguntas"])
                    porcentaje = round((correctas / total) * 100)
                    calificaciones.append(porcentaje)
                    print(f"DEBUG: Añadida calificación calculada: {correctas}/{total} = {porcentaje}%")
                except (ValueError, TypeError, ZeroDivisionError):
                    pass
            # Si hay metadata con información de respuestas correctas
            elif "metadata" in eval_item and eval_item["metadata"]:
                try:
                    metadata = eval_item["metadata"]
                    if "Correctas:" in metadata:
                        # Formato esperado: "Correctas: X/Y"
                        correctas_part = metadata.split("Correctas:")[1].strip()
                        if "/" in correctas_part:
                            correctas, total = correctas_part.split("/")
                            correctas = int(correctas)
                            total = int(total)
                            if total > 0:
                                porcentaje = (correctas / total) * 100
                                calificaciones.append(porcentaje)
                                print(f"DEBUG: Añadida calificación desde metadata: {correctas}/{total} = {porcentaje}%")
                except Exception:
                    pass
        
        # Si no pudimos extraer ninguna calificación, retornar 0%
        if not calificaciones:
            return 0
                
        # Devolver la calificación más alta
        mejor_calificacion = max(calificaciones)
        print(f"DEBUG: Mejor calificación en historia: {mejor_calificacion}%")
        return round(mejor_calificacion)
        
    @rx.var
    def lenguaje_progress(self) -> int:
        """Retorna el progreso (porcentaje) más alto obtenido en evaluaciones de Lenguaje."""
        if not self.stats_history:
            # Si no hay historial, mostramos 0%
            return 0
        
        # Buscar evaluaciones relacionadas con lenguaje
        lenguaje_evaluaciones = []
        for eval_item in self.stats_history:
            if not isinstance(eval_item, dict):
                continue
                
            # Verificar si es una evaluación de lenguaje por el nombre del libro/curso/tema
            is_lenguaje = False
            
            # Verificar en el libro
            libro = eval_item.get("libro", "").lower() if isinstance(eval_item.get("libro", ""), str) else ""
            if libro and any(term in libro for term in ["lengu", "gram", "liter", "comunic", "español", "castellano", "lectura", "redacción"]):
                is_lenguaje = True
                
            # Verificar en el curso si aún no se ha detectado
            if not is_lenguaje:
                curso = eval_item.get("curso", "").lower() if isinstance(eval_item.get("curso", ""), str) else ""
                if curso and any(term in curso for term in ["lengu", "gram", "liter", "comunic", "español", "castellano"]):
                    is_lenguaje = True
                    
            # Verificar en el tema si aún no se ha detectado
            if not is_lenguaje:
                tema = eval_item.get("tema", "").lower() if isinstance(eval_item.get("tema", ""), str) else ""
                if tema and any(term in tema for term in ["lengu", "gram", "liter", "comunic", "texto", "narrativ", "poesía", "poesia", "ensayo", "novela", "cuento", "escrit", "verbal", "habla", "lectura", "ortografía", "ortografia", "redacción", "redaccion", "autor", "obra"]):
                    is_lenguaje = True
            
            if is_lenguaje:
                lenguaje_evaluaciones.append(eval_item)
                print(f"DEBUG: Evaluación de lenguaje encontrada: {eval_item.get('tema')} - {eval_item.get('calificacion')}%")
        
        if not lenguaje_evaluaciones:
            # Si no hay evaluaciones específicas de lenguaje, retornar 0%
            return 0
            
        # Extraer las calificaciones
        calificaciones = []
        for eval_item in lenguaje_evaluaciones:
            # Primero intentamos usar la calificación calculada
            if "calificacion" in eval_item:
                try:
                    calificacion = float(eval_item["calificacion"])
                    calificaciones.append(calificacion)
                    print(f"DEBUG: Añadida calificación: {calificacion}%")
                except (ValueError, TypeError):
                    pass
            # Si no hay calificación, intentamos con puntuacion
            elif "puntuacion" in eval_item:
                try:
                    puntuacion_str = str(eval_item["puntuacion"])
                    # Eliminar el símbolo % si existe
                    puntuacion_str = puntuacion_str.replace("%", "").strip()
                    puntuacion = float(puntuacion_str)
                    calificaciones.append(puntuacion)
                    print(f"DEBUG: Añadida puntuación: {puntuacion}%")
                except (ValueError, TypeError):
                    pass
            # Si hay nota en escala 1-7, convertirla a porcentaje
            elif "nota" in eval_item:
                try:
                    nota = float(eval_item["nota"])
                    # Verificar si la nota está en escala 1.0-7.0 (sistema chileno)
                    if 1.0 <= nota <= 7.0:
                        # Convertir a porcentaje (1.0 = 0%, 7.0 = 100%)
                        porcentaje = ((nota - 1.0) / 6.0) * 100
                        calificaciones.append(porcentaje)
                        print(f"DEBUG: Añadida nota convertida: {nota} -> {porcentaje}%")
                    else:
                        # Asumir que ya es un porcentaje
                        calificaciones.append(nota)
                        print(f"DEBUG: Añadida nota como porcentaje: {nota}%")
                except (ValueError, TypeError):
                    pass
            # O intentamos recalcular a partir de respuestas correctas
            elif "respuestas_correctas" in eval_item and "total_preguntas" in eval_item and eval_item["total_preguntas"] > 0:
                try:
                    correctas = int(eval_item["respuestas_correctas"])
                    total = int(eval_item["total_preguntas"])
                    porcentaje = round((correctas / total) * 100)
                    calificaciones.append(porcentaje)
                    print(f"DEBUG: Añadida calificación calculada: {correctas}/{total} = {porcentaje}%")
                except (ValueError, TypeError, ZeroDivisionError):
                    pass
            # Si hay metadata con información de respuestas correctas
            elif "metadata" in eval_item and eval_item["metadata"]:
                try:
                    metadata = eval_item["metadata"]
                    if "Correctas:" in metadata:
                        # Formato esperado: "Correctas: X/Y"
                        correctas_part = metadata.split("Correctas:")[1].strip()
                        if "/" in correctas_part:
                            correctas, total = correctas_part.split("/")
                            correctas = int(correctas)
                            total = int(total)
                            if total > 0:
                                porcentaje = (correctas / total) * 100
                                calificaciones.append(porcentaje)
                                print(f"DEBUG: Añadida calificación desde metadata: {correctas}/{total} = {porcentaje}%")
                except Exception:
                    pass
        
        # Si no pudimos extraer ninguna calificación, retornar 0%
        if not calificaciones:
            return 0
                
        # Devolver la calificación más alta
        mejor_calificacion = max(calificaciones)
        print(f"DEBUG: Mejor calificación en lenguaje: {mejor_calificacion}%")
        return round(mejor_calificacion)
    # --- Fin Computed Vars ---

    # --- Event Handlers ---
    async def set_active_tab(self, tab: str):
        if not isinstance(tab, str):
            return
        print(f"DEBUG: Navegando a tab '{tab}'. Selección actual: Curso='{self.selected_curso}', Libro='{self.selected_libro}', Tema='{self.selected_tema}'")

        tab_anterior = self.active_tab

        # Si cambiamos a la pestaña de perfil, cargar las estadísticas
        if tab == "perfil":
            print("DEBUG: Cambiando a pestaña de perfil, cargando estadísticas...")
            async for _ in self.load_stats():
                pass
        
        if tab != tab_anterior:
            print(f"DEBUG: Cambiando de pestaña {tab_anterior} a {tab}, limpiando campos generales...")

            # Reiniciar la selección de curso, libro y tema (general)
            self.selected_curso = ""
            self.selected_libro = ""
            self.selected_tema = ""

            # Limpiar contenido de resultados generales
            self.error_message_ui = ""
            self.resumen_content = ""
            self.puntos_content = ""
            self.include_puntos = False
            self.mapa_image_url = ""
            self.mapa_mermaid_code = ""
            self.is_generating_resumen = False
            self.is_generating_mapa = False

            # Limpiar estado específico de evaluaciones - evitamos circular imports
            if tab_anterior == "evaluacion":
                try:
                    print("DEBUG: Reseteando estado de evaluación...")
                    # Resetear variables específicas de evaluación sin importar el módulo
                    # Esto se manejará directamente cuando se importe EvaluationState
                    pass
                except Exception as e:
                    print(f"DEBUG: No se pudo resetear estado de evaluación: {e}")
                    pass

            # Limpiar estado específico de cuestionarios si venimos de esa pestaña
            if tab_anterior == "cuestionario" and CuestionarioState:
                print("DEBUG: Reseteando estado de Cuestionario via get_state...")
                try:
                    cuestionario_substate = await self.get_state(CuestionarioState)
                    if cuestionario_substate and hasattr(cuestionario_substate, "reset_cuestionario"):
                        print("DEBUG: Llamando a CuestionarioState.reset_cuestionario() en la instancia...")
                        async for _ in cuestionario_substate.reset_cuestionario():
                            pass
                    else:
                        print("WARN: No se pudo obtener la instancia de CuestionarioState o el método reset_cuestionario.")
                except Exception as e:
                    print(f"ERROR: Excepción al intentar resetear CuestionarioState via get_state: {e}")
                    traceback.print_exc()

        # Establecer la nueva pestaña activa
        self.active_tab = tab

        # Cargar estadísticas si vamos a la pestaña de perfil
        if tab == "perfil":
            async for _ in self.load_stats():
                pass
        else:
            yield

    def toggle_pregunta(self, index: int):
        """Abre o cierra una pregunta de la pestaña de ayuda."""
        if self.ayuda_pregunta_abierta == index:
            # Si la pregunta ya está abierta, la cerramos
            self.ayuda_pregunta_abierta = -1
        else:
            # Si la pregunta está cerrada, la abrimos
            self.ayuda_pregunta_abierta = index
        yield

    def go_to_curso_and_resumen(self, curso: str):
        if not isinstance(curso, str) or not curso:
            return
        self.selected_curso = curso
        self.selected_libro = ""
        self.selected_tema = ""
        self.resumen_content = ""
        self.puntos_content = ""
        self.mapa_mermaid_code = ""
        self.mapa_image_url = ""
        self.error_message_ui = ""
        self.active_tab = "resumen"
        yield

    def go_to_resumen_tab(self):
        self.error_message_ui = ""
        self.resumen_content = ""
        self.puntos_content = ""
        yield

    def go_to_mapa_tab(self):
        self.error_message_ui = ""
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        yield

    def go_to_evaluacion_tab(self):
        self.error_message_ui = ""

    def handle_login(self):
        self.login_error_message = ""
        self.error_message_ui = ""
        if not self.username_input or not self.password_input:
            self.login_error_message = "Ingresa usuario y contraseña."
            return
        if (self.username_input == "felipe" and self.password_input == "1234") or \
           (self.username_input == "test" and self.password_input == "123"):
            self.is_logged_in = True
            self.logged_in_username = self.username_input
            self.username_input = self.password_input = ""
            self.active_tab = "inicio"
            
            # Cargar estadísticas del usuario desde la BD
            if BACKEND_AVAILABLE and hasattr(db_logic, "get_user_stats") and hasattr(db_logic, "update_user_login"):
                try:
                    # Actualizar fecha de último login
                    db_logic.update_user_login(self.logged_in_username)
                    
                    # Recuperar contadores del usuario
                    user_stats = db_logic.get_user_stats(self.logged_in_username)
                    if user_stats:
                        self.resumenes_generados_count = user_stats.get("resumenes_count", 0)
                        self.mapas_creados_count = user_stats.get("mapas_count", 0)
                        print(f"DEBUG: Contadores cargados de BD: Resúmenes={self.resumenes_generados_count}, Mapas={self.mapas_creados_count}")
                    else:
                        # Si no hay estadísticas, inicializar a 0
                        self.resumenes_generados_count = 0
                        self.mapas_creados_count = 0
                except Exception as e:
                    print(f"ERROR: No se pudieron cargar estadísticas del usuario: {e}")
                    self.resumenes_generados_count = 0
                    self.mapas_creados_count = 0
            else:
                # Si no está disponible el backend, inicializar a 0
                self.resumenes_generados_count = 0
                self.mapas_creados_count = 0
            
            return
        if not BACKEND_AVAILABLE:
            self.login_error_message = "Servicio no disponible. Cuentas prueba: felipe/1234, test/123."
            return
        if not hasattr(login_logic, "verificar_login") or not callable(login_logic.verificar_login):
            self.login_error_message = "Error servicio autenticación."
            return
        try:
            is_valid = login_logic.verificar_login(self.username_input, self.password_input)
            if is_valid:
                self.is_logged_in = True
                self.logged_in_username = self.username_input
                self.username_input = self.password_input = ""
                self.active_tab = "inicio"
                
                # Cargar estadísticas del usuario desde la BD
                if BACKEND_AVAILABLE and hasattr(db_logic, "get_user_stats") and hasattr(db_logic, "update_user_login"):
                    try:
                        # Actualizar fecha de último login
                        db_logic.update_user_login(self.logged_in_username)
                        
                        # Recuperar contadores del usuario
                        user_stats = db_logic.get_user_stats(self.logged_in_username)
                        if user_stats:
                            self.resumenes_generados_count = user_stats.get("resumenes_count", 0)
                            self.mapas_creados_count = user_stats.get("mapas_count", 0)
                            print(f"DEBUG: Contadores cargados de BD: Resúmenes={self.resumenes_generados_count}, Mapas={self.mapas_creados_count}")
                        else:
                            # Si no hay estadísticas, inicializar a 0
                            self.resumenes_generados_count = 0
                            self.mapas_creados_count = 0
                    except Exception as e:
                        print(f"ERROR: No se pudieron cargar estadísticas del usuario: {e}")
                        self.resumenes_generados_count = 0
                        self.mapas_creados_count = 0
                else:
                    # Si no está disponible el backend, inicializar a 0
                    self.resumenes_generados_count = 0
                    self.mapas_creados_count = 0
            else:
                self.login_error_message = "Usuario o contraseña incorrectos."
                self.password_input = ""
        except Exception as e:
            print(f"Error login: {e}")
            self.login_error_message = "Error servicio autenticación. Intenta más tarde."
            self.password_input = ""

    def logout(self):
        """Cierra la sesión del usuario actual."""
        # Guardar estadísticas del usuario en la BD antes de cerrar sesión
        if self.is_logged_in and self.logged_in_username and BACKEND_AVAILABLE and hasattr(db_logic, "update_user_stats"):
            try:
                # Persistir los contadores en la base de datos antes de cerrar sesión
                db_logic.update_user_stats(
                    self.logged_in_username, 
                    resumenes_count=self.resumenes_generados_count, 
                    mapas_count=self.mapas_creados_count
                )
                print(f"INFO: Contadores guardados al cerrar sesión: Resúmenes={self.resumenes_generados_count}, Mapas={self.mapas_creados_count}")
            except Exception as e:
                print(f"ERROR: No se pudieron guardar estadísticas al cerrar sesión: {e}")

        # Proceder con el cierre de sesión
        self.is_logged_in = False
        self.logged_in_username = ""  # Corregido: username → logged_in_username
        self.active_tab = "inicio"
        # Reiniciar todas las variables de estado relacionadas con la sesión
        self.selected_curso = ""
        self.selected_libro = ""
        self.selected_tema = ""
        self.mapa_image_url = ""
        # Eliminamos la redirección que podría causar el error 404
        yield  # Usamos yield en lugar de return para que Reflex maneje la redirección internamente

    def clear_selection_and_results(self):
        print("DEBUG: Ejecutando clear_selection_and_results...")
        self.selected_tema = ""
        self.selected_libro = ""
        self.resumen_content = ""
        self.puntos_content = ""
        self.mapa_mermaid_code = ""
        self.mapa_image_url = ""
        self.error_message_ui = ""

    def handle_curso_change(self, new_curso: str):
        print(f"DEBUG: handle_curso_change -> {new_curso}")
        self.selected_curso = new_curso
        self.selected_libro = ""
        self.selected_tema = ""
        self.error_message_ui = ""
        yield

    def handle_libro_change(self, new_libro: str):
        print(f"DEBUG: handle_libro_change -> {new_libro}")
        self.selected_libro = new_libro
        self.selected_tema = ""
        self.error_message_ui = ""
        yield

    def handle_libros_curso_change(self, new_curso: str):
        print(f"DEBUG: handle_libros_curso_change -> {new_curso}")
        self.selected_curso = new_curso
        self.selected_libro = ""
        self.error_message_ui = ""
        yield

    def handle_libros_libro_change(self, new_libro: str):
        print(f"DEBUG: handle_libros_libro_change -> {new_libro}")
        self.selected_libro = new_libro
        self.error_message_ui = ""
        yield

    def set_selected_tema(self, new_tema: str):
        if not isinstance(new_tema, str):
            return
        print(f"DEBUG: set_selected_tema -> {new_tema[:50]}...")
        self.selected_tema = new_tema
        yield

    def set_include_puntos(self, value: bool):
        if not isinstance(value, bool):
            return
        self.include_puntos = value
        yield

    def handle_puntos_switch(self, value: bool):
        """Manejador seguro para el switch de puntos clave que verifica el estado del tema."""
        # Verificamos si hay un tema seleccionado y solo entonces cambiamos el estado
        if self.selected_tema != "":  # Esta evaluación ocurre en el backend (Python), no en el frontend (JavaScript)
            self.include_puntos = value
        yield
        
    def set_mapa_orientacion(self, value: bool):
        if not isinstance(value, bool):
            return
        self.mapa_orientacion_horizontal = value
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        yield

    def clear_map(self):
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        self.error_message_ui = ""
        yield

    def toggle_language(self):
        """Cambia el idioma entre español (es) e inglés (en)."""
        self.current_language = "en" if self.current_language == "es" else "es"
        yield
        
    @rx.var
    def language_text(self) -> str:
        """Devuelve el texto a mostrar en el botón de idioma."""
        return self.translate("switch_language")
    
    @rx.var
    def tab_inicio_text(self) -> str:
        """Returns the translated Home tab text."""
        return self.translate("tab_inicio")
    
    @rx.var
    def tab_libros_text(self) -> str:
        """Returns the translated Books tab text."""
        return self.translate("tab_libros")
        
    @rx.var
    def tab_resumen_text(self) -> str:
        """Returns the translated Summary tab text."""
        return self.translate("tab_resumen")
        
    @rx.var
    def tab_mapa_text(self) -> str:
        """Returns the translated Mind Map tab text."""
        return self.translate("tab_mapa")
        
    @rx.var
    def tab_cuestionario_text(self) -> str:
        """Returns the translated Questionnaire tab text."""
        return self.translate("tab_cuestionario")
        
    @rx.var
    def tab_evaluacion_text(self) -> str:
        """Returns the translated Evaluation tab text."""
        return self.translate("tab_evaluacion")
        
    @rx.var
    def tab_perfil_text(self) -> str:
        """Returns the translated Profile tab text."""
        return self.translate("tab_perfil")
        
    @rx.var
    def tab_ayuda_text(self) -> str:
        """Returns the translated Help tab text."""
        return self.translate("tab_ayuda")
    
    @rx.var
    def app_tagline_text(self) -> str:
        """Returns the translated app tagline."""
        return self.translate("app_tagline")
        
    def translate(self, key: str, default: str = None) -> str:
        """
        Traduce una clave según el idioma seleccionado.
        
        Args:
            key: Clave de traducción a buscar
            default: Valor por defecto si la clave no se encuentra
            
        Returns:
            Texto traducido según el idioma actual
        """
        translations = get_translations(self.current_language)
        if key in translations:
            return translations[key]
        return default if default else key
        
    @rx.var
    def welcome_text(self) -> str:
        """Returns the translated welcome text with emoji."""
        return "🏠 " + self.translate("welcome")
        
    @rx.var
    def welcome_subtitle_text(self) -> str:
        """Returns the translated welcome subtitle."""
        return self.translate("welcome_subtitle")
        
    # Feature section translations
    @rx.var
    def digital_books_title(self) -> str:
        return self.translate("digital_books")
        
    @rx.var
    def digital_books_desc(self) -> str:
        return self.translate("digital_books_desc")
        
    @rx.var
    def view_books_text(self) -> str:
        return self.translate("view_books")
        
    # Login page translations
    @rx.var
    def login_title_text(self) -> str:
        """Returns the translated login title text."""
        return self.translate("login_title")
    
    @rx.var
    def login_subtitle_text(self) -> str:
        """Returns the translated login subtitle text."""
        return self.translate("login_subtitle")
    
    @rx.var
    def username_placeholder_text(self) -> str:
        """Returns the translated username placeholder text."""
        return self.translate("username")
    
    @rx.var
    def password_placeholder_text(self) -> str:
        """Returns the translated password placeholder text."""
        return self.translate("password")
    
    @rx.var
    def forgot_password_text(self) -> str:
        """Returns the translated forgot password text."""
        return self.translate("forgot_password")
        
    @rx.var
    def login_button_text(self) -> str:
        """Returns the translated login button text."""
        return self.translate("login_button")
    
    @rx.var
    def sign_out_text(self) -> str:
        """Returns the translated sign out button text."""
        return self.translate("sign_out")
    
    @rx.var
    def switch_language_text(self) -> str:
        """Returns the translated switch language text."""
        return self.translate("switch_language")
    
    @rx.var
    def header_title_text(self) -> str:
        """Returns the translated header title."""
        return self.translate("header_title")
    
    @rx.var
    def app_tagline_text(self) -> str:
        """Returns the translated app tagline."""
        return self.translate("app_tagline")
    
    @rx.var
    def login_error_text(self) -> str:
        """Returns the translated login error message."""
        return self.translate("login_error")
    
    # Help tab translations
    @rx.var
    def help_center_text(self) -> str:
        """Returns the translated help center text."""
        return "🔍 " + self.translate("help_center")
    
    @rx.var
    def help_subtitle_text(self) -> str:
        """Returns the translated help subtitle text."""
        return self.translate("help_subtitle")
    
    @rx.var
    def frequent_questions_text(self) -> str:
        """Returns the translated frequent questions text."""
        return self.translate("frequent_questions")
    
    @rx.var
    def not_found_help_text(self) -> str:
        """Returns the translated not found help text."""
        return self.translate("not_found_help")
    
    @rx.var
    def contact_us_text(self) -> str:
        """Returns the translated contact us text."""
        return self.translate("contact_us")
        
    @rx.var
    def intelligent_summaries_title(self) -> str:
        return self.translate("intelligent_summaries")
        
    @rx.var
    def intelligent_summaries_desc(self) -> str:
        return self.translate("intelligent_summaries_desc")
        
    @rx.var
    def create_summary_text(self) -> str:
        return self.translate("create_summary")
        
    @rx.var
    def concept_maps_title(self) -> str:
        return self.translate("concept_maps")
        
    @rx.var
    def concept_maps_desc(self) -> str:
        return self.translate("concept_maps_desc")
        
    @rx.var
    def create_map_text(self) -> str:
        return self.translate("create_map")
        
    @rx.var
    def questionnaires_title(self) -> str:
        return self.translate("questionnaires")
        
    @rx.var
    def questionnaires_desc(self) -> str:
        return self.translate("questionnaires_desc")
        
    @rx.var
    def create_questionnaire_text(self) -> str:
        return self.translate("create_questionnaire")
    
    # Questionnaire tab translations
    @rx.var
    def questionnaire_challenge_heading_text(self) -> str:
        return self.translate("questionnaire_challenge_heading")
        
    @rx.var
    def questionnaire_subtitle_text(self) -> str:
        return self.translate("questionnaire_subtitle")
        
    @rx.var
    def select_course_questionnaire_text(self) -> str:
        return self.translate("select_course_questionnaire")
        
    @rx.var
    def select_book_questionnaire_text(self) -> str:
        return self.translate("select_book_questionnaire")
        
    @rx.var
    def questionnaire_topic_placeholder_text(self) -> str:
        return self.translate("questionnaire_topic_placeholder")
        
    @rx.var
    def generating_questionnaire_text(self) -> str:
        return self.translate("generating_questionnaire")
        
    @rx.var
    def generate_questionnaire_button_text(self) -> str:
        return self.translate("generate_questionnaire_button")
        
    @rx.var
    def questionnaire_heading_text(self) -> str:
        return self.translate("questionnaire_heading")
        
    @rx.var
    def question_number_text(self) -> str:
        return self.translate("question_number")
        
    @rx.var
    def answer_label_text(self) -> str:
        return self.translate("answer_label")
        
    @rx.var
    def assessments_title(self) -> str:
        return self.translate("assessments")
        
    @rx.var
    def assessments_desc(self) -> str:
        return self.translate("assessments_desc")
        
    @rx.var
    def create_assessment_text(self) -> str:
        return self.translate("create_assessment")
    
    # Evaluation tab translations
    @rx.var
    def evaluation_heading_text(self) -> str:
        return self.translate("evaluation_heading")
        
    @rx.var
    def evaluation_subtitle_text(self) -> str:
        return self.translate("evaluation_subtitle")
        
    @rx.var
    def select_course_evaluation_text(self) -> str:
        return self.translate("select_course_evaluation")
        
    @rx.var
    def select_book_evaluation_text(self) -> str:
        return self.translate("select_book_evaluation")
        
    @rx.var
    def evaluation_topic_placeholder_text(self) -> str:
        return self.translate("evaluation_topic_placeholder")
        
    @rx.var
    def generating_evaluation_text(self) -> str:
        return self.translate("generating_evaluation")
        
    @rx.var
    def generate_evaluation_button_text(self) -> str:
        return self.translate("generate_evaluation_button")
        
    @rx.var
    def question_text(self) -> str:
        return self.translate("question_text")
        
    @rx.var
    def of_text(self) -> str:
        return self.translate("of_text")
        
    @rx.var
    def previous_button_text(self) -> str:
        return self.translate("previous_button")
        
    @rx.var
    def next_button_text(self) -> str:
        return self.translate("next_button")
        
    @rx.var
    def finish_evaluation_button_text(self) -> str:
        return self.translate("finish_evaluation_button")
        
    @rx.var
    def finish_review_button_text(self) -> str:
        return self.translate("finish_review_button")
        
    @rx.var
    def evaluation_completed_text(self) -> str:
        return self.translate("evaluation_completed")
        
    @rx.var
    def completed_text(self) -> str:
        return self.translate("completed_text")
        
    @rx.var
    def correct_answers_text(self) -> str:
        return self.translate("correct_answers_text")
        
    @rx.var
    def of_questions_text(self) -> str:
        return self.translate("of_questions_text")
        
    @rx.var
    def questions_text(self) -> str:
        return self.translate("questions_text")
        
    @rx.var
    def motivation_text_1(self) -> str:
        return self.translate("motivation_text_1")
        
    @rx.var
    def motivation_text_2(self) -> str:
        return self.translate("motivation_text_2")
        
    @rx.var
    def new_evaluation_button_text(self) -> str:
        return self.translate("new_evaluation_button")
        
    @rx.var
    def review_button_text(self) -> str:
        return self.translate("review_button")
        
    @rx.var
    def popular_resources_text(self) -> str:
        return self.translate("popular_resources")
        
    # Books tab translations
    @rx.var
    def digital_library_title(self) -> str:
        return self.translate("digital_library")
        
    @rx.var
    def digital_library_desc(self) -> str:
        return self.translate("digital_library_desc")
        
    @rx.var
    def select_course_placeholder(self) -> str:
        return self.translate("select_course_placeholder")
        
    @rx.var
    def select_book_placeholder(self) -> str:
        return self.translate("select_book_placeholder")
        
    @rx.var
    def download_pdf_button_text(self) -> str:
        return self.translate("download_pdf_button")
        
    # Summary tab translations
    @rx.var
    def intelligent_summaries_title(self) -> str:
        return self.translate("intelligent_summaries_title")
        
    @rx.var
    def intelligent_summaries_subtitle(self) -> str:
        return self.translate("intelligent_summaries_subtitle")
        
    @rx.var
    def specific_topic_placeholder(self) -> str:
        return self.translate("specific_topic_placeholder")
        
    @rx.var
    def include_key_points_switch_text(self) -> str:
        return self.translate("include_key_points_switch")
        
    @rx.var
    def generate_summary_button_text(self) -> str:
        return self.translate("generate_summary_button")
        
    @rx.var
    def generating_summary_text(self) -> str:
        return self.translate("generating_summary_text")
        
    @rx.var
    def summary_heading_text(self) -> str:
        return self.translate("summary_heading")
        
    @rx.var
    def key_points_heading_text(self) -> str:
        return self.translate("key_points_heading")
        
    @rx.var
    def create_map_button_text(self) -> str:
        return self.translate("create_map_button")
        
    @rx.var
    def create_questionnaire_button_text(self) -> str:
        return self.translate("create_questionnaire_button")
        
    @rx.var
    def create_evaluation_button_text(self) -> str:
        return self.translate("create_evaluation_button")
        
    # Mind Maps tab translations
    @rx.var
    def create_mind_maps_title(self) -> str:
        return self.translate("create_mind_maps_title")
    
    @rx.var
    def mind_maps_subtitle(self) -> str:
        return self.translate("mind_maps_subtitle")
    
    @rx.var
    def mind_map_select_course_placeholder(self) -> str:
        return self.translate("select_course_placeholder")
    
    @rx.var
    def mind_map_select_book_placeholder(self) -> str:
        return self.translate("select_book_placeholder")
    
    @rx.var
    def mind_map_topic_placeholder(self) -> str:
        return self.translate("topic_placeholder")
    
    @rx.var
    def mind_map_horizontal_orientation_text(self) -> str:
        return self.translate("horizontal_orientation")
    
    @rx.var
    def generating_map_text(self) -> str:
        return self.translate("generating_map_text")
    
    @rx.var
    def generate_map_button_text(self) -> str:
        return self.translate("generate_map_button")
    
    @rx.var
    def mind_map_heading_text(self) -> str:
        return self.translate("mind_map_heading")
        
    @rx.var
    def get_tab_text(self) -> Dict[str, str]:
        """
        Returns a dictionary with tab text translations for the current language.
        This is used to avoid calling translate() directly in component props.
        """
        return {
            "inicio": "Home" if self.current_language == "en" else "Inicio",
            "libros": "Books" if self.current_language == "en" else "Libros",
            "resumen": "Summary" if self.current_language == "en" else "Resumen",
            "mapa": "Mind Map" if self.current_language == "en" else "Mapa Mental",
            "cuestionario": "Questionnaire" if self.current_language == "en" else "Cuestionario",
            "evaluacion": "Evaluation" if self.current_language == "en" else "Evaluación", 
            "perfil": "Profile" if self.current_language == "en" else "Perfil",
            "ayuda": "Help" if self.current_language == "en" else "Ayuda"
        }
    
    # Profile tab text translations
    @rx.var
    def profile_heading_text(self) -> str:
        """Returns the translated profile heading text."""
        return "👤 " + self.translate("profile_heading")
    
    @rx.var
    def profile_subtitle_text(self) -> str:
        """Returns the translated profile subtitle text."""
        return self.translate("profile_subtitle")
    
    @rx.var
    def confirm_action_text(self) -> str:
        """Returns the translated confirm action text."""
        return self.translate("confirm_action")
    
    @rx.var
    def cancel_button_text(self) -> str:
        """Returns the translated cancel button text."""
        return self.translate("cancel_button")
    
    @rx.var
    def confirm_button_text(self) -> str:
        """Returns the translated confirm button text."""
        return self.translate("confirm_button")
    
    @rx.var
    def name_label_text(self) -> str:
        """Returns the translated name label text."""
        return self.translate("name_label")
    
    @rx.var
    def level_label_text(self) -> str:
        """Returns the translated level label text."""
        return self.translate("level_label")
    
    @rx.var
    def active_course_label_text(self) -> str:
        """Returns the translated active course label text."""
        return self.translate("active_course_label")
    
    @rx.var
    def subjects_label_text(self) -> str:
        """Returns the translated subjects label text."""
        return self.translate("subjects_label")
    
    @rx.var
    def evaluations_completed_label_text(self) -> str:
        """Returns the translated evaluations completed label text."""
        return self.translate("evaluations_completed_label")
    
    @rx.var
    def change_password_button_text(self) -> str:
        """Returns the translated change password button text."""
        return self.translate("change_password_button")
    
    @rx.var
    def download_history_button_text(self) -> str:
        """Returns the translated download history button text."""
        return self.translate("download_history_button")
    
    @rx.var
    def delete_history_button_text(self) -> str:
        """Returns the translated delete history button text."""
        return self.translate("delete_history_button")
    
    @rx.var
    def learning_statistics_text(self) -> str:
        """Returns the translated learning statistics text."""
        return "📊 " + self.translate("learning_statistics")
    
    @rx.var
    def progress_by_subject_text(self) -> str:
        """Returns the translated progress by subject text."""
        return self.translate("progress_by_subject")
    
    @rx.var
    def mathematics_text(self) -> str:
        """Returns the translated mathematics text."""
        return self.translate("mathematics")
    
    @rx.var
    def science_text(self) -> str:
        """Returns the translated science text."""
        return self.translate("science")
    
    @rx.var
    def history_text(self) -> str:
        """Returns the translated history text."""
        return self.translate("history")
    
    @rx.var
    def language_subject_text(self) -> str:
        """Returns the translated language subject text."""
        return self.translate("language")
    
    @rx.var
    def evaluations_completed_text(self) -> str:
        """Returns the translated evaluations completed text."""
        return self.translate("evaluations_completed")
    
    @rx.var
    def average_score_text(self) -> str:
        """Returns the translated average score text."""
        return self.translate("average_score")
    
    @rx.var
    def maps_created_text(self) -> str:
        """Returns the translated maps created text."""
        return self.translate("maps_created")
    
    @rx.var
    def summaries_generated_text(self) -> str:
        """Returns the translated summaries generated text."""
        return self.translate("summaries_generated")
    
    @rx.var
    def evaluation_history_text(self) -> str:
        """Returns the translated evaluation history text."""
        return "📚 " + self.translate("evaluation_history")
    
    @rx.var
    def evaluation_history_subtitle_text(self) -> str:
        """Returns the translated evaluation history subtitle text."""
        return self.translate("evaluation_history_subtitle")
    
    @rx.var
    def date_column_text(self) -> str:
        """Returns the translated date column text."""
        return self.translate("date_column")
    
    @rx.var
    def book_column_text(self) -> str:
        """Returns the translated book column text."""
        return self.translate("book_column")
    
    @rx.var
    def topic_column_text(self) -> str:
        """Returns the translated topic column text."""
        return self.translate("topic_column")
    
    @rx.var
    def score_column_text(self) -> str:
        """Returns the translated score column text."""
        return self.translate("score_column")
    
    @rx.var
    def points_column_text(self) -> str:
        """Returns the translated points column text."""
        return self.translate("points_column")
    
    @rx.var
    def review_button_text(self) -> str:
        """Returns the translated review button text."""
        return self.translate("review_button")
    
    @rx.var
    def previous_button_page_text(self) -> str:
        """Returns the translated previous button text."""
        return self.translate("previous_button_page")
    
    @rx.var
    def next_button_page_text(self) -> str:
        """Returns the translated next button text."""
        return self.translate("next_button_page")
    
    @rx.var
    def page_text(self) -> str:
        """Returns the translated page text."""
        return self.translate("page_text")
        
    def set_language(self, lang: str):
        """Establece el idioma directamente."""
        if lang in ["es", "en"]:
            self.current_language = lang
        yield

    async def generate_summary(self):
        print("DEBUG: Iniciando generate_summary...")
        if not self.selected_curso or not self.selected_libro or not self.selected_tema:
            self.error_message_ui = "Selecciona curso, libro y tema."
            yield
            return
        if not BACKEND_AVAILABLE:
            self.error_message_ui = "Servicio no disponible."
            yield
            return
        self.is_generating_resumen = True
        self.resumen_content = ""
        self.puntos_content = ""
        self.error_message_ui = ""
        yield
        try:
            if not hasattr(resumen_logic, "generar_resumen_logica"):
                raise AttributeError("Falta resumen_logic.generar_resumen_logica")
            print(f"DEBUG: Llamando resumen_logic con C='{self.selected_curso}', L='{self.selected_libro}', T='{self.selected_tema}', Puntos={self.include_puntos}")
            result = resumen_logic.generar_resumen_logica(
                self.selected_curso, self.selected_libro, self.selected_tema.strip(), self.include_puntos
            )
            print(f"DEBUG: Resultado de resumen_logic: {result}")
            if isinstance(result, dict) and result.get("status") == "EXITO":
                self.resumen_content = result.get("resumen", "")
                if self.include_puntos:
                    puntos = result.get("puntos")
                    self.puntos_content = puntos if isinstance(puntos, str) else ""
                else:
                    self.puntos_content = ""
                    
                # Incrementar el contador de resúmenes generados
                self.resumenes_generados_count += 1
                print(f"DEBUG: Incrementado contador de resúmenes a {self.resumenes_generados_count}")
                
                # Persistir el contador en la BD
                if BACKEND_AVAILABLE and hasattr(db_logic, "update_user_stats") and self.logged_in_username:
                    try:
                        db_logic.update_user_stats(self.logged_in_username, resumenes_count=self.resumenes_generados_count)
                    except Exception as e:
                        print(f"ERROR: No se pudo actualizar contador de resúmenes en BD: {e}")
            else:
                msg = result.get("message", "Error resumen.") if isinstance(result, dict) else "Error respuesta."
                self.error_message_ui = msg
                print(f"ERROR: Falla en resumen_logic: {msg}")
        except AttributeError as ae:
            self.error_message_ui = f"Error config: {ae}"
            print(f"ERROR Config: {self.error_message_ui}")
        except Exception as e:
            self.error_message_ui = f"Error crítico resumen: {str(e)}"
            print(f"ERROR G-SUM: {traceback.format_exc()}")
        finally:
            self.is_generating_resumen = False
            yield

    async def generate_map(self):
        print("DEBUG: Iniciando generate_map...")
        if not self.selected_tema:
            self.error_message_ui = "Ingresa un tema."
            yield
            return
        if not BACKEND_AVAILABLE:
            self.error_message_ui = "Servicio no disponible."
            yield
            return
        self.is_generating_mapa = True
        self.error_message_ui = ""
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        yield
        try:
            if not all(hasattr(map_logic, fn) for fn in ["generar_nodos_localmente", "generar_mermaid_code", "generar_visualizacion_html"]):
                raise AttributeError("Funciones de map_logic faltantes.")
            print(f"DEBUG: Llamando map_logic.generar_nodos_localmente con T='{self.selected_tema}'")
            resultado_nodos = map_logic.generar_nodos_localmente(self.selected_tema.strip())
            print(f"DEBUG: Resultado nodos: {resultado_nodos}")
            
            # PASO 1: Convertir los nodos a formato de texto estructurado para Mermaid
            if resultado_nodos.get("status") == "EXITO" and "nodos" in resultado_nodos:
                nodos = resultado_nodos["nodos"]
                estructura_texto = f"- Nodo Central: {self.selected_tema.strip().title()}\n"
                
                for nodo in nodos:
                    titulo = nodo.get("titulo", "")
                    if titulo:
                        estructura_texto += f"  - Nodo Secundario: {titulo}\n"
                        
                        for subnodo in nodo.get("subnodos", []):
                            estructura_texto += f"    - Nodo Terciario: {subnodo}\n"
                
                # PASO 2: Generar código Mermaid a partir de la estructura de texto
                print("DEBUG: Generando código Mermaid a partir de la estructura...")
                orientation = "LR" if self.mapa_orientacion_horizontal else "TD"
                mermaid_code, error_mermaid = map_logic.generar_mermaid_code(estructura_texto, orientation)
                
                if error_mermaid:
                    raise Exception(f"Error generando código Mermaid: {error_mermaid}")
                
                if not mermaid_code:
                    raise Exception("No se generó código Mermaid válido")
                
                self.mapa_mermaid_code = mermaid_code
                
                # PASO 3: Generar HTML para visualización
                print("DEBUG: Generando HTML para visualización del mapa...")
                html_url = map_logic.generar_visualizacion_html(mermaid_code, self.selected_tema)
                
                if not html_url:
                    raise Exception("No se pudo generar la visualización HTML")
                
                # PASO 4: Actualizar la URL de la imagen para mostrarla en la UI
                self.mapa_image_url = html_url
                print(f"DEBUG: HTML URL generada: {html_url[:100]}...")
                
                # Incrementar el contador de mapas creados
                self.mapas_creados_count += 1
                print(f"DEBUG: Incrementado contador de mapas a {self.mapas_creados_count}")
            else:
                raise Exception(f"Error en resultado de nodos: {resultado_nodos.get('status')}")
                
        except AttributeError as ae:
            self.error_message_ui = f"Error config map: {ae}"
            print(f"ERROR Config: {self.error_message_ui}")
        except Exception as e:
            self.error_message_ui = f"Error generando mapa: {str(e)}"
            print(f"ERROR G-MAP: {traceback.format_exc()}")
        finally:
            self.is_generating_mapa = False
            yield

    async def load_stats(self):
        print("DEBUG: Iniciando load_stats...")
        if not self.logged_in_username:
            self.stats_history = []
            self.is_loading_stats = False
            yield
            return
        self.is_loading_stats = True
        yield
        try:
            # Primero obtenemos el historial de evaluaciones completo
            if hasattr(db_logic, "obtener_historial"):
                historial = db_logic.obtener_historial(self.logged_in_username)
                if historial and isinstance(historial, list):
                    self.stats_history = historial
                    
                    # Procesamos cada evaluación para asegurarnos de que tenga la calificación como porcentaje (0-100)
                    for item in self.stats_history:
                        # Si tiene nota pero no tiene calificación, convertimos la nota a porcentaje (0-100)
                        if "nota" in item and "calificacion" not in item:
                            try:
                                nota = float(item["nota"])
                                # Si la nota está en escala 1.0-7.0 (sistema chileno), convertir a porcentaje
                                if 1.0 <= nota <= 7.0:
                                    porcentaje = ((nota - 1.0) / 6.0) * 100
                                    item["calificacion"] = round(porcentaje)
                                else:
                                    # Asumir que es directamente un porcentaje
                                    item["calificacion"] = round(nota)
                            except (ValueError, TypeError):
                                item["calificacion"] = 0
                                
                        # Asegurar que tenemos una calificación válida
                        if "calificacion" not in item:
                            item["calificacion"] = 0
                            
                        # Si tenemos información de respuestas, calculamos el porcentaje exacto
                        if "metadata" in item and item["metadata"]:
                            try:
                                if "Correctas:" in item["metadata"]:
                                    correctas_part = item["metadata"].split("Correctas:")[1].strip()
                                    if "/" in correctas_part:
                                        correctas, total = correctas_part.split("/")
                                        correctas = int(correctas)
                                        total = int(total)
                                        if total > 0:
                                            porcentaje = (correctas / total) * 100
                                            item["calificacion"] = round(porcentaje)
                                            item["respuestas_correctas"] = correctas
                                            item["total_preguntas"] = total
                            except Exception as metadata_e:
                                print(f"ERROR procesando metadata: {metadata_e}")
                    
                    print(f"DEBUG: Cargado historial de evaluaciones: {len(historial)} registros")
                    if historial:
                        print(f"DEBUG: Muestra de primer registro: {historial[0]}")
                else:
                    self.stats_history = []
                    print("DEBUG: No se encontró historial de evaluaciones")
            else:
                # Fallback al método anterior (solo estadísticas)
                if not hasattr(db_logic, "obtener_estadisticas_usuario"):
                    raise AttributeError("Falta db_logic.obtener_estadisticas_usuario")
                
                stats_raw = db_logic.obtener_estadisticas_usuario(self.logged_in_username)
                
                # Procesar las estadísticas recibidas
                if isinstance(stats_raw, list):
                    self.stats_history = stats_raw
                elif isinstance(stats_raw, dict) and stats_raw:
                    self.stats_history = [stats_raw]
                else:
                    self.stats_history = []
                
            # Restablecer a la primera página cuando se cargan nuevas estadísticas
            self.historial_evaluaciones_pagina_actual = 1
            
        except Exception as e:
            print(f"ERROR cargando estadísticas: {e}")
            self.stats_history = []
        finally:
            self.is_loading_stats = False
            yield
            
    def pagina_siguiente(self):
        """Avanza a la siguiente página de historial de evaluaciones."""
        if self.historial_evaluaciones_pagina_actual < self.total_paginas_historial:
            self.historial_evaluaciones_pagina_actual += 1
        print(f"DEBUG: Avanzando a página {self.historial_evaluaciones_pagina_actual} de {self.total_paginas_historial}")
        yield
        
    def pagina_anterior(self):
        """Retrocede a la página anterior de historial de evaluaciones."""
        if self.historial_evaluaciones_pagina_actual > 1:
            self.historial_evaluaciones_pagina_actual -= 1
        print(f"DEBUG: Retrocediendo a página {self.historial_evaluaciones_pagina_actual}")
        yield
        
    # Variables para el diálogo de confirmación
    mostrar_dialogo_confirmacion: bool = False
    mostrar_dialogo_confirmar_eliminar: bool = False
    accion_pendiente: str = ""
    mensaje_confirmacion: str = ""
    
    def mostrar_confirmacion_eliminar_historial(self):
        """Muestra un diálogo de confirmación antes de eliminar el historial."""
        self.mostrar_dialogo_confirmacion = True
        self.accion_pendiente = "eliminar_historial"
        self.mensaje_confirmacion = "¿Estás seguro que deseas eliminar todo tu historial de evaluaciones? Esta acción no se puede deshacer."
    
    def cancelar_eliminar_historial(self):
        """Cancela la acción de eliminar historial y cierra el diálogo de confirmación."""
        self.mostrar_dialogo_confirmacion = False
        self.accion_pendiente = None
    
    def eliminar_historial_usuario(self):
        """Elimina todo el historial de evaluaciones del usuario."""
        if BACKEND_AVAILABLE and hasattr(db_logic, "eliminar_historial_usuario"):
            try:
                resultado = db_logic.eliminar_historial_usuario(self.usuario_actual)
                if resultado:
                    self.mostrar_notificacion("Historial eliminado correctamente.")
                    # Actualizar la lista de historial después de eliminar
                    self.cargar_historial_evaluaciones()
                else:
                    self.mostrar_notificacion("No se pudo eliminar el historial.", tipo="error")
            except Exception as e:
                print(f"Error al eliminar historial: {e}")
                self.mostrar_notificacion(f"Error al eliminar el historial: {str(e)}", tipo="error")
        else:
            print("Mock: Eliminar historial del usuario")
            self.mostrar_notificacion("Historial eliminado (simulado).")
            # Simulamos eliminar el historial vaciando la lista
            self.historial_evaluaciones = []
            self.historial_evaluaciones_paginado = []
            self.total_paginas_historial = 1
            self.historial_evaluaciones_pagina_actual = 1
        
        # Cerrar el diálogo de confirmación
        self.mostrar_dialogo_confirmacion = False
        self.accion_pendiente = None
        
    def cancelar_accion(self):
        """Cancela la acción pendiente y cierra el diálogo de confirmación."""
        self.mostrar_dialogo_confirmacion = False
        self.accion_pendiente = ""
        self.mensaje_confirmacion = ""
        
    async def confirmar_accion(self):
        """Ejecuta la acción pendiente después de la confirmación."""
        if self.accion_pendiente == "eliminar_historial":
            self.mostrar_dialogo_confirmacion = False
            self.accion_pendiente = ""
            self.mensaje_confirmacion = ""
            
            # Continuar con la eliminación
            async for _ in self._eliminar_historial_evaluaciones():
                pass
    
    async def _eliminar_historial_evaluaciones(self):
        """Elimina todo el historial de evaluaciones del usuario actual."""
        if not self.logged_in_username:
            self.error_message_ui = "Debes iniciar sesión para realizar esta acción"
            yield
            return
        
        try:
            # Marcar como cargando para mostrar el spinner
            self.is_loading_stats = True
            yield
            
            # Llamar al backend para eliminar el historial
            if BACKEND_AVAILABLE and hasattr(db_logic, "eliminar_historial_evaluaciones"):
                success = db_logic.eliminar_historial_evaluaciones(self.logged_in_username)
                if success:
                    self.stats_history = []  # Vaciar el historial en el frontend
                    self.historial_evaluaciones_pagina_actual = 1  # Volver a la primera página
                    self.error_message_ui = ""  # Limpiar mensajes de error
                    print(f"INFO: Historial de evaluaciones de '{self.logged_in_username}' eliminado con éxito.")
                else:
                    self.error_message_ui = "No se pudo eliminar el historial de evaluaciones"
            else:
                print("ERROR: Backend no disponible o falta función eliminar_historial_evaluaciones")
                self.error_message_ui = "Servicio no disponible. Inténtalo más tarde."
        except Exception as e:
            print(f"ERROR eliminando historial: {e}")
            self.error_message_ui = f"Error al eliminar el historial: {str(e)}"
        finally:
            self.is_loading_stats = False
            yield
        
    @rx.var
    def total_paginas_historial(self) -> int:
        """Calcula el número total de páginas del historial de evaluaciones."""
        return (len(self.stats_history) + self.historial_evaluaciones_por_pagina - 1) // self.historial_evaluaciones_por_pagina
        
    @rx.var
    def tiene_siguiente_pagina(self) -> bool:
        """Indica si hay una página siguiente disponible."""
        return self.historial_evaluaciones_pagina_actual < self.total_paginas_historial
        
    @rx.var
    def tiene_pagina_anterior(self) -> bool:
        """Indica si hay una página anterior disponible."""
        return self.historial_evaluaciones_pagina_actual > 1

    async def download_pdf(self):
        """Función general para descargar PDFs según el contexto actual (resumen, mapa o cuestionario)"""
        print("DEBUG: Iniciando download_pdf...")
        
        # Determinar qué tipo de contenido descargar según la pestaña activa
        if self.active_tab == "resumen":
            async for result in self.download_resumen_pdf():
                yield result
        elif self.active_tab == "mapa":
            async for result in self.download_map_pdf():
                yield result
        elif self.active_tab == "cuestionario":
            async for result in self.download_cuestionario_pdf():
                yield result
        else:
            self.error_message_ui = "No hay contenido disponible para descargar."
            yield

    async def download_resumen_pdf(self):
        """Descarga el resumen actual en formato PDF"""
        print("DEBUG: Iniciando download_resumen_pdf...")
        if not self.resumen_content:
            self.error_message_ui = "No hay resumen para descargar."
            yield
            return

        s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "tema")[:50]
        s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "libro")[:50]
        s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "curso")[:50]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fname_base = f"Resumen_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")

        try:
            pdf_generado = False
            if hasattr(resumen_logic, "generar_resumen_pdf_bytes"):
                print("DEBUG: Intentando generar PDF con resumen_logic...")
                try:
                    pdf_bytes = resumen_logic.generar_resumen_pdf_bytes(
                        resumen_txt=self.resumen_content,
                        puntos_txt=self.puntos_content if self.include_puntos else "",
                        titulo=f"Resumen: {self.selected_tema or 'General'}",
                        subtitulo=f"Curso: {self.selected_curso or 'N/A'} - Libro: {self.selected_libro or 'N/A'}",
                    )
                    if isinstance(pdf_bytes, bytes) and pdf_bytes.startswith(b"%PDF"):
                        fname = f"{fname_base}.pdf"
                        print(f"DEBUG: PDF generado ({len(pdf_bytes)} bytes). Descargando como {fname}")
                        yield rx.download(data=pdf_bytes, filename=fname)
                        pdf_generado = True
                    else:
                        print("WARN: resumen_logic.generar_resumen_pdf_bytes no devolvió un PDF válido.")
                except Exception as pdf_e:
                    print(f"WARN: Error en generación de PDF con resumen_logic (usando fallback HTML): {pdf_e}")

            if not pdf_generado:
                print("DEBUG: Generando fallback HTML...")
                html_content = f"""<!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Resumen: {s_tema}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                        h1 {{ color: #2563eb; }}
                        h2 {{ color: #4b5563; margin-top: 30px; }}
                        .resumen {{ background-color: #f3f4f6; padding: 20px; border-radius: 5px; }}
                        .puntos {{ margin-top: 30px; }}
                        .puntos ol {{ padding-left: 20px; }}
                    </style>
                </head>
                <body>
                    <h1>Resumen: {self.selected_tema}</h1>
                    <h3>Curso: {self.selected_curso} - Libro: {self.selected_libro}</h3>
                    <hr>
                    <div class="resumen">
                        {self.resumen_content.replace(chr(10), '<br>')}
                    </div>"""
                    
                # Add puntos section if needed
                if self.puntos_content and self.include_puntos:
                    puntos_html = self.puntos_content.replace('\n', '<br>')
                    html_content += f"""
                    <h2>Puntos Clave:</h2>
                    <div class="puntos">{puntos_html}</div>"""
                
                html_content += f"""
                    <hr>
                    <footer>
                        <p><i>Generado por SMART_STUDENT el {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</i></p>
                    </footer>
                </body>
                </html>"""
                fname = f"{fname_base}.html"
                print(f"DEBUG: Descargando resumen como HTML: {fname}")
                yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)

        except Exception as e:
            self.error_message_ui = f"Error descarga: {str(e)}"
            print(f"ERROR DWNLD PDF/HTML: {traceback.format_exc()}")
            yield

    async def download_map_pdf(self):
        """Descarga el mapa conceptual actual en formato PDF"""
        print("DEBUG: Iniciando download_map_pdf...")
        if not self.mapa_mermaid_code or not self.mapa_image_url:
            self.error_message_ui = "No hay mapa conceptual para descargar."
            yield
            return

        s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "tema")[:50]
        s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "libro")[:50]
        s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "curso")[:50]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fname_base = f"Mapa_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")

        try:
            pdf_generado = False
            if hasattr(map_logic, "generar_mapa_pdf_bytes"):
                print("DEBUG: Intentando generar PDF del mapa con map_logic...")
                try:
                    pdf_bytes = map_logic.generar_mapa_pdf_bytes(
                        mermaid_code=self.mapa_mermaid_code,
                        tema=self.selected_tema,
                        curso=self.selected_curso,
                        libro=self.selected_libro,
                        html_url=self.mapa_image_url
                    )
                    if isinstance(pdf_bytes, bytes) and pdf_bytes.startswith(b"%PDF"):
                        fname = f"{fname_base}.pdf"
                        print(f"DEBUG: PDF del mapa generado ({len(pdf_bytes)} bytes). Descargando como {fname}")
                        yield rx.download(data=pdf_bytes, filename=fname)
                        pdf_generado = True
                    else:
                        print("WARN: map_logic.generar_mapa_pdf_bytes no devolvió un PDF válido.")
                except Exception as pdf_e:
                    print(f"WARN: Error en generación de PDF del mapa (usando fallback HTML): {pdf_e}")
                    traceback.print_exc()

            if not pdf_generado:
                print("DEBUG: Generando mapa fallback HTML...")
                html_content = f"""<!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Mapa Conceptual: {s_tema}</title>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        h1 {{ color: #2563eb; }}
                        .mermaid {{ background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    </style>
                </head>
                <body>
                    <h1>Mapa Conceptual: {self.selected_tema}</h1>
                    <h3>Curso: {self.selected_curso} - Libro: {self.selected_libro}</h3>
                    <hr>
                    <div class="mermaid">
                        {self.mapa_mermaid_code}
                    </div>
                    <script>
                        mermaid.initialize({{
                            startOnLoad: true,
                            theme: 'default',
                            themeVariables: {{
                                primaryColor: '#d4e8ff',
                                primaryTextColor: '#003366',
                                primaryBorderColor: '#7fb3ff',
                                lineColor: '#4b5563',
                                fontSize: '16px'
                            }}
                        }});
                    </script>
                    <hr>
                    <footer>
                        <p><i>Generado por SMART_STUDENT el {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</i></p>
                    </footer>
                </body>
                </html>"""
                fname = f"{fname_base}.html"
                print(f"DEBUG: Descargando mapa como HTML: {fname}")
                yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)

        except Exception as e:
            self.error_message_ui = f"Error al descargar mapa: {str(e)}"
            print(f"ERROR DWNLD MAP PDF/HTML: {traceback.format_exc()}")
            yield

    async def download_cuestionario_pdf(self):
        """Descarga el cuestionario actual en formato PDF"""
        # Importamos solo cuando se necesita para evitar dependencias circulares
        from .cuestionario import CuestionarioState
        
        print("DEBUG: Iniciando download_cuestionario_pdf...")
        
        # Verificamos primero si el atributo existe
        if not hasattr(CuestionarioState, "cuestionario_preguntas"):
            self.error_message_ui = "No hay cuestionario para descargar."
            print("DEBUG: No hay atributo cuestionario_preguntas")
            yield
            return
            
        # Verificamos si hay preguntas de manera segura con variables reactivas
        try:
            # Usamos la función de utilidad para verificar si hay preguntas
            preguntas_lista = get_safe_var_list(CuestionarioState.cuestionario_preguntas, [])
            tiene_preguntas = len(preguntas_lista) > 0
            if tiene_preguntas:
                print(f"DEBUG: Encontradas {len(preguntas_lista)} preguntas en el cuestionario")
            else:
                print("DEBUG: Lista de preguntas vacía")
        except Exception as e:
            print(f"DEBUG: No se encontraron preguntas en el cuestionario: {e}")
            tiene_preguntas = False
            
        # Si no hay preguntas, informar y salir
        if not tiene_preguntas:
            self.error_message_ui = "No hay preguntas en el cuestionario para descargar."
            yield
            return

        # Use rx.cond instead of 'if' and 'or' with reactive variables
        tema_value = rx.cond(
            (CuestionarioState.cuestionario_tema != "") & (CuestionarioState.cuestionario_tema != None),
            CuestionarioState.cuestionario_tema,
            "tema"
        )
        # Utilizar nuestra función de utilidad para obtener el valor de manera segura
        tema_str = get_safe_var_value(tema_value, "tema")
        # Convertir a string antes de usar re.sub
        s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_str)[:50]
        
        libro_value = rx.cond(
            (CuestionarioState.cuestionario_libro != "") & (CuestionarioState.cuestionario_libro != None),
            CuestionarioState.cuestionario_libro,
            "libro"
        )
        # Utilizar nuestra función de utilidad para obtener el valor de manera segura
        libro_str = get_safe_var_value(libro_value, "libro")
        # Convertir a string antes de usar re.sub
        s_lib = re.sub(r'[\\/*?:"<>|]', "", libro_str)[:50]
        
        curso_value = rx.cond(
            (CuestionarioState.cuestionario_curso != "") & (CuestionarioState.cuestionario_curso != None),
            CuestionarioState.cuestionario_curso,
            "curso"
        )
        # Utilizar nuestra función de utilidad para obtener el valor de manera segura
        curso_str = get_safe_var_value(curso_value, "curso")
        # Convertir a string antes de usar re.sub
        s_cur = re.sub(r'[\\/*?:"<>|]', "", curso_str)[:50]
        # Generar timestamp una sola vez
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        # Generar el nombre base del archivo una sola vez
        fname_base = f"Cuestionario_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")
        print(f"DEBUG: Nombre base del archivo generado: {fname_base}")

        try:
            # Primero intentamos utilizar la URL del PDF que ya se generó en la clase CuestionarioState
            # Usando rx.cond en lugar de if/and para manejar variables reactivas
            cuestionario_pdf_url_exists = hasattr(CuestionarioState, "cuestionario_pdf_url")
            print(f"DEBUG: ¿Existe cuestionario_pdf_url? {cuestionario_pdf_url_exists}")
            
            if cuestionario_pdf_url_exists:
                # Usar nuestra función de utilidad para obtener el valor de manera segura
                pdf_url = get_safe_var_value(CuestionarioState.cuestionario_pdf_url, "")
                print(f"DEBUG: PDF URL obtenida de manera segura: {pdf_url}")
                
                is_pdf_url_not_empty = pdf_url != ""
                
                # Ahora usamos variables Python estándar para la lógica condicional
                if is_pdf_url_not_empty:
                    print(f"DEBUG: Usando PDF ya generado: {pdf_url}")
                    
                    # Intentar encontrar la ruta real del archivo usando nuestra lógica mejorada
                    # No usamos la función auxiliar por los problemas de sintaxis
                    
                    # Limpiar la URL para eliminar parámetros
                    clean_url = pdf_url.split('?')[0]
                    
                    # Extraer el nombre base del archivo para búsquedas posteriores
                    pdf_basename = os.path.basename(clean_url)
                    print(f"DEBUG: Nombre base del PDF: {pdf_basename}")
                    
                    # Manejar diferentes tipos de rutas
                    if clean_url.startswith(('http://', 'https://')):
                        # URL externa, intentamos extraer el nombre del archivo y buscarlo localmente
                        print(f"DEBUG: La URL del PDF es externa: {clean_url}")
                        pdf_path = pdf_basename
                    elif clean_url.startswith('/'):
                        # URL relativa, probar sin la barra inicial
                        pdf_path = clean_url.lstrip('/')
                        print(f"DEBUG: URL relativa convertida a: {pdf_path}")
                    else:
                        # Ya es una ruta relativa
                        pdf_path = clean_url
                        print(f"DEBUG: Usando ruta relativa: {pdf_path}")
                        
                    # Intentar encontrar el archivo en diferentes ubicaciones
                    if pdf_path:
                        # Verificar ruta directa
                        if os.path.exists(pdf_path) and os.path.isfile(pdf_path):
                            print(f"DEBUG: Archivo encontrado en ruta directa: {pdf_path}")
                        else:
                            print(f"DEBUG: No se encontró el archivo en: {pdf_path}")
                            
                            # Intentar con la ruta completa original por si acaso
                            if os.path.exists(pdf_url) and os.path.isfile(pdf_url):
                                pdf_path = pdf_url
                                print(f"DEBUG: Archivo encontrado en URL original: {pdf_path}")
                            else:
                                # Buscar en otras ubicaciones comunes
                                asset_path = os.path.join("assets", pdf_path)
                                if os.path.exists(asset_path) and os.path.isfile(asset_path):
                                    pdf_path = asset_path
                                    print(f"DEBUG: Archivo encontrado en assets: {pdf_path}")
                                else:
                                    # Probar en assets/pdfs/
                                    pdfs_path = os.path.join("assets", "pdfs", os.path.basename(pdf_path))
                                    if os.path.exists(pdfs_path) and os.path.isfile(pdfs_path):
                                        pdf_path = pdfs_path
                                        print(f"DEBUG: Archivo encontrado en assets/pdfs/: {pdf_path}")
                                    else:
                                        # Probar en .web/public/assets/pdfs/
                                        web_pdfs_path = os.path.join(".web", "public", "assets", "pdfs", os.path.basename(pdf_path))
                                        if os.path.exists(web_pdfs_path) and os.path.isfile(web_pdfs_path):
                                            pdf_path = web_pdfs_path
                                            print(f"DEBUG: Archivo encontrado en .web/public/assets/pdfs/: {pdf_path}")
                                        else:
                                            # Intentar buscar por patrón de nombre
                                            try:
                                                pdf_name_pattern = os.path.splitext(os.path.basename(pdf_path))[0]
                                                print(f"DEBUG: Buscando archivos con patrón similar: {pdf_name_pattern}")
                                                
                                                # Directorios a buscar
                                                search_dirs = [
                                                    ".",
                                                    "assets", 
                                                    "assets/pdfs",
                                                    "assets/pdf",
                                                    ".web/public/assets/pdfs",
                                                    ".web/public/assets/pdf", 
                                                    ".web/public",
                                                    "public/assets/pdfs",
                                                    "mi_app_estudio/assets/pdfs",
                                                    "/tmp",
                                                    os.path.join(os.getcwd(), "assets", "pdfs")
                                                ]
                                                
                                                # Patrones a buscar (ampliar para mayor coincidencia)
                                                patterns = [
                                                    pdf_name_pattern,
                                                    pdf_basename,
                                                    s_tema.replace(" ", "_"),
                                                    s_lib.replace(" ", "_"),
                                                    "cuestionario"
                                                ]
                                                
                                                found = False
                                                file_count = 0
                                                max_files = 100  # Limitar la búsqueda para evitar bucles infinitos
                                                for search_dir in search_dirs:
                                                    if os.path.exists(search_dir):
                                                        print(f"DEBUG: Buscando en directorio: {search_dir}")
                                                        try:
                                                            for file in os.listdir(search_dir):
                                                                file_count += 1
                                                                if file_count > max_files:
                                                                    print(f"DEBUG: Límite de búsqueda alcanzado ({max_files} archivos)")
                                                                    break
                                                                    
                                                                if file.endswith('.pdf'):
                                                                    # Verificar si alguno de los patrones coincide
                                                                    for pattern in patterns:
                                                                        if pattern and pattern in file:
                                                                            match_path = os.path.join(search_dir, file)
                                                                            if os.path.isfile(match_path):
                                                                                pdf_path = match_path
                                                                                print(f"DEBUG: Encontrado PDF por patrón '{pattern}': {pdf_path}")
                                                                                found = True
                                                                                break
                                                                    if found:
                                                                        break
                                                        except Exception as dir_err:
                                                            print(f"DEBUG: Error al listar archivos en {search_dir}: {dir_err}")
                                                    if found:
                                                        break
                                            except Exception as e:
                                                print(f"DEBUG: Error buscando PDFs por patrón: {e}")
                                                traceback.print_exc()
                else:
                    pdf_path = ""
                
                # Continuamos con el flujo normal, verificando si pdf_path tiene contenido
                if pdf_path:
                    # Verificar si el archivo existe
                    if os.path.exists(pdf_path):
                        if os.path.isfile(pdf_path):
                            try:
                                with open(pdf_path, 'rb') as f:
                                    pdf_bytes = f.read()
                                # Verificación más robusta del formato PDF
                                is_valid_pdf = False
                                if pdf_bytes:
                                    # Verificar si comienza con la firma de PDF
                                    if pdf_bytes.startswith(b"%PDF"):
                                        is_valid_pdf = True
                                    # Verificar si hay contenido de PDF en los primeros bytes (algunos PDFs pueden tener bytes adicionales al inicio)
                                    elif b"%PDF" in pdf_bytes[:1024]:
                                        print(f"DEBUG: PDF con formato inusual pero detectada firma PDF")
                                        is_valid_pdf = True
                                        
                                if is_valid_pdf:
                                    fname = f"{fname_base}.pdf"
                                    print(f"DEBUG: Leyendo PDF existente ({len(pdf_bytes)} bytes). Descargando como {fname}")
                                    try:
                                        yield rx.download(data=pdf_bytes, filename=fname)
                                        print(f"DEBUG: Descarga iniciada correctamente para {fname}")
                                        return
                                    except Exception as e:
                                        print(f"ERROR: Error durante la descarga del PDF: {e}")
                                        traceback.print_exc()
                                        # Intentar con alternativa de renderizado
                                        try:
                                            print("DEBUG: Intentando abrir PDF en nueva ventana...")
                                            import base64
                                            pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')
                                            data_url = f"data:application/pdf;base64,{pdf_b64}"
                                            yield rx.window_open(data_url, "Cuestionario PDF")
                                            print(f"DEBUG: PDF abierto en nueva ventana")
                                            return
                                        except Exception as e2:
                                            print(f"ERROR: No se pudo abrir el PDF en ventana: {e2}")
                                            # Continuamos con generación de HTML como último recurso
                                else:
                                    print(f"WARN: El archivo existe pero no es un PDF válido: {pdf_path}")
                                    # Intentar generar PDF alternativo
                                    print(f"DEBUG: Intentando generar HTML como alternativa")
                            except Exception as e:
                                print(f"WARN: Error leyendo PDF existente: {e}")
                                traceback.print_exc()  # Añadir traza completa para mejor diagnóstico
                        else:
                            print(f"WARN: La ruta existe pero no es un archivo: {pdf_path}")
                    else:
                        print(f"WARN: No se encontró el archivo PDF en la ruta: {pdf_path}")
                        
                        # Intentar buscar en rutas alternativas
                        try:
                            # Verificar si hay archivos PDF en el directorio actual que coincidan con el nombre base
                            current_dir = os.getcwd()
                            print(f"DEBUG: Buscando PDFs en el directorio actual: {current_dir}")
                            
                            for file in os.listdir(current_dir):
                                if file.endswith('.pdf') and os.path.isfile(os.path.join(current_dir, file)):
                                    print(f"DEBUG: Encontrado posible PDF alternativo: {file}")
                                    
                            # Intentar generar un nuevo PDF como último recurso
                            print(f"DEBUG: Intentando generar un nuevo PDF como último recurso")
                            if hasattr(CuestionarioState, "generar_pdf") and callable(getattr(CuestionarioState, "generar_pdf")):
                                try:
                                    print(f"DEBUG: Llamando a CuestionarioState.generar_pdf()")
                                    async for _ in CuestionarioState.generar_pdf():
                                        pass
                                    
                                    # Volver a intentar con la URL actualizada
                                    if hasattr(CuestionarioState, "cuestionario_pdf_url"):
                                        nueva_pdf_url = get_safe_var_value(CuestionarioState.cuestionario_pdf_url, "")
                                        if nueva_pdf_url and nueva_pdf_url != pdf_url:
                                            print(f"DEBUG: Nueva URL de PDF generada: {nueva_pdf_url}")
                                            # Limpiar la URL y verificar si existe el archivo
                                            clean_url = nueva_pdf_url.split('?')[0]
                                            nueva_pdf_path = clean_url.lstrip('/')
                                            
                                            # Verificar si existe el archivo
                                            found_pdf = False
                                            if os.path.exists(nueva_pdf_path) and os.path.isfile(nueva_pdf_path):
                                                print(f"DEBUG: Nuevo PDF encontrado en: {nueva_pdf_path}")
                                                pdf_path = nueva_pdf_path
                                                found_pdf = True
                                                
                                            # Si no lo encontramos directamente, buscar por nombre de archivo
                                            if not found_pdf:
                                                print(f"DEBUG: Buscando archivo recién generado por nombre...")
                                                pdf_basename = os.path.basename(nueva_pdf_path)
                                                for search_dir in [".", "assets/pdfs", ".web/public/assets/pdfs", "/tmp"]:
                                                    if os.path.exists(search_dir):
                                                        for file in os.listdir(search_dir):
                                                            if file == pdf_basename:
                                                                pdf_path = os.path.join(search_dir, file)
                                                                print(f"DEBUG: Archivo encontrado en: {pdf_path}")
                                                                found_pdf = True
                                                                break
                                                    if found_pdf:
                                                        break
                                except Exception as e:
                                    print(f"DEBUG: Error al intentar generar nuevo PDF: {e}")
                                    traceback.print_exc()
                                    
                        except Exception as e:
                            print(f"DEBUG: Error al intentar listar archivos PDF alternativos: {e}")
            
            # Si no hay PDF o falló la lectura, generamos HTML con las preguntas
            print(f"DEBUG: No se encontró o no se pudo leer un PDF válido. Generando HTML como alternativa...")
            preguntas_html = ""
            
            # Usar nuestra función de utilidad para convertir la lista reactiva
            preguntas_lista = get_safe_var_list(CuestionarioState.cuestionario_preguntas, [])
            
            # Ahora iteramos sobre la lista Python estándar
            print(f"DEBUG: Generando HTML para {len(preguntas_lista)} preguntas")
            for i, pregunta in enumerate(preguntas_lista):
                # Asegurarnos de extraer correctamente los valores usando get con valores por defecto
                pregunta_texto = str(pregunta.get("pregunta", f"Pregunta {i+1}"))
                explicacion = str(pregunta.get("explicacion", ""))
                
                # Manejar diferentes formatos de respuesta correcta
                if "correcta" in pregunta:
                    correcta = str(pregunta.get("correcta", ""))
                elif "correctas" in pregunta and isinstance(pregunta.get("correctas"), list):
                    # Si es una lista de respuestas correctas (selección múltiple)
                    correctas_lista = pregunta.get("correctas", [])
                    correcta = ", ".join([str(c) for c in correctas_lista]) if correctas_lista else ""
                else:
                    correcta = ""
                
                # Agregar la entrada de HTML para esta pregunta
                preguntas_html += f"""
                <div class="pregunta">
                    <h3>{i+1}. {pregunta_texto}</h3>
                    <div class="respuesta">Respuesta: {correcta}</div>
                    {f'<div class="explicacion">Explicación: {explicacion}</div>' if explicacion else ''}
                </div>
                """
            
            # Generar fecha actual para el footer
            fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Si no hay preguntas en el HTML, agregar un mensaje informativo
            if not preguntas_html.strip():
                preguntas_html = """
                <div class="mensaje-info">
                    <p>No se encontraron preguntas para este cuestionario.</p>
                    <p>Por favor, genera primero un cuestionario en la sección correspondiente.</p>
                </div>
                """
                print("DEBUG: No hay preguntas para incluir en el HTML")
            
            # Generar el HTML completo con estilos mejorados
            html_content = f"""<!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Cuestionario: {s_tema}</title>
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Arial, sans-serif; 
                        margin: 0; 
                        padding: 40px; 
                        line-height: 1.6; 
                        color: #333;
                        background-color: #f9f9f9;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 0 auto;
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    h1 {{ 
                        color: #2563eb; 
                        margin-top: 0;
                        padding-bottom: 10px;
                        border-bottom: 2px solid #e5e7eb;
                    }}
                    h2 {{ color: #4b5563; margin-top: 30px; }}
                    h3 {{ margin-bottom: 15px; }}
                    .pregunta {{ 
                        background-color: #f3f4f6; 
                        padding: 20px; 
                        border-radius: 8px; 
                        margin-bottom: 25px;
                        border-left: 4px solid #2563eb;
                    }}
                    .pregunta h3 {{ margin-top: 0; color: #1e40af; }}
                    .respuesta {{ 
                        margin-top: 15px; 
                        font-weight: bold;
                        background-color: #edf7ed;
                        padding: 10px;
                        border-radius: 5px;
                     }}
                    .explicacion {{ 
                        margin-top: 15px; 
                        font-style: italic; 
                        color: #4b5563;
                        padding: 10px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                    }}
                    .mensaje-info {{ 
                        background-color: #ffedd5; 
                        padding: 20px; 
                        border-radius: 8px; 
                        border-left: 4px solid #f97316; 
                    }}
                    hr {{ 
                        border: none; 
                        height: 1px; 
                        background-color: #e5e7eb;
                        margin: 30px 0;
                    }}
                    footer {{ 
                        margin-top: 30px; 
                        color: #6b7280; 
                        font-size: 0.9em;
                        text-align: center;
                    }}
                    @media print {{
                        body {{ background-color: white; }}
                        .container {{ box-shadow: none; padding: 0; }}
                        .pregunta {{ page-break-inside: avoid; }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Cuestionario: {s_tema}</h1>
                    <h3>Curso: {s_cur} - Libro: {s_lib}</h3>
                    <p>Contiene preguntas generadas para tu estudio</p>
                    <hr>
                    {preguntas_html}
                    <hr>
                    <footer>
                        <p><i>Generado por SMART_STUDENT el {fecha_actual}</i></p>
                    </footer>
                </div>
            </body>
            </html>"""
            
            print(f"DEBUG: HTML generado con {len(preguntas_html)} caracteres de preguntas")
            fname = f"{fname_base}.html"
            print(f"DEBUG: Descargando cuestionario como HTML: {fname}")
            
            # Vamos a intentar tres métodos diferentes para asegurar que el usuario reciba el contenido
            download_success = False
            
            # Método 1: Descarga directa con rx.download
            try:
                print(f"DEBUG: Intentando descarga directa con rx.download...")
                yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)
                print(f"DEBUG: Descarga HTML iniciada correctamente para {fname}")
                download_success = True
            except Exception as e:
                print(f"ERROR: Falló descarga directa: {e}")
                traceback.print_exc()
            
            # Método 2: Abrir en una nueva ventana con data URL (si falló el método 1)
            if not download_success:
                try:
                    print(f"DEBUG: Intentando abrir HTML en nueva ventana con data URL...")
                    import base64
                    html_b64 = base64.b64encode(html_content.encode("utf-8", errors='replace')).decode('ascii')
                    data_url = f"data:text/html;base64,{html_b64}"
                    yield rx.window_open(data_url, "Cuestionario HTML")
                    print(f"DEBUG: HTML abierto en nueva ventana")
                    download_success = True
                except Exception as e2:
                    print(f"ERROR: Falló apertura en ventana: {e2}")
                    traceback.print_exc()
            
            # Método 3: Guardar el HTML en un archivo temporal y proporcionar un enlace (si fallaron los métodos anteriores)
            if not download_success:
                try:
                    print(f"DEBUG: Intentando guardar HTML en archivo temporal...")
                    import tempfile
                    import uuid
                    
                    # Crear un identificador único para este archivo
                    file_id = str(uuid.uuid4())[:8]
                    temp_filename = f"cuestionario_{file_id}.html"
                    
                    # Intentar guardar en diferentes ubicaciones
                    save_paths = [
                        os.path.join("assets", "temp", temp_filename),
                        os.path.join(".web", "public", "temp", temp_filename),
                        os.path.join(tempfile.gettempdir(), temp_filename)
                    ]
                    
                    saved_path = None
                    for path in save_paths:
                        try:
                            # Crear el directorio si no existe
                            os.makedirs(os.path.dirname(path), exist_ok=True)
                            
                            # Guardar el archivo HTML
                            with open(path, 'w', encoding='utf-8') as f:
                                f.write(html_content)
                            
                            saved_path = path
                            print(f"DEBUG: HTML guardado en: {saved_path}")
                            break
                        except Exception as save_err:
                            print(f"WARN: No se pudo guardar en {path}: {save_err}")
                    
                    if saved_path:
                        # Mostrar mensaje al usuario con la ubicación del archivo
                        self.error_message_ui = f"El cuestionario se ha guardado como HTML en: {saved_path}"
                        print(f"INFO: HTML guardado en {saved_path}")
                        download_success = True
                except Exception as e3:
                    print(f"ERROR: Falló guardado de archivo: {e3}")
                    traceback.print_exc()
            
            if not download_success:
                self.error_message_ui = "No se pudo descargar el cuestionario. Por favor, inténtelo de nuevo."
                print("ERROR: Todos los métodos de descarga fallaron")

        except Exception as e:
            self.error_message_ui = f"Error al descargar cuestionario: {str(e)}"
            print(f"ERROR DWNLD CUESTIONARIO PDF/HTML: {traceback.format_exc()}")
            # Asegurarnos de terminar el generador
            yield None

    async def descargar_historial(self):
        """Genera y descarga un archivo Excel con el historial de evaluaciones."""
        print("DEBUG: Iniciando descarga del historial...")
        if not self.logged_in_username:
            self.error_message_ui = "Error: Debes iniciar sesión para descargar el historial"
            yield
            return
            
        # Primero nos aseguramos de tener el historial actualizado
        async for _ in self.load_stats():
            pass
        
        if not self.stats_history:
            self.error_message_ui = "No hay historial de evaluaciones para descargar"
            yield
            return
            
        try:
            # Importamos pandas para crear el archivo Excel
            import pandas as pd
            import io
            
            # Preparamos los datos para el DataFrame
            data = []
            for evaluacion in self.stats_history:
                row = {
                    'Fecha': evaluacion.get('fecha', ''),
                    'Libro': evaluacion.get('libro', ''),
                    'Tema': evaluacion.get('tema', ''),
                    'Calificación': evaluacion.get('calificacion', evaluacion.get('nota', 0)),
                    'Respuestas Correctas': evaluacion.get('respuestas_correctas', 0),
                    'Total Preguntas': evaluacion.get('total_preguntas', 0)
                }
                data.append(row)
                
            # Crear DataFrame con pandas
            df = pd.DataFrame(data)
            
            # Crear buffer en memoria para el archivo Excel
            output = io.BytesIO()
            
            # Crear un ExcelWriter con opciones de formato
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Historial de Evaluaciones', index=False)
                
                # Formateo automático del ancho de las columnas
                worksheet = writer.sheets['Historial de Evaluaciones']
                for i, col in enumerate(df.columns):
                    # Establecer el ancho basado en la longitud máxima en la columna
                    max_length = max(df[col].astype(str).map(len).max(), len(col)) + 3
                    worksheet.column_dimensions[chr(65 + i)].width = max_length
            
            # Obtener los bytes del archivo Excel
            excel_data = output.getvalue()
            
            # Generar el enlace de descarga con extensión xlsx
            filename = f"historial_evaluaciones_{self.logged_in_username}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            
            # Devolver contenido del Excel para descarga
            yield rx.download(
                data=excel_data,
                filename=filename
            )
        except Exception as e:
            print(f"ERROR: No se pudo generar el archivo CSV: {e}", file=sys.stderr)
            traceback.print_exc()
            self.error_message_ui = f"Error al generar el archivo: {str(e)}"
            yield

    def open_contact_form(self):
        """Abre el formulario de contacto o redirige al correo de soporte."""
        # En una implementación completa, esto mostraría un modal con un formulario de contacto
        # Por ahora, simplemente abrimos el cliente de correo del usuario
        print("DEBUG: Abriendo formulario de contacto o cliente de correo")
        import webbrowser
        try:
            webbrowser.open("mailto:support@smartstudent.cl?subject=Consulta%20desde%20SMART%20STUDENT")
        except Exception as e:
            self.error_message_ui = "No se pudo abrir el cliente de correo. Por favor, envía un correo a support@smartstudent.cl"
            print(f"ERROR: No se pudo abrir el cliente de correo: {e}")
        yield

    def set_ayuda_search_query(self, query: str):
        """Establece la consulta de búsqueda para la pestaña de ayuda."""
        if not isinstance(query, str):
            return
        self.ayuda_search_query = query
        yield
    
    def repasar_evaluacion_y_ir(self, curso: str, libro: str, tema: str):
        """Navega a la pestaña de evaluaciones con los datos de una evaluación previa."""
        print(f"DEBUG: Repasando evaluación - Curso: {curso}, Libro: {libro}, Tema: {tema}")
        if not curso or not libro or not tema:
            self.error_message_ui = "Faltan datos para repasar esta evaluación"
            yield
            return
            
        # Establecer los valores seleccionados
        self.selected_curso = curso
        self.selected_libro = libro
        self.selected_tema = tema
        
        # Ir a la pestaña de evaluación
        self.active_tab = "evaluacion"
        yield

# --- FIN CLASE AppState ---
