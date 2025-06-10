#!/usr/bin/env python3
"""
Script final optimizado para Railway con manejo de errores de Rich/Markup
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_railway_environment():
    """Configurar variables de entorno optimizadas para Railway"""
    # Variables de entorno básicas
    os.environ['PORT'] = os.environ.get('PORT', '8080')
    os.environ['HOST'] = '0.0.0.0'
    os.environ['RAILWAY_ENVIRONMENT'] = 'production'
    
    # Configuración de Reflex para producción
    os.environ['REFLEX_ENV'] = 'prod'
    os.environ['REFLEX_DEBUG'] = 'false'
    os.environ['REFLEX_DISABLE_TELEMETRY'] = 'true'
    
    # Optimizaciones de memoria
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=256 --optimize-for-size'
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Variables de Python
    os.environ['PYTHONPATH'] = '/app'
    
    # Configurar GEMINI_API_KEY si no existe
    if 'GEMINI_API_KEY' not in os.environ:
        logger.warning("GEMINI_API_KEY no configurada")
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    try:
        import reflex as rx
        logger.info("✓ Reflex disponible")
        return True
    except ImportError as e:
        logger.error(f"✗ Error importando Reflex: {e}")
        return False

def clean_reflex_cache():
    """Limpiar cache de Reflex para evitar problemas"""
    cache_dirs = ['.web', '.reflex', 'node_modules', '__pycache__']
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                import shutil
                shutil.rmtree(cache_dir)
                logger.info(f"✓ Cache {cache_dir} limpiado")
            except Exception as e:
                logger.warning(f"⚠ No se pudo limpiar {cache_dir}: {e}")

def init_reflex_safe():
    """Inicializar Reflex de forma segura para evitar errores de Rich"""
    try:
        logger.info("Inicializando Reflex...")
        
        # Ejecutar reflex init con output silenciado para evitar errores de Rich
        result = subprocess.run(
            [sys.executable, '-m', 'reflex', 'init', '--loglevel', 'error'],
            capture_output=True,
            text=True,
            timeout=120,
            env=os.environ.copy()
        )
        
        if result.returncode == 0:
            logger.info("✓ Reflex init exitoso")
            return True
        else:
            logger.warning(f"⚠ Reflex init con advertencias: {result.stderr}")
            # Continuar aunque haya advertencias
            return True
            
    except subprocess.TimeoutExpired:
        logger.error("✗ Reflex init timeout")
        return False
    except Exception as e:
        logger.error(f"✗ Error en reflex init: {e}")
        return False

def run_reflex_production():
    """Ejecutar Reflex en modo producción con manejo de errores"""
    try:
        logger.info("Iniciando Reflex en modo producción...")
        
        # Comando para ejecutar en producción
        cmd = [
            sys.executable, '-m', 'reflex', 'run',
            '--env', 'prod',
            '--loglevel', 'error',
            '--host', '0.0.0.0',
            '--port', os.environ.get('PORT', '8080')
        ]
        
        logger.info(f"Ejecutando: {' '.join(cmd)}")
        
        # Ejecutar con manejo de errores
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy(),
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitorear el proceso
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Filtrar mensajes problemáticos de Rich
                if '[/usr/bin/node]' not in output and 'MarkupError' not in output:
                    print(output.strip())
        
        rc = process.poll()
        return rc == 0
        
    except Exception as e:
        logger.error(f"✗ Error ejecutando Reflex: {e}")
        return False

def main():
    """Función principal"""
    logger.info("=== Railway Final Fix - Iniciando ===")
    
    # 1. Configurar entorno
    setup_railway_environment()
    logger.info("✓ Entorno configurado")
    
    # 2. Verificar dependencias
    if not check_dependencies():
        logger.error("✗ Dependencias no disponibles")
        sys.exit(1)
    
    # 3. Limpiar cache si es necesario
    if os.environ.get('CLEAN_CACHE', 'false').lower() == 'true':
        clean_reflex_cache()
    
    # 4. Inicializar Reflex de forma segura
    if not os.path.exists('.web') or os.environ.get('FORCE_INIT', 'false').lower() == 'true':
        if not init_reflex_safe():
            logger.error("✗ Falló inicialización de Reflex")
            sys.exit(1)
    
    # 5. Ejecutar aplicación
    logger.info("🚀 Iniciando aplicación...")
    if not run_reflex_production():
        logger.error("✗ Falló ejecución de la aplicación")
        sys.exit(1)

if __name__ == "__main__":
    main()
