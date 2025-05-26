"""
Script para aplicar las correcciones necesarias a los mensajes de revisión.
"""
import re

# Ruta del archivo a modificar
file_path = '/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py'

# Leer el contenido del archivo
with open(file_path, 'r') as file:
    content = file.read()

# Reemplazar todas las instancias de mensajes de respuesta con los componentes optimizados
content = content.replace(
    'rx.cond(\n                                                EvaluationState.is_current_question_correct_in_review,\n                                                rx.text(\n                                                    "¡Respuesta correcta!",\n                                                    color="green.500",\n                                                    font_weight="bold",\n                                                    style={"color": "#22C55E", "fontSize": "1.1em", "textShadow": "0px 0px 1px #000"}\n                                                ),\n                                                rx.text(\n                                                    "Respuesta incorrecta",\n                                                    color="red.500",\n                                                    font_weight="bold",\n                                                    style={"color": "#E53E3E", "fontSize": "1.1em", "textShadow": "0px 0px 1px #000"}\n                                                )\n                                            )',
    'rx.cond(\n                                                EvaluationState.is_current_question_correct_in_review,\n                                                mensaje_respuesta_correcta(),\n                                                mensaje_respuesta_incorrecta()\n                                            )'
)

# Guardar el contenido modificado
with open(file_path, 'w') as file:
    file.write(content)

print("Se han aplicado las correcciones a los mensajes de revisión.")
print("Ahora se utilizan componentes HTML optimizados que garantizan la visualización correcta de los colores.")
