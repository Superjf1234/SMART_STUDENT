# backend/db_logic.py
import sqlite3
import os
import sys
from datetime import datetime
import traceback
from typing import Dict, Any, List

DATABASE_FILE = "student_stats.db"

# ELIMINADO: logged_in_user = None
# ELIMINADO: def set_current_user(username): ...


def get_db_connection():
    # ... (sin cambios) ...
    try:
        conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(
            f"ERROR (db_logic): No se pudo conectar a DB {DATABASE_FILE} - {e}",
            file=sys.stderr,
        )
        traceback.print_exc()
        return None


def inicializar_db():
    # Inicializar tablas para almacenar datos del usuario
    create_table_query = """
        CREATE TABLE IF NOT EXISTS evaluacion_historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            curso TEXT NOT NULL,
            libro TEXT NOT NULL,
            tema TEXT NOT NULL,
            fecha TEXT NOT NULL,
            nota REAL NOT NULL,
            metadata TEXT
        )
    """
    
    # Tabla para almacenar contadores de usuario (resúmenes y mapas generados)
    create_user_stats_table = """
        CREATE TABLE IF NOT EXISTS user_stats (
            username TEXT PRIMARY KEY,
            resumenes_count INTEGER DEFAULT 0,
            mapas_count INTEGER DEFAULT 0,
            last_login TEXT,
            last_active TEXT
        )
    """
    
    # Verificar si la columna metadata ya existe, y añadirla si no
    check_metadata_query = """
    SELECT COUNT(*) FROM pragma_table_info('evaluacion_historial') WHERE name='metadata'
    """
    
    add_metadata_query = """
    ALTER TABLE evaluacion_historial ADD COLUMN metadata TEXT
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(create_table_query)
                print("INFO (db_logic): Tabla evaluacion_historial asegurada.")
                
                # Crear tabla de estadísticas de usuario
                cursor.execute(create_user_stats_table)
                print("INFO (db_logic): Tabla user_stats asegurada.")
                
                # Verificar si la columna metadata existe
                cursor.execute(check_metadata_query)
                metadata_exists = cursor.fetchone()[0]
                
                if metadata_exists == 0:
                    try:
                        # Si no existe, añadimos la columna
                        cursor.execute(add_metadata_query)
                        print("INFO (db_logic): Columna metadata añadida a evaluacion_historial.")
                    except sqlite3.Error as column_error:
                        if "duplicate column name" not in str(column_error):
                            print(f"ERROR (db_logic): Error al añadir columna metadata: {column_error}")
        except sqlite3.Error as e:
            print(
                f"ERROR (db_logic): No se pudo crear/verificar tabla - {e}",
                file=sys.stderr,
            )
            traceback.print_exc()
        finally:
            conn.close()


# --- MODIFICADA ---
def guardar_resultado_evaluacion(username, curso, libro, tema, nota, respuestas_correctas=None, total_preguntas=None):
    """Guarda evaluación para un usuario específico."""
    if not username:  # Verificar que se pasó el username
        print(
            "ERROR (db_logic): Intento de guardar evaluación sin username.",
            file=sys.stderr,
        )
        return False

    try:
        nota_float = float(nota)
    except (ValueError, TypeError):
        print(
            f"ERROR (db_logic): Intento de guardar nota inválida ({nota}).",
            file=sys.stderr,
        )
        return False

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Crear metadata con información de respuestas correctas
    metadata = ""
    if respuestas_correctas is not None and total_preguntas is not None:
        metadata = f"Correctas: {respuestas_correctas}/{total_preguntas}"
    
    # Actualizar query para incluir metadata
    insert_query = """
        INSERT INTO evaluacion_historial (username, curso, libro, tema, fecha, nota, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    conn = get_db_connection()
    success = False
    if conn:
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    insert_query,
                    (
                        username,
                        curso,
                        libro,
                        tema,
                        fecha_actual,
                        nota_float,
                        metadata,
                    ),  # Usar username parámetro
                )
                print(
                    f"INFO (db_logic): Evaluación guardada para '{username}' (Tema: {tema}, Nota: {nota_float})."
                )
                success = True
        except sqlite3.Error as e:
            print(
                f"ERROR (db_logic): No se pudo guardar evaluación en BD - {e}",
                file=sys.stderr,
            )
            traceback.print_exc()
        except Exception as e_gen:
            print(
                f"ERROR (db_logic): Error inesperado guardando evaluación - {e_gen}",
                file=sys.stderr,
            )
            traceback.print_exc()
        finally:
            conn.close()
    return success


