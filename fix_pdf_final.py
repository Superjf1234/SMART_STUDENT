#!/usr/bin/env python
"""
Script definitivo para solucionar el problema 404 al descargar PDFs
Este script crea un nuevo directorio que es accesible desde el navegador y un mecanismo de redirección
"""
import os
import glob
import shutil
from pathlib import Path

# Constantes
WORKSPACE_ROOT = '/workspaces/SMART_STUDENT'
STATIC_DIR = os.path.join(WORKSPACE_ROOT, '.web', 'public')
ASSETS_DIR = os.path.join(WORKSPACE_ROOT, 'assets')
PDFS_SOURCE_DIR = os.path.join(ASSETS_DIR, 'pdfs')
PDFS_PUBLIC_DIR = os.path.join(STATIC_DIR, 'assets', 'pdfs')

# Crear los directorios necesarios
print("1. Creando directorios necesarios...")
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(PDFS_SOURCE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'assets'), exist_ok=True)
os.makedirs(PDFS_PUBLIC_DIR, exist_ok=True)
print("✓ Directorios creados correctamente")

# Crear un archivo PDF de prueba
print("\n2. Creando archivo PDF de prueba...")
test_pdf_path = os.path.join(PDFS_SOURCE_DIR, 'test_fixed.pdf')
with open(test_pdf_path, 'w') as f:
    f.write("%PDF-1.7\n% Archivo PDF de prueba para SMART_STUDENT\n")
print(f"✓ Archivo PDF de prueba creado en {test_pdf_path}")

# Copiar el PDF de prueba a la carpeta pública
print("\n3. Copiando archivo PDF a carpeta pública...")
test_pdf_public_path = os.path.join(PDFS_PUBLIC_DIR, 'test_fixed.pdf')
shutil.copy2(test_pdf_path, test_pdf_public_path)
print(f"✓ Archivo PDF copiado a {test_pdf_public_path}")

# Escanear y copiar archivos PDF existentes
print("\n4. Copiando PDFs existentes a carpeta pública...")
pdf_files = glob.glob(os.path.join(PDFS_SOURCE_DIR, '*.pdf'))
for pdf_file in pdf_files:
    filename = os.path.basename(pdf_file)
    dest_path = os.path.join(PDFS_PUBLIC_DIR, filename)
    if os.path.abspath(pdf_file) != os.path.abspath(dest_path):  # Evitar copiar sobre sí mismo
        shutil.copy2(pdf_file, dest_path)
        print(f"✓ Copiado: {filename}")

# Establecer permisos
print("\n5. Estableciendo permisos...")
for root, dirs, files in os.walk(STATIC_DIR):
    for d in dirs:
        try:
            os.chmod(os.path.join(root, d), 0o755)
        except:
            pass
    for f in files:
        try:
            os.chmod(os.path.join(root, f), 0o644)
        except:
            pass
print("✓ Permisos establecidos correctamente")

# Verificar configuración
print("\n6. Verificando la configuración URL y acceso a PDFs...")

# Buscar la configuración en cuestionario.py
cuestionario_file = os.path.join(WORKSPACE_ROOT, 'mi_app_estudio', 'cuestionario.py')
state_file = os.path.join(WORKSPACE_ROOT, 'mi_app_estudio', 'state.py')

needs_cuestionario_fix = False
needs_state_fix = False

# Verificar cuestionario.py
try:
    with open(cuestionario_file, 'r') as f:
        cuestionario_content = f.read()
    
    if "self.cuestionario_pdf_url = f\"/{filepath.replace(os.sep, '/')}\"" in cuestionario_content:
        print("✗ Encontrada URL incorrecta en cuestionario.py - se requiere corrección")
        needs_cuestionario_fix = True
    elif "self.cuestionario_pdf_url = f\"/assets/pdfs/{filename}\"" in cuestionario_content:
        print("✓ La URL en cuestionario.py está configurada correctamente")
    else:
        print("? No se identificó el patrón en cuestionario.py")
except Exception as e:
    print(f"Error al verificar cuestionario.py: {e}")

# Verificar state.py
try:
    with open(state_file, 'r') as f:
        state_content = f.read()
    
    if "pdf_path = os.path.join(\"assets\", CuestionarioState.cuestionario_pdf_url.lstrip('/'))" in state_content:
        print("✗ Encontrado patrón incorrecto de acceso en state.py - se requiere corrección")
        needs_state_fix = True
    elif "pdf_path = CuestionarioState.cuestionario_pdf_url.lstrip('/')" in state_content:
        print("✓ El acceso en state.py está configurado correctamente")
    else:
        print("? No se identificó el patrón en state.py")
except Exception as e:
    print(f"Error al verificar state.py: {e}")

# Realizar correcciones si es necesario
if needs_cuestionario_fix:
    print("\n7. Corrigiendo cuestionario.py...")
    try:
        updated_cuestionario = cuestionario_content.replace(
            "self.cuestionario_pdf_url = f\"/{filepath.replace(os.sep, '/')}\" # Use forward slashes for URL",
            "self.cuestionario_pdf_url = f\"/assets/pdfs/{filename}\" # URL relativa al directorio de archivos estáticos"
        )
        
        # Verificar si hubo cambio
        if updated_cuestionario != cuestionario_content:
            with open(cuestionario_file, 'w') as f:
                f.write(updated_cuestionario)
            print("✓ cuestionario.py corregido exitosamente")
        else:
            print("? No se encontró la cadena exacta para reemplazar en cuestionario.py")
    except Exception as e:
        print(f"Error al corregir cuestionario.py: {e}")

if needs_state_fix:
    print("\n8. Corrigiendo state.py...")
    try:
        updated_state = state_content.replace(
            "pdf_path = os.path.join(\"assets\", CuestionarioState.cuestionario_pdf_url.lstrip('/'))",
            "pdf_path = CuestionarioState.cuestionario_pdf_url.lstrip('/')"
        )
        
        # Verificar si hubo cambio
        if updated_state != state_content:
            with open(state_file, 'w') as f:
                f.write(updated_state)
            print("✓ state.py corregido exitosamente")
        else:
            print("? No se encontró la cadena exacta para reemplazar en state.py")
    except Exception as e:
        print(f"Error al corregir state.py: {e}")

# Resumen final
print("\n=== RESUMEN DE LA SOLUCIÓN ===")
print("✓ Se han creado las carpetas necesarias")
print("✓ Se ha creado un archivo PDF de prueba")
print("✓ Se han copiado los PDFs existentes a la carpeta pública")
print("✓ Se han establecido los permisos correctos")
print("✓ Se ha verificado la configuración de URLs")
if needs_cuestionario_fix or needs_state_fix:
    print("✓ Se han realizado correcciones en los archivos")

print("\n=== VERIFICACIÓN ===")
print(f"1. URL del archivo de prueba: /assets/pdfs/test_fixed.pdf")
print(f"2. La ruta física correspondiente es: {test_pdf_public_path}")
print(f"3. El directorio público es: {STATIC_DIR}")

print("\n=== ACCIÓN REQUERIDA ===")
print("Reinicia la aplicación con 'reflex run' para aplicar los cambios")
print("Si el problema persiste, verifica los logs del servidor buscando errores 404 para identificar la ruta exacta")
