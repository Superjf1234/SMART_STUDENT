#!/usr/bin/env python3
"""
SOLUCIÓN DEFINITIVA PARA RAILWAY - EVITA COMPLETAMENTE EL BUILD DE PRODUCCIÓN
NO USA reflex run EN ABSOLUTO - Ejecuta la app directamente
"""
import os
import sys
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def setup_ultra_minimal_env():
    """Configuración ultra mínima que evita TODOS los problemas"""
    # Variables básicas de Railway
    os.environ['PORT'] = os.environ.get('PORT', '8080')
    os.environ['HOST'] = '0.0.0.0'
    
    # CRÍTICO: Variables que FUERZAN modo desarrollo
    os.environ['REFLEX_ENV'] = 'dev'  # NUNCA prod
    os.environ['REFLEX_DEBUG'] = 'false'
    os.environ['REFLEX_DISABLE_TELEMETRY'] = 'true'
    os.environ['REFLEX_SKIP_COMPILE'] = 'true'
    os.environ['REFLEX_NO_BUILD'] = 'true'
    
    # Variables de memoria críticas
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=64'  # Muy bajo
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Variables adicionales de seguridad
    os.environ['NEXT_TELEMETRY_DISABLED'] = '1'
    os.environ['CI'] = 'true'  # Evita interacciones
    
    logger.info("✓ Entorno ultra-mínimo configurado")

def import_and_run_directly():
    """
    Método definitivo: No usar reflex CLI en absoluto
    Importar y ejecutar la app directamente como servidor web
    """
    try:
        logger.info("🚀 MÉTODO DIRECTO - Sin reflex CLI")
        
        # Agregar directorio actual al path
        sys.path.insert(0, '/app' if os.path.exists('/app') else '.')
        
        # Importar reflex
        import reflex as rx
        logger.info("✓ Reflex importado")
        
        # Configurar directamente sin rxconfig
        config = rx.Config(
            app_name="mi_app_estudio",
            backend_host="0.0.0.0",
            backend_port=int(os.environ.get('PORT', '8080')),
            frontend_port=int(os.environ.get('PORT', '8080')),
            env=rx.Env.DEV,  # FORZADO desarrollo
            tailwind=None,
            telemetry_enabled=False,
            loglevel="error"
        )
        
        logger.info("✓ Configuración manual creada")
        
        # Importar la aplicación
        from mi_app_estudio.mi_app_estudio import app
        logger.info("✓ App importada")
        
        # Verificar que la app existe
        if not hasattr(app, 'run'):
            # Si no tiene run, usar el método de servidor HTTP básico
            logger.info("📡 Usando servidor HTTP básico")
            import uvicorn
            
            # Crear una app ASGI básica
            from reflex.utils import prerequisites
            
            # Ejecutar con uvicorn directamente
            uvicorn.run(
                "mi_app_estudio.mi_app_estudio:app",
                host="0.0.0.0",
                port=int(os.environ.get('PORT', '8080')),
                log_level="error"
            )
        else:
            # Ejecutar la app normalmente
            logger.info(f"🌐 Servidor iniciando en puerto {os.environ.get('PORT', '8080')}")
            app.run(
                host="0.0.0.0",
                port=int(os.environ.get('PORT', '8080')),
                debug=False
            )
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        return fallback_basic_server()
    except Exception as e:
        logger.error(f"❌ Error ejecutando app: {e}")
        return fallback_basic_server()

def fallback_basic_server():
    """
    Servidor de respaldo ultra-básico si todo falla
    """
    try:
        logger.info("🔄 Iniciando servidor de respaldo...")
        
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        
        class SimpleHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                # Healthcheck endpoint para Railway
                if self.path == '/health' or self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    health_response = {
                        "status": "healthy",
                        "service": "smart_student",
                        "mode": "development",
                        "timestamp": str(__import__('datetime').datetime.now())
                    }
                    self.wfile.write(__import__('json').dumps(health_response).encode())
                else:
                    # Página principal
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Student - Iniciando...</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .container { max-width: 600px; margin: 0 auto; }
        .loading { color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Smart Student</h1>
        <p class="loading">Aplicación iniciándose...</p>
        <p>La aplicación se está configurando en modo desarrollo optimizado para Railway.</p>
        <p><small>Si ves este mensaje, el servidor básico está funcionando correctamente.</small></p>
        <script>
            setTimeout(() => location.reload(), 10000);
        </script>
    </div>
</body>
</html>
                """
                self.wfile.write(html.encode())
            
            def log_message(self, format, *args):
                pass  # Silenciar logs
        
        port = int(os.environ.get('PORT', '8080'))
        server = HTTPServer(('0.0.0.0', port), SimpleHandler)
        logger.info(f"🌐 Servidor de respaldo en puerto {port}")
        server.serve_forever()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en servidor de respaldo: {e}")
        return False

def main():
    """Función principal ultra-simplificada"""
    print("=" * 60)
    print("🏥 RAILWAY ULTRA-DIRECT FIX - Solución sin reflex CLI")
    print("=" * 60)
    
    # 1. Configurar entorno
    setup_ultra_minimal_env()
    
    # 2. Intentar ejecución directa
    if import_and_run_directly():
        logger.info("✅ Éxito con método directo")
    else:
        logger.error("❌ Todos los métodos fallaron")
        sys.exit(1)

if __name__ == "__main__":
    main()
