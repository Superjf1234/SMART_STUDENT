# setup_pdf_environment.py
# Script para preparar el entorno para descargar PDFs correctamente
import os
import glob
import shutil
import sys

print("===== Configurando ambiente para descarga de PDFs =====")

# 1. Crear estructura de directorios
WORKSPACE_ROOT = '/workspaces/SMART_STUDENT'
ASSETS_DIR = os.path.join(WORKSPACE_ROOT, 'assets')
PDFS_SOURCE_DIR = os.path.join(ASSETS_DIR, 'pdfs')
PUBLIC_DIR = os.path.join(WORKSPACE_ROOT, '.web', 'public')
PUBLIC_ASSETS_DIR = os.path.join(PUBLIC_DIR, 'assets')
PUBLIC_PDFS_DIR = os.path.join(PUBLIC_ASSETS_DIR, 'pdfs')

print("Creando estructura de directorios...")
os.makedirs(PDFS_SOURCE_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)
os.makedirs(PUBLIC_ASSETS_DIR, exist_ok=True)
os.makedirs(PUBLIC_PDFS_DIR, exist_ok=True)

# 2. Copiar todos los PDFs existentes al directorio público
print("Copiando PDFs existentes...")
pdf_count = 0
for pdf_file in glob.glob(os.path.join(PDFS_SOURCE_DIR, '*.pdf')):
    filename = os.path.basename(pdf_file)
    dest_path = os.path.join(PUBLIC_PDFS_DIR, filename)
    shutil.copy2(pdf_file, dest_path)
    pdf_count += 1
    print(f"  Copiado: {filename}")

print(f"Se copiaron {pdf_count} archivos PDF")

# 3. Crear un archivo de prueba
print("Creando archivo PDF de prueba...")
test_pdf_name = "test_download_check.pdf"
test_source_path = os.path.join(PDFS_SOURCE_DIR, test_pdf_name)
test_dest_path = os.path.join(PUBLIC_PDFS_DIR, test_pdf_name)

# Crear un archivo PDF mínimo válido
with open(test_source_path, 'w') as f:
    f.write("%PDF-1.0\n% Archivo de prueba\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF")

# Copiarlo al directorio público
shutil.copy2(test_source_path, test_dest_path)

print(f"Archivo de prueba creado en: {test_source_path}")
print(f"y copiado a: {test_dest_path}")

# 4. Configurar permisos
print("Estableciendo permisos...")
for root, dirs, files in os.walk(PUBLIC_DIR):
    for d in dirs:
        os.chmod(os.path.join(root, d), 0o755)
    for f in files:
        os.chmod(os.path.join(root, f), 0o644)

print("\n===== Configuración completada =====")
print(f"URL de prueba: /assets/pdfs/{test_pdf_name}")
print("Reinicia la aplicación con 'reflex run' para aplicar los cambios")
print("Si el problema persiste, verifica los logs del servidor")
