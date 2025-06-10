#!/usr/bin/env python3
"""
Solución definitiva para Railway - Modo desarrollo sin build de producción
Evita completamente el JavaScript heap out of memory
"""
import os
import sys
import subprocess
import time
import signal

def setup_dev_environment():
    """Configurar entorno de desarrollo optimizado para Railway"""
    # Variables básicas de Railway
    os.environ['PORT'] = os.environ.get('PORT', '8080')
    os.environ['HOST'] = '0.0.0.0'
    
    # FORZAR modo desarrollo para evitar build pesado
    os.environ['REFLEX_ENV'] = 'dev'
    os.environ['REFLEX_DEBUG'] = 'false'
    os.environ['REFLEX_DISABLE_TELEMETRY'] = 'true'
    
    # Optimizaciones críticas de memoria
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=128 --optimize-for-size --gc-interval=100'
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['PYTHONPATH'] = '/app'
    
    # Variables para evitar errores
    os.environ['REFLEX_SKIP_COMPILE'] = 'true'
    os.environ['NEXT_TELEMETRY_DISABLED'] = '1'
    
    print("✓ Entorno de desarrollo configurado")

def clean_build_artifacts():
    """Limpiar artefactos de build que pueden causar problemas"""
    import shutil
    
    artifacts = ['.web', '.reflex', 'node_modules', '__pycache__', '.next']
    
    for artifact in artifacts:
        if os.path.exists(artifact):
            try:
                if os.path.isdir(artifact):
                    shutil.rmtree(artifact)
                else:
                    os.remove(artifact)
                print(f"✓ Limpiado: {artifact}")
            except Exception as e:
                print(f"⚠ No se pudo limpiar {artifact}: {e}")

def run_reflex_dev_safe():
    """
    Ejecutar Reflex en modo desarrollo de forma segura
    Sin build de producción, sin errores de memoria
    """
    try:
        print("🚀 Iniciando Reflex en modo desarrollo...")
        
        # Comando simplificado para desarrollo
        cmd = [
            sys.executable, '-m', 'reflex', 'run',
            '--env', 'dev',  # MODO DESARROLLO
            '--backend-host', '0.0.0.0',
            '--backend-port', os.environ.get('PORT', '8080'),
            '--frontend-port', os.environ.get('PORT', '8080'),
            '--loglevel', 'error'  # Reducir logs para evitar Rich errors
        ]
        
        print(f"📡 Servidor iniciando en puerto {os.environ.get('PORT', '8080')}")
        print(f"🔧 Comando: {' '.join(cmd)}")
        
        # Ejecutar con manejo de señales
        def signal_handler(signum, frame):
            print("\n🛑 Deteniendo servidor...")
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Ejecutar el proceso
        process = subprocess.run(cmd, env=os.environ.copy())
        
        return process.returncode == 0
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
        return True
    except Exception as e:
        print(f"❌ Error ejecutando Reflex: {e}")
        return False

def fallback_direct_import():
    """
    Método de respaldo: importar y ejecutar directamente la app
    Sin usar reflex run para evitar todos los problemas de build
    """
    try:
        print("🔄 Intentando método de respaldo...")
        
        # Importar directamente
        import reflex as rx
        print("✓ Reflex importado")
        
        # Configurar Reflex para desarrollo
        import rxconfig
        print("✓ Configuración cargada")
        
        # Importar la app
        from mi_app_estudio.mi_app_estudio import app
        print("✓ App importada")
        
        # Ejecutar directamente sin reflex CLI
        print(f"🌐 Servidor directo en puerto {os.environ.get('PORT', '8080')}")
        
        # Usar el método interno de Reflex
        app._run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', '8080')),
            debug=False
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Error en método de respaldo: {e}")
        return False

def main():
    """Función principal con múltiples estrategias de recuperación"""
    print("=" * 60)
    print("🏥 RAILWAY DEV MODE FIX - Solución definitiva")
    print("=" * 60)
    
    # 1. Configurar entorno
    setup_dev_environment()
    
    # 2. Limpiar artefactos problemáticos
    print("\n🧹 Limpiando artefactos de build...")
    clean_build_artifacts()
    
    # 3. Verificar que las importaciones funcionan
    try:
        import reflex as rx
        print("✓ Reflex disponible")
        
        from mi_app_estudio.mi_app_estudio import app
        print("✓ App disponible")
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        sys.exit(1)
    
    # 4. Intentar ejecución en modo desarrollo
    print("\n🚀 Método 1: Reflex run en modo desarrollo")
    if run_reflex_dev_safe():
        print("✅ Éxito con reflex run")
        return
    
    # 5. Método de respaldo: importación directa
    print("\n🔄 Método 2: Importación directa (respaldo)")
    if fallback_direct_import():
        print("✅ Éxito con importación directa")
        return
    
    # 6. Si todo falla
    print("\n❌ Todos los métodos fallaron")
    print("💡 Sugerencias:")
    print("   - Verificar variables de entorno")
    print("   - Revisar logs de Railway")
    print("   - Considerar aumentar memoria en Railway")
    
    sys.exit(1)

if __name__ == "__main__":
    main()
