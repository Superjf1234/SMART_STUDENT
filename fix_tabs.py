#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Ruta del archivo a modificar
file_path = 'mi_app_estudio/state.py'

print(f"Leyendo {file_path}...")
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Reemplazar cualquier posible tabulador con espacios para mantener consistencia
fixed_content = content.replace('\t', '    ')

# Guardar el archivo modificado
print("Guardando el archivo modificado...")
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(fixed_content)

print("Hecho.")
