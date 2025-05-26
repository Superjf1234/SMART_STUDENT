#!/usr/bin/env python
"""
Script para verificar y corregir la configuración de archivos estáticos en Reflex.
Asegura que las carpetas necesarias estén en el lugar correcto.
"""

import os
import shutil
import sys

# Directorios a verificar/crear
dirs_to_check = [
    'assets',
    'assets/pdfs',
    'assets/mapas',
    '/workspaces/SMART_STUDENT/.web/public/assets',
    '/workspaces/SMART_STUDENT/.web/public/assets/pdfs',
    '/workspaces/SMART_STUDENT/.web/public/assets/mapas'
]

for directory in dirs_to_check:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"Creado directorio: {directory}")
        except Exception as e:
            print(f"Error creando directorio {directory}: {e}")

# Función para copiar archivos entre directorios
def sync_directories(src, dst):
    if not os.path.exists(src):
        print(f"Directorio fuente no existe: {src}")
        return
    
    if not os.path.exists(dst):
        os.makedirs(dst)
    
    # Copiar todos los archivos de src a dst
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isfile(s):
            shutil.copy2(s, d)
            print(f"Copiado: {s} -> {d}")
        elif os.path.isdir(s):
            sync_directories(s, d)

# Sincronizar directorios de assets
print("Sincronizando directorios de activos...")
if os.path.exists('/workspaces/SMART_STUDENT/assets'):
    sync_directories('/workspaces/SMART_STUDENT/assets', '/workspaces/SMART_STUDENT/.web/public/assets')
    print("Sincronización completada.")
else:
    print("Directorio de activos no encontrado.")

print("¡Proceso completado!")
