#!/usr/bin/env python
"""
Script para verificar las correcciones realizadas en la funcionalidad de descarga de PDF
"""
import os
import sys
import re
import datetime
import traceback

print("===== VERIFICACIÓN DE CORRECCIONES DE DESCARGA DE PDF =====\n")

# Verificar estructura de directorios
print("1. Verificando estructura de directorios:")
project_root = os.path.dirname(os.path.abspath(__file__))
directories = [
    'assets',
    'assets/pdfs',
    '.web',
    '.web/public',
    '.web/public/assets',
    '.web/public/assets/pdfs'
]

for directory in directories:
    full_path = os.path.join(project_root, directory)
    if os.path.exists(full_path):
        print(f"  ✓ {directory} existe")
    else:
        print(f"  ✗ {directory} NO existe")
        try:
            os.makedirs(full_path, exist_ok=True)
            print(f"    - Creado {directory}")
        except Exception as e:
            print(f"    - Error al crear {directory}: {e}")

# Verificar archivo state.py
print("\n2. Verificando correcciones en el código:")
state_path = os.path.join(project_root, 'mi_app_estudio', 'state.py')
if not os.path.exists(state_path):
    print(f"  ✗ No se encontró el archivo state.py en la ruta esperada")
    sys.exit(1)

try:
    with open(state_path, 'r') as f:
        content = f.read()
    
    # Verificar correcciones
    checks = [
        {
            "name": "Manejo seguro de variables reactivas",
            "pattern": r"get_safe_var_value\(CuestionarioState\.cuestionario_pdf_url",
            "status": False
        },
        {
            "name": "Búsqueda en múltiples ubicaciones",
            "pattern": r"Buscando archivos con patrón similar",
            "status": False
        },
        {
            "name": "Verificación robusta de formato PDF",
            "pattern": r"b\"%PDF\" in pdf_bytes\[:1024\]",
            "status": False
        },
        {
            "name": "Fallback a HTML si falla PDF",
            "pattern": r"No se encontró o no se pudo leer un PDF válido. Generando HTML",
            "status": False
        }
    ]
    
    for check in checks:
        if re.search(check["pattern"], content):
            check["status"] = True
            print(f"  ✓ {check['name']} - CORRECTO")
        else:
            print(f"  ✗ {check['name']} - NO ENCONTRADO")
    
    # Generar un PDF de prueba para tests
    print("\n3. Generando PDF de prueba:")
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    test_pdf_name = f"test_cuestionario_{timestamp}.pdf"
    test_pdf_path = os.path.join(project_root, 'assets', 'pdfs', test_pdf_name)
    
    try:
        with open(test_pdf_path, 'wb') as f:
            # Un PDF minimalista válido
            f.write(b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[]/Count 0>>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000015 00000 n \n0000000060 00000 n \ntrailer\n<</Size 3/Root 1 0 R>>\nstartxref\n110\n%%EOF\n")
        print(f"  ✓ PDF de prueba generado: {test_pdf_path}")
        
        # Copiar a la carpeta pública también
        public_path = os.path.join(project_root, '.web', 'public', 'assets', 'pdfs', test_pdf_name)
        import shutil
        shutil.copy2(test_pdf_path, public_path)
        print(f"  ✓ PDF de prueba copiado a área pública: {public_path}")
        
        # Ruta relativa para URL
        relative_url = f"assets/pdfs/{test_pdf_name}"
        print(f"\nRuta relativa para probar en la aplicación:")
        print(f"  URL: /{relative_url}")
        print(f"  (Puedes usar esta URL para establecer manualmente cuestionario_pdf_url en CuestionarioState)")
        
    except Exception as e:
        print(f"  ✗ Error generando PDF de prueba: {e}")
        traceback.print_exc()
    
    # Resumen final
    print("\n4. Resumen de la verificación:")
    total_checks = len(checks)
    passed_checks = sum(1 for check in checks if check["status"])
    
    if passed_checks == total_checks:
        print(f"  ✓ Todas las correcciones verificadas correctamente ({passed_checks}/{total_checks})")
    else:
        print(f"  ⚠ Algunas correcciones no se encontraron ({passed_checks}/{total_checks})")
    
    print("\nRECOMENDACIONES:")
    print("1. Reinicia la aplicación para aplicar todos los cambios")
    print("2. Navega al módulo de cuestionarios y genera un nuevo cuestionario")
    print("3. Intenta descargar el PDF del cuestionario")
    print("4. Revisa los logs para verificar que la ruta del PDF se resuelve correctamente")
    
except Exception as e:
    print(f"Error durante la verificación: {e}")
    traceback.print_exc()
