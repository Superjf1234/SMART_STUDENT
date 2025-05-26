#!/usr/bin/env python
"""
Script para corregir la funcionalidad de descarga de PDF en SMART_STUDENT.
Este script modifica el componente de UI para usar rx.download directo en lugar de URL.
"""
import os
import re

# Archivos a modificar
cuestionario_file = '/workspaces/SMART_STUDENT/mi_app_estudio/cuestionario.py'

print("=== SOLUCIÓN ALTERNATIVA PARA DESCARGA DE PDF ===")
print("Modificando cuestionario.py para usar rx.download directo...")

# Buscar el código del botón de descarga y reemplazarlo
with open(cuestionario_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Patrón a buscar: el enlace que usa la URL del PDF
pattern = r'''rx\.cond\(\s*
                        CuestionarioState\.cuestionario_pdf_url != "",\s*
                        rx\.link\(\s*
                            rx\.button\([^)]*\),\s*
                            href=CuestionarioState\.cuestionario_pdf_url,\s*
                            is_external=True,\s*
                        \),\s*
                        rx\.fragment\(\)'''

# Nuevo código que usa rx.download directamente
replacement = '''rx.cond(
                        CuestionarioState.cuestionario_pdf_url != "",
                        rx.button(
                            rx.hstack(
                                rx.icon("download", mr="0.2em"),
                                rx.text("Descargar PDF")
                            ),
                            size="2",
                            variant="soft",
                            color_scheme="green",
                            on_click=AppState.download_pdf,
                        ),
                        rx.fragment()'''

# Usar re.DOTALL para que el patrón funcione en múltiples líneas
modified_content = re.sub(pattern, replacement, content, flags=re.VERBOSE | re.DOTALL)

if content != modified_content:
    with open(cuestionario_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    print("✓ Botón de descarga modificado para usar AppState.download_pdf directamente")
    print("  Ahora el botón llamará a la función download_pdf del estado en lugar de usar una URL")
else:
    print("✗ No se encontró el patrón del botón de descarga o ya estaba modificado")

print("\n=== SIGUIENTES PASOS ===")
print("1. Reinicia tu aplicación Reflex con 'reflex run'")
print("2. Genera un nuevo cuestionario y prueba el botón 'Descargar PDF'")
print("3. Ahora el botón debería ejecutar la función download_pdf en vez de abrir una URL")
print("\nEsta solución evita el problema del error 404 al no depender de una URL estática")
