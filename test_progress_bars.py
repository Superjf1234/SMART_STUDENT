#!/usr/bin/env python3
"""
Test script para verificar el funcionamiento de las barras de progreso en la pestaña de perfil.
Este script crea evaluaciones de prueba para cada materia y luego carga el perfil para
verificar que las barras de progreso muestren los valores correctos.
"""

import os
import sys
import sqlite3
from datetime import datetime

# Asegurar que el directorio de trabajo es el correcto
if not os.path.exists("rxconfig.py"):
    print("ERROR: Este script debe ejecutarse desde el directorio raíz del proyecto.")
    sys.exit(1)

# Conexión a la base de datos
def get_db_connection():
    try:
        conn = sqlite3.connect("student_stats.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"ERROR: No se pudo conectar a la base de datos: {e}")
        return None

# Limpiar evaluaciones de usuario de prueba
def limpiar_evaluaciones_usuario(username):
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evaluacion_historial WHERE username = ?", (username,))
            print(f"INFO: Eliminadas las evaluaciones previas del usuario {username}")
            return True
    except Exception as e:
        print(f"ERROR: No se pudieron eliminar las evaluaciones: {e}")
        return False
    finally:
        conn.close()

# Crear evaluaciones de prueba
def crear_evaluaciones_prueba(username):
    conn = get_db_connection()
    if not conn:
        return False
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Evaluaciones para cada materia
    evaluaciones = [
        # Matemáticas - 85%
        {
            "curso": "1ro Medio",
            "libro": "Matemáticas Avanzada",
            "tema": "Álgebra y Ecuaciones",
            "nota": 6.1,  # Escala 1-7 (sistema chileno)
            "metadata": "Correctas: 17/20"  # 85%
        },
        # Ciencias - 90%
        {
            "curso": "2do Medio",
            "libro": "Biología Celular",
            "tema": "La Célula y sus Funciones",
            "nota": 6.4,  # Escala 1-7 (sistema chileno)
            "metadata": "Correctas: 18/20"  # 90%
        },
        # Historia - 75%
        {
            "curso": "3ro Medio",
            "libro": "Historia Universal",
            "tema": "La Edad Media y el Feudalismo",
            "nota": 5.5,  # Escala 1-7 (sistema chileno)
            "metadata": "Correctas: 15/20"  # 75%
        },
        # Lenguaje - 80%
        {
            "curso": "4to Medio",
            "libro": "Lenguaje y Literatura",
            "tema": "Análisis Narrativo",
            "nota": 5.8,  # Escala 1-7 (sistema chileno)
            "metadata": "Correctas: 16/20"  # 80%
        }
    ]
    
    try:
        with conn:
            cursor = conn.cursor()
            for eval_data in evaluaciones:
                cursor.execute(
                    """
                    INSERT INTO evaluacion_historial 
                    (username, curso, libro, tema, fecha, nota, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        username,
                        eval_data["curso"],
                        eval_data["libro"],
                        eval_data["tema"],
                        fecha_actual,
                        eval_data["nota"],
                        eval_data["metadata"]
                    )
                )
            
            print(f"INFO: Creadas {len(evaluaciones)} evaluaciones de prueba para el usuario {username}")
            return True
    except Exception as e:
        print(f"ERROR: No se pudieron crear las evaluaciones de prueba: {e}")
        return False
    finally:
        conn.close()

# Verificar historial de evaluaciones
def verificar_historial(username):
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, curso, libro, tema, fecha, nota, metadata
                FROM evaluacion_historial
                WHERE username = ?
                ORDER BY fecha DESC
                """, 
                (username,)
            )
            
            rows = cursor.fetchall()
            
            if not rows:
                print(f"El usuario {username} no tiene evaluaciones")
                return
            
            print(f"\nEvaluaciones del usuario {username}:")
            print("-" * 80)
            for row in rows:
                print(f"ID: {row['id']}")
                print(f"Curso: {row['curso']}")
                print(f"Libro: {row['libro']}")
                print(f"Tema: {row['tema']}")
                print(f"Fecha: {row['fecha']}")
                print(f"Nota: {row['nota']}")
                
                # Calcular porcentaje a partir de la nota
                nota = float(row['nota'])
                porcentaje = round(((nota - 1.0) / 6.0) * 100)
                
                # Extraer información de respuestas correctas de metadata
                respuestas_correctas = ""
                if row['metadata'] and "Correctas:" in row['metadata']:
                    respuestas_correctas = row['metadata']
                
                print(f"Porcentaje: {porcentaje}%")
                print(f"Metadata: {respuestas_correctas}")
                print("-" * 80)
    except Exception as e:
        print(f"ERROR: No se pudo verificar el historial: {e}")
    finally:
        conn.close()

def main():
    # Usuario de prueba
    test_user = "felipe"
    
    print(f"Preparando prueba de barras de progreso para el usuario: {test_user}")
    
    # Limpiar evaluaciones previas
    limpiar_evaluaciones_usuario(test_user)
    
    # Crear evaluaciones de prueba
    crear_evaluaciones_prueba(test_user)
    
    # Verificar historial
    verificar_historial(test_user)
    
    print("\nPrueba completada. Ahora puedes iniciar la aplicación y verificar")
    print("las barras de progreso en la pestaña de perfil.")
    print("\nValores esperados:")
    print("- Matemáticas: 85%")
    print("- Ciencias: 90%")
    print("- Historia: 75%")
    print("- Lenguaje: 80%")
    print("\nPara iniciar la aplicación, ejecuta:")
    print("python main.py run")

if __name__ == "__main__":
    main()
