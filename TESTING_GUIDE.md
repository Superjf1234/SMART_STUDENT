# 🧪 Guía de Testing - SMART STUDENT

## 📋 Resumen de Tests

Este proyecto incluye múltiples suites de tests optimizadas para diferentes entornos:

### 🤖 **Tests para CI/CD (GitHub Actions)**
- **Archivo**: `test_ci_optimized.py`
- **Propósito**: Tests rápidos y estables para CI/CD
- **Características**: Sin inicio de servidor, solo verificación de compilación

### 🏠 **Tests Locales Completos**
- **Archivo**: `test_railway_local.py` 
- **Propósito**: Tests completos incluyendo inicio de servidor
- **Características**: Incluye limpieza de puertos y tests de ejecución

### ⚡ **Tests Unitarios Básicos**
- **Carpeta**: `tests/`
- **Archivos**: `test_basic.py`, `test_config.py`, `test_utils.py`
- **Propósito**: Tests de funcionalidades específicas

## 🚀 Cómo Ejecutar Tests

### **Localmente (Desarrollo)**
```bash
# Todos los tests
pytest

# Solo tests rápidos (sin servidor)
pytest test_ci_optimized.py

# Solo tests unitarios
pytest tests/

# Excluir tests lentos
pytest -m "not slow"

# Test específico de Railway (local)
pytest test_railway_local.py::test_imports
pytest test_railway_local.py::test_reflex_init
```

### **Para CI/CD (GitHub Actions)**
```bash
# Tests optimizados para CI
pytest test_ci_optimized.py -v

# Tests básicos sin servidor
pytest tests/ -m "not slow" -v

# Tests de importación únicamente
pytest test_utils_import.py test_bilingual_parsing.py -v
```

### **Simulación Railway Local**
```bash
# Test completo de Railway (incluye servidor)
python test_railway_local.py

# Solo verificación de importaciones
python -c "import mi_app_estudio; print('✅ Imports OK')"
```

## 🔧 Configuración de Tests

### **Variables de Entorno para Tests**
```bash
# Para desarrollo local
export REFLEX_ENV=dev
export NODE_ENV=development  
export PORT=8080

# Para CI/CD
export CI=true
export GITHUB_ACTIONS=true
export NODE_OPTIONS=--max-old-space-size=512
```

### **Marcadores de Tests**
- `@pytest.mark.slow` - Tests que toman tiempo
- `@pytest.mark.skipif(CI)` - Omitir en CI/CD
- `@pytest.mark.integration` - Tests de integración
- `@pytest.mark.unit` - Tests unitarios

## 🚨 Problemas Comunes y Soluciones

### **Error: TimeoutExpired en CI**
```
subprocess.TimeoutExpired: Command timed out after 5 seconds
```
**Solución**: El test `test_reflex_run` se omite automáticamente en CI.

### **Error: Address already in use**
```
OSError: [Errno 98] Address already in use
```
**Solución**: 
```bash
python clean_port.py 8080
pytest test_railway_local.py
```

### **Error: Memory issues en CI**
```
JavaScript heap out of memory
```
**Solución**: Los tests CI usan `NODE_OPTIONS=--max-old-space-size=512`

## 📊 Estructura de Tests

```
📁 Tests/
├── 🤖 test_ci_optimized.py      # CI/CD optimizado
├── 🏠 test_railway_local.py     # Local completo  
├── 📝 test_bilingual_parsing.py # Parsing bilingüe
├── ✅ test_correct_markers.py   # Marcadores
├── 🔧 test_utils_import.py      # Utilidades
└── 📁 tests/                    # Tests unitarios
    ├── test_basic.py
    ├── test_config.py
    └── test_utils.py
```

## 🎯 Tests por Entorno

| Entorno | Comando | Archivos | Tiempo |
|---------|---------|----------|---------|
| **GitHub Actions** | `pytest test_ci_optimized.py` | CI optimizado | ~2 min |
| **Local Development** | `pytest` | Todos | ~5 min |
| **Railway Simulation** | `python test_railway_local.py` | Railway local | ~3 min |
| **Quick Check** | `pytest tests/ -m "not slow"` | Solo unitarios | ~30 seg |

## 🔍 Debug de Tests

### **Ver output detallado**
```bash
pytest -v -s test_ci_optimized.py
```

### **Ver solo errores**
```bash
pytest --tb=short --disable-warnings
```

### **Test específico con debug**
```bash
pytest test_railway_local.py::test_imports -v -s
```

### **Verificar que scripts existen**
```bash
ls -la railway_memory_fix.py final_port_fix.py clean_port.py
```

## ✅ Verificación de Éxito

Un test suite exitoso debe mostrar:
```
✅ Imports OK
✅ Reflex init OK  
✅ Compilation OK
✅ Basic functionality OK
✅ All solution scripts present

=== X passed, 0 failed ===
```

---

**💡 Tip**: Para desarrollo diario, usa `pytest test_ci_optimized.py` para un check rápido.