# --- MODIFICADA ---
def obtener_historial(username):
    """Obtiene historial para un usuario específico."""
    if not username:
        print(
            "ERROR (db_logic): Intento de obtener historial sin username.",
            file=sys.stderr,
        )
        return []  # Retornar lista vacía si no hay usuario

    select_query = """
        SELECT id, curso, libro, tema, fecha, nota, metadata
        FROM evaluacion_historial
        WHERE username = ?
        ORDER BY fecha DESC
    """
    conn = get_db_connection()
    historial = []
    if conn:
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(select_query, (username,))  # Usar username parámetro
                rows = cursor.fetchall()
                historial = [
                    dict(row) for row in rows
                ]  # Convertir a dict para fácil uso en Reflex
                print(
                    f"INFO (db_logic): Obtenidas {len(historial)} entradas de historial para '{username}'."
                )
        except sqlite3.Error as e:
            print(
                f"ERROR (db_logic): No se pudo obtener historial de BD - {e}",
                file=sys.stderr,
            )
            traceback.print_exc()
        except Exception as e_gen:
            print(
                f"ERROR (db_logic): Error inesperado obteniendo historial - {e_gen}",
                file=sys.stderr,
            )
            traceback.print_exc()
        finally:
            conn.close()
    return historial


def obtener_estadisticas_usuario(username: str) -> list[Dict[str, Any]]:
    """Obtiene estadísticas de evaluaciones para un usuario específico.
    Devuelve una lista con el historial completo de evaluaciones."""
    if not username:
        print(
            "ERROR (db_logic): Intento de obtener estadísticas sin username.",
            file=sys.stderr,
        )
        return []
        
    select_query = """
        SELECT curso, libro, tema, fecha, nota
        FROM evaluacion_historial
        WHERE username = ?
        ORDER BY fecha DESC
    """
    
    conn = get_db_connection()
    if not conn:
        return []
        
    historial = []
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(select_query, (username,))
            
            rows = cursor.fetchall()
            for row in rows:
                fecha_str = row["fecha"]
                try:
                    # Convertir de formato ISO a formato más legible
                    fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                    fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                except:
                    fecha_formateada = fecha_str
                    
                historial.append({
                    "curso": row["curso"],
                    "libro": row["libro"],
                    "tema": row["tema"],
                    "puntuacion": row["nota"],
                    "fecha": fecha_formateada
                })
                
            print(f"INFO (db_logic): Obtenidos {len(historial)} registros de evaluación para '{username}'.")
    except Exception as e:
        print(
            f"ERROR (db_logic): No se pudo obtener estadísticas de BD - {e}",
            file=sys.stderr,
        )
        traceback.print_exc()
    finally:
        conn.close()
        
    return historial


def eliminar_historial_evaluaciones(username: str) -> bool:
    """Elimina todo el historial de evaluaciones para un usuario específico.
    
    Args:
        username (str): El nombre de usuario cuyo historial se eliminará.
        
    Returns:
        bool: True si la operación tuvo éxito, False en caso contrario.
    """
    if not username:
        print(
            "ERROR (db_logic): Intento de eliminar historial sin username.",
            file=sys.stderr,
        )
        return False
        
    delete_query = """
        DELETE FROM evaluacion_historial
        WHERE username = ?
    """
    
    conn = get_db_connection()
    if not conn:
        return False
        
    success = False
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(delete_query, (username,))
            
            if cursor.rowcount > 0:
                print(f"INFO (db_logic): Se eliminaron {cursor.rowcount} registros de evaluación para '{username}'.")
            else:
                print(f"INFO (db_logic): No se encontraron registros para eliminar para el usuario '{username}'.")
            
            success = True
    except Exception as e:
        print(
            f"ERROR (db_logic): No se pudo eliminar historial de BD - {e}",
            file=sys.stderr,
        )
        traceback.print_exc()
    finally:
        conn.close()
        
    return success


# --- Funciones para gestionar estadísticas de usuario ---

