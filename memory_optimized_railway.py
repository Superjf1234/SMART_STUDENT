#!/usr/bin/env python3
"""
Railway Memory Optimized Deployment Script
Versión ultra-optimizada para minimizar el uso de memoria
"""

import os
import sys
import subprocess
import gc

def setup_memory_optimization():
    """Configurar variables para optimización extrema de memoria"""
    
    # Configurar Node.js con límites estrictos de memoria
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=128 --max-semi-space-size=2 --max-heap-size=128'
    
    # Configurar Python para usar menos memoria
    os.environ['PYTHONHASHSEED'] = '0'  # Reproducibilidad y menos overhead
    os.environ['PYTHONOPTIMIZE'] = '2'  # Optimizaciones máximas
    
    # Deshabilitar features que consumen memoria
    os.environ['NEXT_TELEMETRY_DISABLED'] = '1'
    os.environ['NODE_ENV'] = 'production'
    os.environ['REFLEX_ENV'] = 'prod'
    
    # Configurar Reflex para usar mínima memoria
    os.environ['REFLEX_FRONTEND_PORT'] = str(int(os.environ.get('PORT', '8080')) + 1)
    os.environ['REFLEX_BACKEND_PORT'] = os.environ.get('PORT', '8080')
    os.environ['REFLEX_DB_URL'] = 'sqlite:///student_stats.db'
    
    # Configurar límites de workers
    os.environ['WEB_CONCURRENCY'] = '1'  # Solo 1 worker para ahorrar memoria
    os.environ['REFLEX_WORKERS'] = '1'
    
    print("Memory optimization configured:")
    print(f"NODE_OPTIONS: {os.environ['NODE_OPTIONS']}")
    print(f"PYTHONOPTIMIZE: {os.environ['PYTHONOPTIMIZE']}")
    print(f"WEB_CONCURRENCY: {os.environ['WEB_CONCURRENCY']}")

def cleanup_memory():
    """Limpiar memoria antes de iniciar la aplicación"""
    # Forzar garbage collection
    gc.collect()
    
    # Limpiar imports innecesarios si es posible
    modules_to_remove = []
    for module_name in sys.modules:
        if any(pattern in module_name for pattern in ['test_', 'debug_', 'analyze_']):
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        if module_name in sys.modules:
            del sys.modules[module_name]
    
    gc.collect()
    print(f"Cleaned up {len(modules_to_remove)} test/debug modules")

def main():
    print("=== RAILWAY MEMORY OPTIMIZED DEPLOYMENT ===")
    
    # Setup memory optimization
    setup_memory_optimization()
    
    # Clean memory
    cleanup_memory()
    
    # Configurar paths
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    current_dir = os.getcwd()
    app_dir = os.path.join(current_dir, 'mi_app_estudio')
    os.environ['PYTHONPATH'] = f"{current_dir}:{app_dir}"
    
    print(f"PORT: {port}")
    print(f"HOST: {host}")
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    
    # Cambiar al directorio de la aplicación
    if os.path.exists('mi_app_estudio'):
        os.chdir('mi_app_estudio')
        print(f"Changed to: {os.getcwd()}")
    else:
        print("ERROR: mi_app_estudio directory not found")
        return 1
    
    # Verificar archivos críticos
    if not os.path.exists('mi_app_estudio.py'):
        print("ERROR: Main app file not found")
        return 1
    
    print("Starting Memory Optimized Reflex...")
    
    # Comando optimizado para memoria
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'prod',
        '--backend-host', host,
        '--backend-port', port,
        '--frontend-port', str(int(port) + 1)
    ]
    
    print(f"COMMAND: {' '.join(cmd)}")
    
    # Ejecutar con límites de memoria
    try:
        # Usar exec para reemplazar el proceso y liberar memoria
        os.execvpe(cmd[0], cmd, os.environ)
        
    except Exception as e:
        print(f"Error with execvpe: {e}")
        
        # Fallback con subprocess
        try:
            result = subprocess.run(cmd, env=os.environ.copy())
            return result.returncode
        except Exception as e2:
            print(f"Subprocess failed: {e2}")
            return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
