#!/usr/bin/python3

import os
import sys
import sqlite3
from datetime import datetime

# Ruta a la base de datos
DATABASE_FILE = "student_stats.db"

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"ERROR: No se pudo conectar a DB {DATABASE_FILE} - {e}")
        return None

def crear_tabla_si_no_existe():
    """Crea la tabla evaluacion_historial si no existe."""
    conn = get_db_connection()
    if conn:
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
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
                """)
                print("INFO: Tabla evaluacion_historial asegurada.")
                
                # Verificar si la columna metadata existe
                cursor.execute("PRAGMA table_info(evaluacion_historial)")
                columns = cursor.fetchall()
                metadata_exists = False
                
                for column in columns:
                    if column[1] == "metadata":
                        metadata_exists = True
                        break
                
                if not metadata_exists:
                    cursor.execute("ALTER TABLE evaluacion_historial ADD COLUMN metadata TEXT")
                    print("INFO: Columna metadata añadida a evaluacion_historial.")
                else:
                    print("INFO: La columna metadata ya existe.")
        except sqlite3.Error as e:
            print(f"ERROR: No se pudo crear tabla - {e}")

def guardar_evaluacion(username, curso, libro, tema, nota, respuestas_correctas=None, total_preguntas=None):
    """Guarda una evaluación en la base de datos."""
    conn = get_db_connection()
    if conn:
        try:
            metadata = ""
            if respuestas_correctas is not None and total_preguntas is not None:
                metadata = f"Correctas: {respuestas_correctas}/{total_preguntas}"
            
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO evaluacion_historial 
                    (username, curso, libro, tema, fecha, nota, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (username, curso, libro, tema, fecha_actual, nota, metadata)
                )
            print("INFO: Evaluación guardada correctamente.")
            return True
        except sqlite3.Error as e:
            print(f"ERROR: No se pudo guardar evaluación - {e}")
    return False

def obtener_historial(username):
    """Obtiene el historial de evaluaciones de un usuario."""
    conn = get_db_connection()
    historial = []
    if conn:
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM evaluacion_historial WHERE username = ? ORDER BY fecha DESC",
                    (username,)
                )
                rows = cursor.fetchall()
                historial = [dict(row) for row in rows]
                print(f"INFO: Obtenidas {len(historial)} entradas de historial para '{username}'.")
        except sqlite3.Error as e:
            print(f"ERROR: No se pudo obtener historial - {e}")
    return historial

def main():
    """Función principal de prueba."""
    print("Creando tabla si no existe...")
    crear_tabla_si_no_existe()
    
    username = "test_user"
    curso = "8vo Básico"
    libro = "Ciencias Naturales"
    tema = "Sistema respiratorio"
    nota = 6.7
    respuestas_correctas = 8
    total_preguntas = 10
    
    # Guardar evaluación
    print(f"Guardando evaluación para {username}...")
    resultado = guardar_evaluacion(username, curso, libro, tema, nota, respuestas_correctas, total_preguntas)
    
    if not resultado:
        print("ERROR: No se pudo guardar la evaluación.")
        return
    
    # Mostrar historial
    print(f"Recuperando historial para {username}...")
    historial = obtener_historial(username)
    
    if not historial:
        print("ERROR: No se pudo recuperar el historial o está vacío.")
        return
    
    print(f"Se encontraron {len(historial)} registros:")
    for i, evaluacion in enumerate(historial):
        print(f"Evaluación {i+1}:")
        for key, value in evaluacion.items():
            print(f"  - {key}: {value}")
        print("  ---")

if __name__ == "__main__":
    main()
