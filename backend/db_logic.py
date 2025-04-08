# backend/db_logic.py
import sqlite3
import os
from datetime import datetime
import traceback
import logging

DATABASE_FILE = "student_stats.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"No se pudo conectar a DB {DATABASE_FILE} - {e}")
        traceback.print_exc()
        return None

def inicializar_db():
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
                logging.info("Base de datos inicializada / tabla asegurada.")
        except sqlite3.Error as e:
            logging.error(f"No se pudo crear/verificar tabla - {e}")
            traceback.print_exc()
        finally:
            conn.close()

def guardar_evaluacion(username, curso, libro, tema, nota):
    if not username:
        logging.error("Intento de guardar evaluación sin username.")
        return False

    try:
        nota_float = float(nota)
    except (ValueError, TypeError):
        logging.error(f"Intento de guardar nota inválida ({nota}).")
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
                    ),
                )
                logging.info(f"Evaluación guardada para '{username}' (Tema: {tema}, Nota: {nota_float}).")
                success = True
        except sqlite3.Error as e:
            logging.error(f"No se pudo guardar evaluación en BD - {e}")
            traceback.print_exc()
        except Exception as e_gen:
            logging.error(f"Error inesperado guardando evaluación - {e_gen}")
            traceback.print_exc()
        finally:
            conn.close()
    return success

def obtener_historial(username):
    if not username:
        logging.error("Intento de obtener historial sin username.")
        return []

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
                cursor.execute(select_query, (username,))
                rows = cursor.fetchall()
                historial = [dict(row) for row in rows]
                logging.info(f"Obtenidas {len(historial)} entradas de historial para '{username}'.")
        except sqlite3.Error as e:
            logging.error(f"No se pudo obtener historial de BD - {e}")
            traceback.print_exc()
        except Exception as e_gen:
            logging.error(f"Error inesperado obteniendo historial - {e_gen}")
            traceback.print_exc()
        finally:
            conn.close()
    return historial

if __name__ == "__main__":
    logging.info("--- Ejecutando pruebas de db_logic.py ---")
    inicializar_db()
    test_user = "usuario_prueba_web"
    logging.info(f"\nGuardando para {test_user}...")
    guardar_evaluacion(test_user, "1ro Medio", "Biología", "Célula", 7.0)
    guardar_evaluacion(test_user, "1ro Medio", "Biología", "Fotosíntesis", 5.5)
    guardar_evaluacion("otro_usuario", "8vo Básico", "Historia", "Edad Media", 4.0)
    logging.info(f"\nObteniendo historial para {test_user}...")
    historial_test = obtener_historial(test_user)
    if historial_test:
        for item in historial_test:
            logging.info(f"  - ID: {item['id']}, Curso: {item['curso']}, Tema: {item['tema']}, Nota: {item['nota']}")
    else:
        logging.info("  (Vacío)")
    logging.info(f"\nObteniendo historial para otro_usuario...")
    historial_otro = obtener_historial("otro_usuario")
    if historial_otro:
        logging.info(f"  - Encontrado: {len(historial_otro)} registro(s).")
    else:
        logging.info("  (Vacío)")
    logging.info("\n--- Pruebas db_logic.py finalizadas ---")
