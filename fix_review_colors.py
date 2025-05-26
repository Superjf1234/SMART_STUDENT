"""
Script para corregir los colores en el modo de revisión de evaluaciones.
"""

import re

# Ruta del archivo a modificar
file_path = '/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py'

# Leer el contenido del archivo
with open(file_path, 'r') as file:
    content = file.read()

# Patrones para reemplazar
# Para respuestas correctas
correct_pattern = r'rx\.text\(\s*"¡Respuesta correcta!",\s*color="green\.500",\s*font_weight="bold",\s*style=\{"color": "green"\}'
correct_replacement = r'rx.text(\n                                                    "¡Respuesta correcta!",\n                                                    color="green.500",\n                                                    font_weight="bold",\n                                                    style={"color": "#22C55E", "fontSize": "1.1em", "textShadow": "0px 0px 1px #000"}'

# Para respuestas incorrectas
incorrect_pattern = r'rx\.text\(\s*"Respuesta incorrecta",\s*color="red\.500",\s*font_weight="bold",\s*style=\{"color": "red"\}'
incorrect_replacement = r'rx.text(\n                                                    "Respuesta incorrecta",\n                                                    color="red.500",\n                                                    font_weight="bold",\n                                                    style={"color": "#E53E3E", "fontSize": "1.1em", "textShadow": "0px 0px 1px #000"}'

# Aplicar los reemplazos
modified_content = re.sub(correct_pattern, correct_replacement, content)
modified_content = re.sub(incorrect_pattern, incorrect_replacement, modified_content)

# Guardar el contenido modificado
with open(file_path, 'w') as file:
    file.write(modified_content)

print("Se han aplicado las modificaciones para corregir los colores en el modo de revisión.")