def get_user_stats(username):
    """
    Obtiene las estadísticas de usuario: contadores de resúmenes y mapas.
    
    Args:
        username: Nombre del usuario
        
    Returns:
        dict: Diccionario con las estadísticas (mapas_count, resumenes_count)
    """
    if not username:
        print("ERROR (db_logic): Intento de obtener estadísticas sin username.")
        return {"resumenes_count": 0, "mapas_count": 0}
    
    select_query = """
        SELECT resumenes_count, mapas_count
        FROM user_stats
        WHERE username = ?
    """
    
    conn = get_db_connection()
    if not conn:
        return {"resumenes_count": 0, "mapas_count": 0}
    
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(select_query, (username,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "resumenes_count": row["resumenes_count"],
                    "mapas_count": row["mapas_count"]
                }
            else:
                # Si no existe el usuario, crear un registro con valores iniciales
                insert_query = """
                    INSERT OR IGNORE INTO user_stats (username, resumenes_count, mapas_count, last_login, last_active)
                    VALUES (?, 0, 0, ?, ?)
                """
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(insert_query, (username, fecha_actual, fecha_actual))
                
                print(f"INFO (db_logic): Creado nuevo registro de stats para usuario '{username}'")
                return {"resumenes_count": 0, "mapas_count": 0}
    except Exception as e:
        print(f"ERROR (db_logic): Error al obtener estadísticas de usuario: {e}")
        traceback.print_exc()
        return {"resumenes_count": 0, "mapas_count": 0}
    finally:
        conn.close()

def update_user_stats(username, resumenes_count=None, mapas_count=None):
    """
    Actualiza las estadísticas de usuario (resúmenes y mapas generados).
    
    Args:
        username: Nombre del usuario
        resumenes_count: Si se proporciona, actualiza el contador de resúmenes
        mapas_count: Si se proporciona, actualiza el contador de mapas
        
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    if not username:
        print("ERROR (db_logic): Intento de actualizar estadísticas sin username.")
        return False
    
    # Si no hay nada que actualizar, salir
    if resumenes_count is None and mapas_count is None:
        return True
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Verificar primero si el usuario existe
    check_query = "SELECT COUNT(*) FROM user_stats WHERE username = ?"
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(check_query, (username,))
            user_exists = cursor.fetchone()[0] > 0
            
            if user_exists:
                # Construir la consulta de actualización dinámicamente
                update_parts = []
                params = []
                
                if resumenes_count is not None:
                    update_parts.append("resumenes_count = ?")
                    params.append(resumenes_count)
                
                if mapas_count is not None:
                    update_parts.append("mapas_count = ?")
                    params.append(mapas_count)
                
                # Siempre actualizar last_active
                update_parts.append("last_active = ?")
                params.append(fecha_actual)
                
                # Añadir username al final de los parámetros
                params.append(username)
                
                update_query = f"""
                    UPDATE user_stats
                    SET {', '.join(update_parts)}
                    WHERE username = ?
                """
                
                cursor.execute(update_query, params)
                print(f"INFO (db_logic): Actualizadas estadísticas para '{username}'")
            else:
                # Crear un nuevo registro si no existe
                insert_query = """
                    INSERT INTO user_stats (username, resumenes_count, mapas_count, last_login, last_active)
                    VALUES (?, ?, ?, ?, ?)
                """
                
                # Usar 0 como valor predeterminado si no se proporciona
                r_count = resumenes_count if resumenes_count is not None else 0
                m_count = mapas_count if mapas_count is not None else 0
                
                cursor.execute(insert_query, (username, r_count, m_count, fecha_actual, fecha_actual))
                print(f"INFO (db_logic): Creado nuevo registro de stats para '{username}'")
            
            return True
    except Exception as e:
        print(f"ERROR (db_logic): Error al actualizar estadísticas de usuario: {e}")
        traceback.print_exc()
        return False
    finally:
        conn.close()

def update_user_login(username):
    """
    Actualiza la fecha de último inicio de sesión del usuario.
    
    Args:
        username: Nombre del usuario
        
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    if not username:
        return False
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Utilizamos UPSERT para insertar o actualizar según sea necesario
    upsert_query = """
        INSERT INTO user_stats (username, last_login, last_active)
        VALUES (?, ?, ?)
        ON CONFLICT(username) 
        DO UPDATE SET last_login = ?, last_active = ?
    """
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(upsert_query, (username, fecha_actual, fecha_actual, fecha_actual, fecha_actual))
            print(f"INFO (db_logic): Actualizada fecha de login para '{username}'")
            return True
    except Exception as e:
        print(f"ERROR (db_logic): Error al actualizar login de usuario: {e}")
        traceback.print_exc()
        return False
    finally:
        conn.close()


# --- Inicialización ---
# Es buena idea llamar a inicializar_db() una vez cuando la aplicación Reflex arranque.
# Puedes hacerlo en tu archivo principal de Reflex (tu_proyecto_web.py) antes de definir la App,
# o podrías tener una función de setup en db_logic.py que sea llamada.
# Por ahora, nos aseguramos que la función exista.
# Si ejecutas este archivo directamente para probar, inicializará:
if __name__ == "__main__":
    print("--- Ejecutando pruebas de db_logic.py ---")
    inicializar_db()
    test_user = "usuario_prueba_web"
    print(f"\nGuardando para {test_user}...")
    guardar_resultado_evaluacion(test_user, "1ro Medio", "Biología", "Célula", 7.0)
    guardar_resultado_evaluacion(test_user, "1ro Medio", "Biología", "Fotosíntesis", 5.5)
    guardar_resultado_evaluacion("otro_usuario", "8vo Básico", "Historia", "Edad Media", 4.0)
    print(f"\nObteniendo historial para {test_user}...")
    historial_test = obtener_historial(test_user)
    if historial_test:
        for item in historial_test:
            print(
                f"  - ID: {item['id']}, Curso: {item['curso']}, Tema: {item['tema']}, Nota: {item['nota']}"
            )
    else:
        print("  (Vacío)")
    print(f"\nObteniendo historial para otro_usuario...")
    historial_otro = obtener_historial("otro_usuario")
    if historial_otro:
        print(f"  - Encontrado: {len(historial_otro)} registro(s).")
    else:
        print("  (Vacío)")
    print("\n--- Pruebas db_logic.py finalizadas ---")
