#!/usr/bin/env python
"""
Script de prueba para verificar que el PDF se puede descargar correctamente
"""
import os
import sys
import re
import datetime
import shutil

# Verificar la estructura de directorios de PDF
def check_pdf_directories():
    print("\n1. Verificando estructura de directorios de PDF...")
    project_root = os.path.dirname(os.path.abspath(__file__))
    expected_paths = [
        'assets',
        'assets/pdfs',
        '.web',
        '.web/public',
        '.web/public/assets',
        '.web/public/assets/pdfs'
    ]

    all_exist = True
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
                all_exist = False
                
    return all_exist

# Crear archivo PDF de prueba
def create_test_pdf():
    print("\n2. Creando PDF de prueba...")
    project_root = os.path.dirname(os.path.abspath(__file__))
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
            
        pdf_url = f"/assets/pdfs/{pdf_filename}"
        print(f"\n3. URL para acceder al PDF: {pdf_url}")
        return pdf_url
    except Exception as e:
        print(f"  ✗ Error creando/copiando archivo PDF: {e}")
        return None

# Verificar el estado del código
def check_code_fixes():
    print("\n4. Verificando correcciones en el código...")
    project_root = os.path.dirname(os.path.abspath(__file__))
    state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')
    
    try:
        with open(state_file, 'r') as f:
            content = f.read()
        
        # Verificar Fix 1: StringCastedVar
        if "str(tema_value)" in content:
            print("  ✓ Fix de StringCastedVar aplicado correctamente")
        else:
            print("  ✗ Fix de StringCastedVar no encontrado")
        
        # Verificar Fix 2: VarTypeError
        if "pdf_url_empty = CuestionarioState.cuestionario_pdf_url ==" in content:
            print("  ✓ Fix de VarTypeError aplicado correctamente")
        else:
            print("  ✗ Fix de VarTypeError no encontrado")
            
        return "str(tema_value)" in content and "pdf_url_empty = CuestionarioState.cuestionario_pdf_url ==" in content
    except Exception as e:
        print(f"  ✗ Error verificando el código: {e}")
        return False

# Verificar manejo seguro de variables reactivas
def suggest_reactive_var_patterns():
    print("\n5. Recomendaciones de patrones seguros para variables reactivas:")
    print("""
  ✓ Para usar una variable reactiva en una función estándar:
    # Incorrecto
    result = standard_function(reactive_var)
    
    # Correcto
    result = standard_function(str(reactive_var))
    
  ✓ Para condicionales con variables reactivas:
    # Incorrecto
    if reactive_var:
        do_something()
    
    # Correcto
    condition = reactive_var != ""
    rx.cond(
        condition,
        lambda: do_something(),
        lambda: do_nothing()
    )
    
  ✓ Para operaciones lógicas con variables reactivas:
    # Incorrecto
    if reactive_var_a and reactive_var_b:
        do_something()
    
    # Correcto
    condition = (reactive_var_a != "") & (reactive_var_b != "")
    rx.cond(
        condition,
        lambda: do_something(),
        lambda: do_nothing()
    )
    """)

if __name__ == "__main__":
    print("=== TEST DE DESCARGA DE PDF ===")
    
    # Comprobar estructura de directorios
    dirs_ok = check_pdf_directories()
    
    # Crear PDF de prueba
    pdf_url = create_test_pdf() if dirs_ok else None
    
    # Verificar correcciones en el código
    code_ok = check_code_fixes()
    
    # Sugerir patrones seguros
    suggest_reactive_var_patterns()
    
    # Resumen
    print("\n=== RESUMEN DEL DIAGNÓSTICO ===")
    if dirs_ok:
        print("  ✓ Estructura de directorios correcta")
    else:
        print("  ✗ Problemas con la estructura de directorios")
        
    if pdf_url:
        print(f"  ✓ PDF de prueba creado en {pdf_url}")
    else:
        print("  ✗ Error creando PDF de prueba")
        
    if code_ok:
        print("  ✓ Correcciones de código aplicadas correctamente")
    else:
        print("  ✗ Faltan algunas correcciones de código")
        
    print("\n=== RESULTADO FINAL ===")
    if dirs_ok and pdf_url and code_ok:
        print("  ✅ Todo correcto. La descarga de PDF debería funcionar.")
    else:
        print("  ❌ Se encontraron problemas. Revise los mensajes anteriores.")
    
    print("=== FIN DEL TEST ===")
