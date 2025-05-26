import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import reflex as rx
from mi_app_estudio.evaluaciones import EvaluationState

def test_review_colors():
    """Analiza el código para verificar los colores de revisión en las evaluaciones."""
    print("\n=== Verificación de colores en revisión de evaluaciones ===")
    
    # Leer el archivo de la interfaz principal
    with open('/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py', 'r') as f:
        func_code = f.read()
    
    # Buscar patrones de color para respuestas correctas/incorrectas
    correct_pattern = "'¡Respuesta correcta!'"
    incorrect_pattern = "'Respuesta incorrecta'"
    
    # Buscar patrones más específicos con el color
    correct_green_count = func_code.count("'¡Respuesta correcta!',\n                                                    color=\"green.500\"")
    incorrect_red_count = func_code.count("'Respuesta incorrecta',\n                                                    color=\"red.500\"")
    
    # También buscar con comillas dobles
    correct_green_count += func_code.count("\"¡Respuesta correcta!\",\n                                                    color=\"green.500\"")
    incorrect_red_count += func_code.count("\"Respuesta incorrecta\",\n                                                    color=\"red.500\"")
    
    # Caso alternativo sin salto de línea
    correct_green_count += func_code.count("'¡Respuesta correcta!', color=\"green.500\"")
    incorrect_red_count += func_code.count("'Respuesta incorrecta', color=\"red.500\"")
    correct_green_count += func_code.count("\"¡Respuesta correcta!\", color=\"green.500\"")
    incorrect_red_count += func_code.count("\"Respuesta incorrecta\", color=\"red.500\"")
    
    print(f"- Instancias de respuestas correctas con color verde: {correct_green_count}")
    print(f"- Instancias de respuestas incorrectas con color rojo: {incorrect_red_count}")
    
    # Verificar todas las apariciones de los textos
    correct_total = func_code.count("'¡Respuesta correcta!'") + func_code.count("\"¡Respuesta correcta!\"")
    incorrect_total = func_code.count("'Respuesta incorrecta'") + func_code.count("\"Respuesta incorrecta\"")
    
    print(f"- Total de apariciones de respuesta correcta: {correct_total}")
    print(f"- Total de apariciones de respuesta incorrecta: {incorrect_total}")
    
    # Mostrar líneas donde aparecen respuestas sin color
    found_issues = False
    lines = func_code.split('\n')
    for i, line in enumerate(lines):
        if "¡Respuesta correcta!" in line and "green.500" not in line:
            print(f"\n⚠️ Línea {i+1}: Respuesta correcta sin color verde:")
            print(f"  {line.strip()}")
            found_issues = True
        if "Respuesta incorrecta" in line and "red.500" not in line:
            print(f"\n⚠️ Línea {i+1}: Respuesta incorrecta sin color rojo:")
            print(f"  {line.strip()}")
            found_issues = True
    
    if not found_issues:
        print("\n✅ No se encontraron problemas específicos en el código.")
    
    # Sugerencias para corregir el problema
    print("\n🔧 Sugerencia de corrección:")
    print("  Asegurarse de que cada aparición de los textos tenga los colores correctos:")
    print("  - Para respuestas correctas: color=\"green.500\"")
    print("  - Para respuestas incorrectas: color=\"red.500\"")

if __name__ == "__main__":
    test_review_colors()