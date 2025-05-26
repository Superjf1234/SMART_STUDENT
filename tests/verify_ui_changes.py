"""
Script para verificar que los mensajes de respuesta en el modo de revisión 
muestren los colores correctos (verde para correctas, rojo para incorrectas).
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reflex as rx
from mi_app_estudio.evaluaciones import EvaluationState

def verify_styles():
    """Verifica que los estilos CSS se apliquen correctamente en el modo de revisión."""
    print("\n=== Verificación de estilos en el modo de revisión ===")
    
    # Verificar la implementación actual con doble estrategia de coloración
    found_issues = False
    
    # Leer el archivo de la interfaz principal
    with open('/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py', 'r') as f:
        func_code = f.read()
    
    # Verificar que todas las instancias tengan el color adecuado Y el estilo inline
    green_color_count = func_code.count('color="green.500"')
    green_style_count = func_code.count('style={"color": "green"}')
    red_color_count = func_code.count('color="red.500"')
    red_style_count = func_code.count('style={"color": "red"}')
    
    print(f"- Instancias con color='green.500': {green_color_count}")
    print(f"- Instancias con style={{\"color\": \"green\"}}: {green_style_count}")
    print(f"- Instancias con color='red.500': {red_color_count}")
    print(f"- Instancias con style={{\"color\": \"red\"}}: {red_style_count}")
    
    # Verificar que cada texto de respuesta tenga ambos atributos
    correct_patterns = [
        '"¡Respuesta correcta!",\n                                                    color="green.500",\n                                                    font_weight="bold",\n                                                    style={"color": "green"}'
    ]
    
    incorrect_patterns = [
        '"Respuesta incorrecta",\n                                                    color="red.500",\n                                                    font_weight="bold",\n                                                    style={"color": "red"}'
    ]
    
    # Verificar patrones correctos
    for pattern in correct_patterns:
        count = func_code.count(pattern)
        print(f"- Patrón correcto con ambos atributos encontrado {count} veces")
        if count < 3:  # Esperamos al menos 3 instancias
            found_issues = True
            print(f"  ⚠️ Esperábamos 3 instancias, pero encontramos {count}")
    
    # Verificar patrones incorrectos
    for pattern in incorrect_patterns:
        count = func_code.count(pattern)
        print(f"- Patrón incorrecto con ambos atributos encontrado {count} veces")
        if count < 3:  # Esperamos al menos 3 instancias
            found_issues = True
            print(f"  ⚠️ Esperábamos 3 instancias, pero encontramos {count}")
    
    print("\n=== Resultado de la verificación ===")
    if found_issues:
        print("⚠️ Se detectaron problemas en la implementación de estilos")
    else:
        print("✅ Los estilos se están aplicando correctamente")
    
    print("\nLos siguientes elementos se están utilizando para controlar el color:")
    print("1. color='green.500'/'red.500' - Estilo de Reflex/Chakra UI")
    print("2. style={'color': 'green'/'red'} - Estilo CSS inline directo")
    
    print("\nEsta implementación redundante debería solucionar problemas de visualización en cualquier navegador.")

if __name__ == "__main__":
    verify_styles()