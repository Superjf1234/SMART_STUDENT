#!/usr/bin/env python3
"""
Analizador de uso de memoria para identificar problemas
"""

import sys
import os
import psutil
import gc
from pathlib import Path

def analyze_memory_usage():
    """Analizar el uso actual de memoria"""
    process = psutil.Process()
    
    print("=== ANÁLISIS DE MEMORIA ===")
    print(f"RSS (Resident Set Size): {process.memory_info().rss / 1024 / 1024:.2f} MB")
    print(f"VMS (Virtual Memory Size): {process.memory_info().vms / 1024 / 1024:.2f} MB")
    print(f"Porcentaje de memoria del sistema: {process.memory_percent():.2f}%")
    
    # Información del sistema
    memory = psutil.virtual_memory()
    print(f"\n=== MEMORIA DEL SISTEMA ===")
    print(f"Total: {memory.total / 1024 / 1024:.2f} MB")
    print(f"Disponible: {memory.available / 1024 / 1024:.2f} MB")
    print(f"Usado: {memory.used / 1024 / 1024:.2f} MB")
    print(f"Porcentaje usado: {memory.percent}%")

def analyze_modules():
    """Analizar módulos cargados que podrían consumir memoria"""
    print(f"\n=== MÓDULOS CARGADOS ===")
    
    large_modules = []
    test_modules = []
    debug_modules = []
    
    for name, module in sys.modules.items():
        if hasattr(module, '__file__') and module.__file__:
            try:
                size = Path(module.__file__).stat().st_size
                if size > 100000:  # Archivos > 100KB
                    large_modules.append((name, size))
            except:
                pass
        
        if any(pattern in name for pattern in ['test_', 'debug_', 'analyze_']):
            if name.startswith('test_'):
                test_modules.append(name)
            elif name.startswith('debug_'):
                debug_modules.append(name)
            elif name.startswith('analyze_'):
                debug_modules.append(name)
    
    print(f"Módulos grandes (>100KB): {len(large_modules)}")
    for name, size in sorted(large_modules, key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {name}: {size/1024:.1f} KB")
    
    print(f"\nMódulos de test: {len(test_modules)}")
    for name in test_modules[:5]:
        print(f"  {name}")
    
    print(f"\nMódulos de debug: {len(debug_modules)}")
    for name in debug_modules[:5]:
        print(f"  {name}")

def analyze_project_files():
    """Analizar archivos del proyecto que podrían ser problemáticos"""
    print(f"\n=== ANÁLISIS DE ARCHIVOS DEL PROYECTO ===")
    
    current_dir = Path.cwd()
    large_files = []
    unnecessary_files = []
    
    for file_path in current_dir.rglob("*"):
        if file_path.is_file():
            try:
                size = file_path.stat().st_size
                
                # Archivos grandes
                if size > 1000000:  # > 1MB
                    large_files.append((str(file_path), size))
                
                # Archivos innecesarios para producción
                if any(pattern in file_path.name for pattern in [
                    'test_', 'debug_', 'analyze_', '.log', '.pyc', 
                    'nohup.out', '__pycache__'
                ]):
                    unnecessary_files.append(str(file_path))
                    
            except:
                pass
    
    print(f"Archivos grandes (>1MB): {len(large_files)}")
    for path, size in sorted(large_files, key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {Path(path).name}: {size/1024/1024:.2f} MB")
    
    print(f"\nArchivos innecesarios para producción: {len(unnecessary_files)}")
    for path in unnecessary_files[:10]:
        print(f"  {Path(path).name}")

def get_recommendations():
    """Obtener recomendaciones para optimizar memoria"""
    print(f"\n=== RECOMENDACIONES ===")
    
    recommendations = [
        "1. Usar requirements_optimized.txt (sin selenium)",
        "2. Usar memory_optimized_railway.py como startup script",
        "3. Configurar NODE_OPTIONS='--max-old-space-size=128'",
        "4. Usar WEB_CONCURRENCY=1 para limitar workers",
        "5. Eliminar archivos de test/debug del deploy",
        "6. Considerar dividir la aplicación en módulos más pequeños",
        "7. Usar railway_optimized.json para configuración",
        "8. Considerar upgrade del plan de Railway si es necesario"
    ]
    
    for rec in recommendations:
        print(rec)

def main():
    print("Iniciando análisis de memoria...")
    
    try:
        analyze_memory_usage()
        analyze_modules()
        analyze_project_files()
        get_recommendations()
        
    except ImportError:
        print("psutil no está instalado. Instalando...")
        os.system("pip install psutil")
        print("Ejecuta el script nuevamente después de la instalación")

if __name__ == "__main__":
    main()
