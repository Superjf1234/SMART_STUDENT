# Railway Configuration for SMART_STUDENT

## Variables de entorno requeridas en Railway:
```
REFLEX_ENV=prod
NODE_ENV=production
PYTHONPATH=/app
GEMINI_API_KEY=tu_clave_api_aqui
```

## Configuración del servicio:
- **Memoria**: 2GB mínimo (recomendado 4GB para 32GB plan)
- **CPU**: 2 vCPU mínimo
- **Timeout**: 300 segundos
- **Puerto**: 8080 (automático con $PORT)

## Healthcheck:
- **Path**: `/` 
- **Timeout**: 300s
- **Retries**: 3

## Comandos de despliegue:
1. Hacer commit de todos los cambios
2. Subir a repositorio conectado a Railway
3. Railway detectará Dockerfile automáticamente
4. El healthcheck usará el endpoint `/health` configurado

## Archivos importantes:
- `Dockerfile` - Configuración optimizada
- `Procfile` - Comando de inicio
- `railway_simple_start.py` - Script de inicio simplificado
- `requirements.optimized.txt` - Dependencias optimizadas
