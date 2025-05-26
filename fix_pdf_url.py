#!/usr/bin/env python
"""
Script para corregir el problema de las URLs de PDFs en la aplicación SMART_STUDENT.
Este script modifica tanto la forma en que se generan las URLs como la forma en que
se accede a ellas para descargar los PDFs.
"""

import os
import re

# Archivos a modificar
cuestionario_file = '/workspaces/SMART_STUDENT/mi_app_estudio/cuestionario.py'
state_file = '/workspaces/SMART_STUDENT/mi_app_estudio/state.py'

# 1. Corregir la generación de URLs en cuestionario.py
with open(cuestionario_file, 'r', encoding='utf-8') as file:
    cuestionario_content = file.read()

# Buscar y modificar la línea donde se crea la URL del PDF
pdf_url_pattern = r'self\.cuestionario_pdf_url = f"/{filepath\.replace\(os\.sep, \'/\'\)}" # Use forward slashes for URL'
pdf_url_replacement = r'self.cuestionario_pdf_url = f"/assets/pdfs/{filename}" # URL relativa al directorio de archivos estáticos'

cuestionario_modified = re.sub(pdf_url_pattern, pdf_url_replacement, cuestionario_content)

if cuestionario_content != cuestionario_modified:
    print("Se encontró y corrigió el patrón de URL del PDF en cuestionario.py")
    with open(cuestionario_file, 'w', encoding='utf-8') as file:
        file.write(cuestionario_modified)
else:
    print("No se encontró el patrón de URL del PDF en cuestionario.py")

# 2. Corregir el acceso a las URLs en state.py
with open(state_file, 'r', encoding='utf-8') as file:
    state_content = file.read()

# Buscar y modificar cómo se construye la ruta para acceder al PDF existente
pdf_access_pattern = r'pdf_path = os\.path\.join\("assets", CuestionarioState\.cuestionario_pdf_url\.lstrip\(\'/\'\)\)'
pdf_access_replacement = r'pdf_path = CuestionarioState.cuestionario_pdf_url.lstrip("/")'

state_modified = re.sub(pdf_access_pattern, pdf_access_replacement, state_content)

if state_content != state_modified:
    print("Se encontró y corrigió el patrón de acceso al PDF en state.py")
    with open(state_file, 'w', encoding='utf-8') as file:
        file.write(state_modified)
else:
    print("No se encontró el patrón de acceso al PDF en state.py")

# 3. Asegurémonos de que el directorio para PDFs existe
os.makedirs('assets/pdfs', exist_ok=True)
print("Se verificó que el directorio assets/pdfs existe")

print("¡Correcciones completadas!")
