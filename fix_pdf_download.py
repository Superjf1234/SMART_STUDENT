#!/usr/bin/env python
"""
Script completo para solucionar el problema de descarga de PDFs en SMART_STUDENT.
Este script:
1. Corrige las rutas y URLs de los PDFs en el código
2. Crea los directorios necesarios
3. Configura correctamente la sincronización de archivos estáticos entre Reflex y los directorios públicos
"""

import os
import shutil
import sys
import re

print("=== SOLUCIONANDO PROBLEMA DE DESCARGA DE PDFs EN SMART_STUDENT ===")

# 1. CORREGIR RUTAS Y URLs EN EL CÓDIGO

print("\n1. Corrigiendo rutas y URLs en el código...")

# Archivos a modificar
cuestionario_file = '/workspaces/SMART_STUDENT/mi_app_estudio/cuestionario.py'
state_file = '/workspaces/SMART_STUDENT/mi_app_estudio/state.py'

# Patrón para la URL del PDF en cuestionario.py
pdf_url_pattern = (
    r'self\.cuestionario_pdf_url\s*=\s*f"/{filepath\.replace\(os\.sep,\s*\'/\'\)}".*'
)
pdf_url_replacement = (
    'self.cuestionario_pdf_url = f"/assets/pdfs/{filename}" # URL relativa al directorio de archivos estáticos'
)

# Patrón para el acceso al PDF en state.py
pdf_access_pattern = (
    r'pdf_path\s*=\s*os\.path\.join\("assets",\s*CuestionarioState\.cuestionario_pdf_url\.lstrip\(\'/\'\)\)'
)
pdf_access_replacement = (
    'pdf_path = CuestionarioState.cuestionario_pdf_url.lstrip("/")'
)

# Función para reemplazar texto en archivo
def replace_in_file(file_path, pattern, replacement):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Buscar el patrón
        modified = re.sub(pattern, replacement, content)
        
        if content != modified:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified)
            print(f"  ✓ Reemplazo realizado en {os.path.basename(file_path)}")
            return True
        else:
            print(f"  ✗ No se encontró el patrón en {os.path.basename(file_path)} o ya está corregido")
            return False
    except Exception as e:
        print(f"  ✗ Error procesando {file_path}: {e}")
        return False

# Aplicar reemplazos
replace_in_file(cuestionario_file, pdf_url_pattern, pdf_url_replacement)
replace_in_file(state_file, pdf_access_pattern, pdf_access_replacement)

# 2. CREAR DIRECTORIOS NECESARIOS

print("\n2. Creando directorios necesarios...")

# Directorios a crear
directories = [
    '/workspaces/SMART_STUDENT/assets',
    '/workspaces/SMART_STUDENT/assets/pdfs',
    '/workspaces/SMART_STUDENT/.web/public/assets',
    '/workspaces/SMART_STUDENT/.web/public/assets/pdfs'
]

for directory in directories:
    try:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ Directorio creado o verificado: {directory}")
    except Exception as e:
        print(f"  ✗ Error creando directorio {directory}: {e}")

# 3. CREAR ARCHIVO PDF DE PRUEBA

print("\n3. Creando archivo PDF de prueba...")

test_pdf_path = '/workspaces/SMART_STUDENT/assets/pdfs/test_pdf.pdf'
try:
    with open(test_pdf_path, 'w') as f:
        f.write("%PDF-1.7\n% PDF de prueba para SMART_STUDENT\n")
    print(f"  ✓ Archivo de prueba creado: {test_pdf_path}")
except Exception as e:
    print(f"  ✗ Error creando archivo de prueba {test_pdf_path}: {e}")

# 4. SINCRONIZAR ARCHIVOS CON .WEB/PUBLIC

print("\n4. Sincronizando archivos con directorio público de Reflex...")

def sync_directory(src, dst):
    try:
        if not os.path.exists(src):
            print(f"  ✗ El directorio fuente no existe: {src}")
            return False
            
        os.makedirs(dst, exist_ok=True)
        
        # Copiar todos los archivos de src a dst
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            
            if os.path.isfile(s):
                shutil.copy2(s, d)
                print(f"  ✓ Archivo copiado: {item}")
            elif os.path.isdir(s):
                if sync_directory(s, d):
                    print(f"  ✓ Subdirectorio sincronizado: {item}")
        return True
    except Exception as e:
        print(f"  ✗ Error sincronizando {src} a {dst}: {e}")
        return False

# Sincronizar directorio assets
sync_directory('/workspaces/SMART_STUDENT/assets', '/workspaces/SMART_STUDENT/.web/public/assets')

# 5. VERIFICAR PERMISOS

print("\n5. Verificando permisos de archivos...")

try:
    for root, dirs, files in os.walk('/workspaces/SMART_STUDENT/assets'):
        for file in files:
            file_path = os.path.join(root, file)
            os.chmod(file_path, 0o644)  # Permisos rw-r--r--
            print(f"  ✓ Permisos actualizados para: {file_path}")
        for directory in dirs:
            dir_path = os.path.join(root, directory)
            os.chmod(dir_path, 0o755)  # Permisos rwxr-xr-x
            print(f"  ✓ Permisos actualizados para: {dir_path}")
except Exception as e:
    print(f"  ✗ Error actualizando permisos: {e}")

print("\n=== SOLUCIÓN COMPLETADA ===")
print("Ahora deberías poder descargar PDFs desde la pestaña de cuestionarios.")
print("Si aún hay problemas, reinicia la aplicación Reflex con: reflex run --loglevel debug")
