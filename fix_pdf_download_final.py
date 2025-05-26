#!/usr/bin/env python
"""
Script para solucionar el problema del error 404 en la descarga de PDFs.
Este script:
1. Verifica la estructura de directorios
2. Corrige las URLs en el código
3. Copia los archivos PDF al directorio correcto
4. Genera un PDF de prueba
"""
import os
import glob
import shutil
import subprocess
import re
import datetime
import sys

print("=== SOLUCIÓN PARA ERRORES 404 EN DESCARGA DE PDF ===")

# 1. Verificar y crear directorios necesarios
print("\n1. Verificando directorios...")
project_root = '/workspaces/SMART_STUDENT'
directories = [
    'assets',
    'assets/pdfs',
    '.web/public',
    '.web/public/assets',
    '.web/public/assets/pdfs'
]

for directory in directories:
    full_path = os.path.join(project_root, directory)
    if not os.path.exists(full_path):
        try:
            os.makedirs(full_path, exist_ok=True)
            print(f"✓ Creado directorio: {directory}")
        except Exception as e:
            print(f"✗ Error creando directorio {directory}: {e}")
    else:
        print(f"✓ El directorio {directory} ya existe")

# 2. Corregir el archivo cuestionario.py
print("\n2. Corrigiendo el archivo cuestionario.py...")
cuestionario_file = os.path.join(project_root, 'mi_app_estudio', 'cuestionario.py')
if os.path.exists(cuestionario_file):
    try:
        with open(cuestionario_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el patrón de URL del PDF y corregirlo
        old_pattern = r'self\.cuestionario_pdf_url\s*=\s*f"/{filepath\.replace\(os\.sep,\s*\'/\'\)}"'
        new_content = re.sub(old_pattern, 'self.cuestionario_pdf_url = f"/assets/pdfs/{filename}"', content)
        
        if content != new_content:
            with open(cuestionario_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✓ URL del PDF en cuestionario.py corregida")
        else:
            print("✓ URL del PDF en cuestionario.py ya estaba correcta")
    except Exception as e:
        print(f"✗ Error al modificar cuestionario.py: {e}")
else:
    print(f"✗ No se encontró el archivo {cuestionario_file}")

# 3. Corregir el archivo state.py
print("\n3. Corrigiendo el archivo state.py...")
state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')
if os.path.exists(state_file):
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el patrón de ruta del PDF y corregirlo
        old_pattern = r'pdf_path\s*=\s*os\.path\.join\("assets",\s*CuestionarioState\.cuestionario_pdf_url\.lstrip\(\'/\'\)\)'
        new_content = re.sub(old_pattern, 'pdf_path = CuestionarioState.cuestionario_pdf_url.lstrip("/")', content)
        
        if content != new_content:
            with open(state_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✓ Ruta del PDF en state.py corregida")
        else:
            print("✓ Ruta del PDF en state.py ya estaba correcta")
    except Exception as e:
        print(f"✗ Error al modificar state.py: {e}")
else:
    print(f"✗ No se encontró el archivo {state_file}")

# 4. Crear un PDF de prueba
print("\n4. Creando PDF de prueba...")
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
filename = f"test_pdf_{timestamp}.pdf"
pdf_path = os.path.join(project_root, 'assets', 'pdfs', filename)

try:
    # Crear un archivo PDF simple con el encabezado mínimo requerido
    with open(pdf_path, 'w') as f:
        f.write("%PDF-1.7\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n171\n%%EOF")
    print(f"✓ Archivo PDF de prueba creado en: {pdf_path}")
    
    # Copiar a la carpeta pública
    public_pdf_path = os.path.join(project_root, '.web', 'public', 'assets', 'pdfs', filename)
    shutil.copy2(pdf_path, public_pdf_path)
    print(f"✓ PDF copiado a: {public_pdf_path}")
    
    # URL pública del PDF
    pdf_url = f"/assets/pdfs/{filename}"
    print(f"✓ URL del PDF de prueba: {pdf_url}")
except Exception as e:
    print(f"✗ Error creando el PDF de prueba: {e}")

# 5. Copiar todos los PDFs existentes a la carpeta pública
print("\n5. Copiando PDFs existentes a la carpeta pública...")
pdfs_dir = os.path.join(project_root, 'assets', 'pdfs')
public_pdfs_dir = os.path.join(project_root, '.web', 'public', 'assets', 'pdfs')

if os.path.exists(pdfs_dir):
    pdf_files = [f for f in os.listdir(pdfs_dir) if f.endswith('.pdf')]
    if pdf_files:
        for pdf_file in pdf_files:
            src = os.path.join(pdfs_dir, pdf_file)
            dst = os.path.join(public_pdfs_dir, pdf_file)
            try:
                shutil.copy2(src, dst)
                print(f"✓ Copiado: {pdf_file}")
            except Exception as e:
                print(f"✗ Error copiando {pdf_file}: {e}")
        print(f"✓ {len(pdf_files)} archivos PDF copiados")
    else:
        print("✓ No hay archivos PDF para copiar")
else:
    print(f"✗ Directorio {pdfs_dir} no existe")

# 6. Sincronizar directorios
print("\n6. Sincronizando directorios para asegurar la disponibilidad de los archivos...")
try:
    # Asegurar permisos de los directorios
    os.chmod(os.path.join(project_root, 'assets'), 0o755)
    os.chmod(os.path.join(project_root, 'assets', 'pdfs'), 0o755)
    os.chmod(os.path.join(project_root, '.web', 'public', 'assets'), 0o755)
    os.chmod(os.path.join(project_root, '.web', 'public', 'assets', 'pdfs'), 0o755)
    print("✓ Permisos de directorios actualizados")
except Exception as e:
    print(f"✗ Error actualizando permisos: {e}")

# 7. Resumen y siguientes pasos
print("\n=== RESUMEN ===")
print("1. Directorios verificados y creados")
print("2. Código corregido en cuestionario.py")
print("3. Código corregido en state.py")
print("4. PDF de prueba creado")
print("5. PDFs existentes copiados")
print("\n=== SIGUIENTES PASOS ===")
print("1. Reinicia tu aplicación Reflex con 'reflex run'")
print("2. Accede a la URL de prueba para verificar: " + pdf_url)
print("3. Genera un nuevo cuestionario y prueba el botón 'Descargar PDF'")
print("\nSi continúas teniendo problemas, verifica:")
print("- Que el servidor Reflex esté sirviendo archivos estáticos correctamente")
print("- Que los permisos de los directorios y archivos sean adecuados")
print("- Los logs del servidor en busca de errores específicos")
