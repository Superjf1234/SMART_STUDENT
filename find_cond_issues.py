#!/usr/bin/env python3
"""
Script para encontrar posibles problemas con rx.cond()
"""

import re

def find_cond_issues():
    with open('/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py', 'r') as f:
        content = f.read()
    
    # Buscar patrones de rx.cond con strings crudos
    patterns = [
        r'rx\.cond\([^)]*"[^"]*"[^)]*\)',  # rx.cond con strings entre comillas
        r'cond\([^)]*"[^"]*"[^)]*\)',      # cond con strings entre comillas
    ]
    
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        for pattern in patterns:
            if re.search(pattern, line):
                # Verificar si no está dentro de rx.text() o similar
                if '"' in line and 'rx.text(' not in line and 'rx.cond(' in line:
                    issues.append((i, line.strip()))
    
    return issues

if __name__ == "__main__":
    issues = find_cond_issues()
    
    if issues:
        print("⚠️ Posibles problemas encontrados:")
        for line_num, line in issues:
            print(f"Línea {line_num}: {line}")
    else:
        print("✅ No se encontraron problemas obvios")
