# 🚨 GUÍA DE TROUBLESHOOTING - Railway Rich MarkupError

## ⚡ SOLUCIÓN RÁPIDA ACTUAL

**Status:** ✅ **IMPLEMENTADO**  
**Script Activo:** `emergency_railway_simple.py`  
**Procfile:** `web: python emergency_railway_simple.py`

---

## 🔍 VERIFICAR DEPLOYMENT

### 1. Ejecutar Monitor
```bash
python railway_deployment_monitor.py
```

### 2. Verificar Logs en Railway
- Dashboard > Deploy Logs
- Buscar: "🚀 Iniciando Smart Student..."
- Confirmar: "✓ Reflex importado" y "✓ App importada"

---

## 🚨 SI AÚN HAY ERRORES

### Opción 1: Script Robusto
```bash
# Cambiar Procfile a:
web: python railway_final_fix.py
```

### Opción 2: Script Ultra-Minimal  
```bash
# Cambiar Procfile a:
web: python ultra_minimal_railway.py
```

### Opción 3: Requirements Mínimos
```bash
# Usar requirements_minimal.txt
cp requirements_minimal.txt requirements.txt
```

---

## 🔧 VARIABLES DE ENTORNO CRÍTICAS

Verificar en Railway Dashboard que estén configuradas:

```
REFLEX_ENV=dev
REFLEX_DISABLE_TELEMETRY=true  
REFLEX_DEBUG=false
NODE_OPTIONS=--max-old-space-size=256
PYTHONUNBUFFERED=1
GEMINI_API_KEY=tu_api_key_aqui
```

---

## 🩺 DIAGNÓSTICO DE ERRORES

### Error: Rich MarkupError
**Síntoma:** `closing tag '[/usr/bin/node]'`  
**Solución:** ✅ Ya implementada con emergency_railway_simple.py

### Error: Out of Memory
**Síntoma:** `Deploy Ran Out of Memory`  
**Solución:** 
1. Verificar NODE_OPTIONS=--max-old-space-size=256
2. Usar requirements_minimal.txt
3. Confirmar REFLEX_ENV=dev

### Error: Module Not Found
**Síntoma:** `ModuleNotFoundError: No module named 'mi_app_estudio'`  
**Solución:** Verificar estructura de archivos y PYTHONPATH

---

## 📋 CHECKLIST DE VERIFICACIÓN

- [ ] ✅ Procfile apunta a emergency_railway_simple.py
- [ ] ✅ Script existe y es ejecutable  
- [ ] ✅ Variables de entorno configuradas
- [ ] ✅ Git push completado
- [ ] ✅ Railway redeploy automático activado

---

## 🆘 CONTACTO DE EMERGENCIA

Si todos los scripts fallan:

1. **Rollback:** Usar commit anterior que funcionaba
2. **Debug:** Activar logs detallados temporalmente
3. **Alternativa:** Usar Dockerfile simple

---

**Última actualización:** 10 de Junio, 2025  
**Estado:** 🟢 SOLUCIONADO
