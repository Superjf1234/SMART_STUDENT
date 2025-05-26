#!/usr/bin/env python
"""
Script de diagnóstico para solucionar el problema de descarga de PDF
"""
import os
import glob
import shutil
import datetime
import sys

print("=== DIAGNÓSTICO DE DESCARGA DE PDF EN SMART_STUDENT ===")

# 1. Verificar estructura del proyecto
print("\n1. Verificando estructura del proyecto...")
project_root = '/workspaces/SMART_STUDENT'
expected_paths = [
    'assets',
    'assets/pdfs',
    '.web',
    '.web/public',
    '.web/public/assets',
    '.web/public/assets/pdfs'
]

for path in expected_paths:
    full_path = os.path.join(project_root, path)
    if os.path.exists(full_path):
        print(f"  ✓ {path} existe")
    else:
        print(f"  ✗ {path} no existe -> creando")
        try:
            os.makedirs(full_path, exist_ok=True)
            print(f"    ✓ {path} creado correctamente")
        except Exception as e:
            print(f"    ✗ Error creando {path}: {e}")

# 2. Crear archivo PDF de prueba
print("\n2. Creando PDF de prueba...")
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
pdf_filename = f"test_pdf_{timestamp}.pdf"
pdf_path = os.path.join(project_root, 'assets', 'pdfs', pdf_filename)
public_pdf_path = os.path.join(project_root, '.web', 'public', 'assets', 'pdfs', pdf_filename)

try:
    # Crear PDF simple
    with open(pdf_path, 'w') as pdf_file:
        pdf_file.write("%PDF-1.7\n% Archivo PDF de prueba para SMART_STUDENT\n")
    print(f"  ✓ Archivo PDF creado en: {pdf_path}")
    
    # Copiar a la carpeta pública
    shutil.copy2(pdf_path, public_pdf_path)
    print(f"  ✓ Archivo copiado a: {public_pdf_path}")
    
    # Establecer permisos
    try:
        os.chmod(pdf_path, 0o644)
        os.chmod(public_pdf_path, 0o644)
        print(f"  ✓ Permisos establecidos correctamente")
    except Exception as e:
        print(f"  ✗ Error estableciendo permisos: {e}")
except Exception as e:
    print(f"  ✗ Error creando/copiando archivo PDF: {e}")

# 3. Verificar URL de acceso
pdf_url = f"/assets/pdfs/{pdf_filename}"
print(f"\n3. URL para acceder al PDF: {pdf_url}")
print(f"   Esta URL debe funcionar para la descarga del PDF")

# 4. Buscar PDFs existentes y copiarlos
print("\n4. Buscando PDFs existentes...")
pdf_files = glob.glob(os.path.join(project_root, 'assets', 'pdfs', '*.pdf'))
if pdf_files:
    print(f"  ✓ Encontrados {len(pdf_files)} archivos PDF")
    for pdf in pdf_files:
        pdf_name = os.path.basename(pdf)
        dst_path = os.path.join(project_root, '.web', 'public', 'assets', 'pdfs', pdf_name)
        try:
            shutil.copy2(pdf, dst_path)
            print(f"    ✓ Copiado {pdf_name} a .web/public/assets/pdfs/")
        except Exception as e:
            print(f"    ✗ Error copiando {pdf_name}: {e}")
else:
    print("  ✗ No se encontraron archivos PDF existentes")

# 5. Verificar código en cuestionario.py
print("\n5. Verificando código en cuestionario.py...")
cuestionario_file = os.path.join(project_root, 'mi_app_estudio', 'cuestionario.py')
try:
    with open(cuestionario_file, 'r') as f:
        content = f.read()
    
    # Buscar cómo se genera la URL del PDF
    if "self.cuestionario_pdf_url = f\"/{filepath.replace(os.sep, '/')}\"" in content:
        print("  ✗ Se encontró URL incorrecta -> necesita corrección")
        fix_needed = True
    elif "self.cuestionario_pdf_url = f\"/assets/pdfs/{filename}\"" in content:
        print("  ✓ URL del PDF configurada correctamente")
        fix_needed = False
    else:
        print("  ? No se encontró ningún patrón conocido para la URL del PDF")
        fix_needed = True
        
    if fix_needed:
        print("  ! Se recomienda aplicar el script fix_pdf_url.py o fix_pdf_download.py")
except Exception as e:
    print(f"  ✗ Error verificando cuestionario.py: {e}")

# 6. Verificar código en state.py
print("\n6. Verificando código en state.py...")
state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')
try:
    with open(state_file, 'r') as f:
        content = f.read()
    
    # Buscar cómo se lee el PDF
    if "pdf_path = os.path.join(\"assets\", CuestionarioState.cuestionario_pdf_url.lstrip('/'))" in content:
        print("  ✗ Se encontró patrón incorrecto de acceso al PDF -> necesita corrección")
        fix_needed = True
    elif "pdf_path = CuestionarioState.cuestionario_pdf_url.lstrip('/')" in content:
        print("  ✓ Acceso al PDF configurado correctamente")
        fix_needed = False
    else:
        print("  ? No se encontró ningún patrón conocido para el acceso al PDF")
        fix_needed = True
        
    if fix_needed:
        print("  ! Se recomienda aplicar el script fix_pdf_url.py o fix_pdf_download.py")
except Exception as e:
    print(f"  ✗ Error verificando state.py: {e}")

# 7. Información de resolución
print("\n=== SOLUCIÓN RECOMENDADA ===")
print("1. Verificar que el código genere las URLs como '/assets/pdfs/nombre_archivo.pdf'")
print("2. Asegurarse de que los archivos PDF estén copiados en .web/public/assets/pdfs/")
print("3. La URL para el archivo de prueba es:")
print(f"   {pdf_url}")
print("4. Si al hacer clic en 'Descargar PDF' aparece el error 404, revisar los logs del servidor")
print("   y asegurarse de que la ruta en el navegador corresponda con la ubicación del archivo")
print("=== FIN DIAGNÓSTICO ===")
