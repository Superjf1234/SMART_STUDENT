# backend/db_logic.py
import sqlite3
import os
import sys
from datetime import datetime
import traceback

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
    # ... (sin cambios, pero asegúrate que se llame al inicio de la app Reflex) ...
    create_table_query = """
        CREATE TABLE IF NOT EXISTS evaluacion_historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            curso TEXT NOT NULL,
            libro TEXT NOT NULL,
            tema TEXT NOT NULL,
            fecha TEXT NOT NULL,
            nota REAL NOT NULL
        )
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(create_table_query)
                print("INFO (db_logic): Base de datos inicializada / tabla asegurada.")
        except sqlite3.Error as e:
            print(
                f"ERROR (db_logic): No se pudo crear/verificar tabla - {e}",
                file=sys.stderr,
            )
            traceback.print_exc()
        finally:
            conn.close()


# --- MODIFICADA ---
def guardar_evaluacion(username, curso, libro, tema, nota):
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
    insert_query = """
        INSERT INTO evaluacion_historial (username, curso, libro, tema, fecha, nota)
        VALUES (?, ?, ?, ?, ?, ?)
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
        SELECT id, curso, libro, tema, fecha, nota
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


def obtener_estadisticas_usuario(username: str) -> dict:
    """Obtiene estadísticas de evaluaciones para un usuario específico: total y nota promedio."""
    stats = {"total_evaluaciones": 0, "nota_promedio": 0.0}
    if not username:
        print(
            "ERROR (db_logic): Intento de obtener estadísticas sin username.",
            file=sys.stderr,
        )
        return stats
    conn = get_db_connection()
    if not conn:
        return stats
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as total, AVG(nota) as avg_nota FROM evaluacion_historial WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                stats["total_evaluaciones"] = row["total"] or 0
                stats["nota_promedio"] = float(row["avg_nota"]) if row["avg_nota"] is not None else 0.0
    except Exception as e:
        print(
            f"ERROR (db_logic): No se pudo obtener estadísticas de BD - {e}",
            file=sys.stderr,
        )
    finally:
        conn.close()
    return stats


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
    guardar_evaluacion(test_user, "1ro Medio", "Biología", "Célula", 7.0)
    guardar_evaluacion(test_user, "1ro Medio", "Biología", "Fotosíntesis", 5.5)
    guardar_evaluacion("otro_usuario", "8vo Básico", "Historia", "Edad Media", 4.0)
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
