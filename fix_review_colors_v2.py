"""
Script para corregir los colores en el modo de revisión de evaluaciones
usando componentes personalizados.
"""

import os

# Ruta del archivo a modificar
file_path = '/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py'

# Crear una copia de seguridad del archivo
backup_path = file_path + '.bak_colors'
os.system(f'cp {file_path} {backup_path}')
print(f"Se ha creado una copia de seguridad en {backup_path}")

# Definir el componente de texto personalizado que se agregará al inicio del archivo
custom_component = """
# Componentes personalizados para mensajes de revisión con colores forzados
def correct_answer_text():
    return rx.html("<div style='color: #22C55E; font-weight: bold; font-size: 1.1em; text-shadow: 0px 0px 1px rgba(0,0,0,0.1);'>¡Respuesta correcta!</div>")

def incorrect_answer_text():
    return rx.html("<div style='color: #E53E3E; font-weight: bold; font-size: 1.1em; text-shadow: 0px 0px 1px rgba(0,0,0,0.1);'>Respuesta incorrecta</div>")

"""

# Leer el contenido del archivo
with open(file_path, 'r') as file:
    content = file.readlines()

# Encontrar la línea después de las importaciones para insertar los componentes personalizados
import_end_line = 0
for i, line in enumerate(content):
    if line.startswith('# Constantes globales'):
        import_end_line = i
        break

# Insertar el componente personalizado después de las importaciones
content.insert(import_end_line, custom_component)

# Reemplazar los texto_respuesta_correcta y texto_respuesta_incorrecta
for i, line in enumerate(content):
    # Reemplazar texto de respuesta correcta
    if '                                                rx.text(' in line and '"¡Respuesta correcta!"' in content[i+1]:
        content[i] = '                                                correct_answer_text(),\n'
        # Eliminar las 4 líneas siguientes (texto, color, font_weight, style)
        for j in range(4):
            content[i+1] = ''
    
    # Reemplazar texto de respuesta incorrecta
    if '                                                rx.text(' in line and '"Respuesta incorrecta"' in content[i+1]:
        content[i] = '                                                incorrect_answer_text(),\n'
        # Eliminar las 4 líneas siguientes (texto, color, font_weight, style)
        for j in range(4):
            content[i+1] = ''

# Guardar el contenido modificado (eliminar líneas vacías duplicadas)
filtered_content = []
for line in content:
    if line != '':
        filtered_content.append(line)

with open(file_path, 'w') as file:
    file.writelines(filtered_content)

print("Se han aplicado las modificaciones para corregir los colores en el modo de revisión.")
print("Ahora se usan componentes HTML directos para garantizar que los colores se muestren correctamente.")
