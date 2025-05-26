#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

# Ruta del archivo a revisar
file_path = 'mi_app_estudio/state.py'

print(f"Examinando el archivo {file_path} por caracteres problemáticos...")

# Leer el archivo y encontrar líneas específicas
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Examinar las líneas alrededor del método problemático
start_line = 2310
end_line = 2330

for i, line in enumerate(lines[start_line:end_line], start=start_line):
    # Mostrar la línea y sus caracteres
    print(f"Línea {i+1}: {repr(line)}")

print("\nComprobando indentación específica...")
target_method = "def open_contact_form(self):"
for i, line in enumerate(lines):
    if target_method in line:
        print(f"Método encontrado en línea {i+1}")
        # Mostrar las siguientes líneas para verificar indentación
        for j in range(i, min(i+10, len(lines))):
            indent = len(lines[j]) - len(lines[j].lstrip())
            chars = ' '.join(f'{ord(c)}' for c in lines[j][:indent])
            print(f"Línea {j+1}: Indentación={indent}, Caracteres={chars}, Contenido={repr(lines[j].lstrip())}")

print("\nHecho.")
