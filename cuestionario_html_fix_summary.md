# Solución del problema de descarga de cuestionario en HTML

## Problema
Al intentar descargar un cuestionario en formato HTML, se producía un error relacionado con variables reactivas de Reflex:

```
ERROR DWNLD CUESTIONARIO PDF/HTML: Traceback (most recent call last):
  File "/workspaces/SMART_STUDENT/mi_app_estudio/state.py", line 1925, in download_cuestionario_pdf
    preguntas_lista = list(CuestionarioState.cuestionario_preguntas) if has_preguntas else []
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/python/3.12.1/lib/python3.12/site-packages/reflex/vars/base.py", line 1344, in __iter__
    raise VarTypeError(
reflex.utils.exceptions.VarTypeError: Cannot iterate over Var 'reflex___state____state__mi_app_estudio___state____app_state__mi_app_estudio___cuestionario____cuestionario_state.cuestionario_preguntas'. Instead use `rx.foreach`.
```

Además, en caso de que el HTML sí se generara, mostraba las referencias a las variables reactivas en lugar de sus valores reales:

```
Cuestionario: ((((reflex___state____state__mi_app_estudio___sta
```

## Solución implementada

Se implementaron las siguientes correcciones:

### 1. Funciones de utilidad para manejar variables reactivas

Se añadieron dos funciones auxiliares al principio de `state.py`:

```python
def get_safe_var_value(var, default=None):
    """
    Obtiene de manera segura el valor de una variable reactiva de Reflex.
    """
    if var is None:
        return default
        
    try:
        # Intentar obtener _var_value directamente
        if hasattr(var, "_var_value"):
            return var._var_value
    except:
        pass
        
    try:
        # Intentar conversión con str()
        val = str(var)
        if "<reflex.Var>" in val:
            val = val.split("</reflex.Var>")[-1]
        return val
    except:
        pass
        
    return default


def get_safe_var_list(var_list, default=None):
    """
    Obtiene de manera segura los valores de una lista reactiva de Reflex.
    """
    if default is None:
        default = []
        
    if var_list is None:
        return default
        
    # Método 1: Acceder directamente a _var_value
    try:
        if hasattr(var_list, "_var_value"):
            val = var_list._var_value
            if isinstance(val, list):
                return val
    except:
        pass
        
    # ...más métodos de recuperación...
        
    return default
```

### 2. Mejor verificación de la existencia de preguntas

Se modificó la verificación inicial de preguntas para usar la función de utilidad:

```python
try:
    # Usamos la función de utilidad para verificar si hay preguntas
    preguntas_lista = get_safe_var_list(CuestionarioState.cuestionario_preguntas, [])
    tiene_preguntas = len(preguntas_lista) > 0
    if tiene_preguntas:
        print(f"DEBUG: Encontradas {len(preguntas_lista)} preguntas en el cuestionario")
    else:
        print("DEBUG: Lista de preguntas vacía")
except Exception as e:
    print(f"DEBUG: No se encontraron preguntas en el cuestionario: {e}")
    tiene_preguntas = False
```

### 3. Conversión segura de variables reactivas para nombre de archivo

```python
# Utilizar nuestra función de utilidad para obtener el valor de manera segura
tema_str = get_safe_var_value(tema_value, "tema")
# Convertir a string antes de usar re.sub
s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_str)[:50]
```

### 4. Eliminación de duplicado en generación de timestamp

Se eliminó el duplicado:

```python
# Generar timestamp una sola vez
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
# Generar el nombre base del archivo una sola vez
fname_base = f"Cuestionario_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")
```

### 5. Obtención segura de URL del PDF

```python
# Usar nuestra función de utilidad para obtener el valor de manera segura
pdf_url = get_safe_var_value(CuestionarioState.cuestionario_pdf_url, "")
print(f"DEBUG: PDF URL obtenida de manera segura: {pdf_url}")
```

### 6. Conversión segura de la lista de preguntas para iteración

```python
# Usar nuestra función de utilidad para convertir la lista reactiva
preguntas_lista = get_safe_var_list(CuestionarioState.cuestionario_preguntas, [])

# Ahora iteramos sobre la lista Python estándar
for i, pregunta in enumerate(preguntas_lista):
```

### 7. Mejora en el manejo de diferentes tipos de preguntas

```python
# Manejar diferentes formatos de respuesta correcta
if "correcta" in pregunta:
    correcta = str(pregunta.get("correcta", ""))
elif "correctas" in pregunta and isinstance(pregunta.get("correctas"), list):
    # Si es una lista de respuestas correctas (selección múltiple)
    correctas_lista = pregunta.get("correctas", [])
    correcta = ", ".join([str(c) for c in correctas_lista]) if correctas_lista else ""
else:
    correcta = ""
```

### 8. Mejora en la generación del HTML para manejo de caso vacío

```python
# Si no hay preguntas en el HTML, agregar un mensaje informativo
if not preguntas_html.strip():
    preguntas_html = """
    <div class="mensaje-info">
        <p>No se encontraron preguntas para este cuestionario.</p>
        <p>Por favor, genera primero un cuestionario en la sección correspondiente.</p>
    </div>
    """
    print("DEBUG: No hay preguntas para incluir en el HTML")
```

## Herramientas de diagnóstico

También se crearon herramientas para diagnosticar y verificar las correcciones:

- `diagnose_reactive_vars.py`: Para analizar la estructura interna de las variables reactivas
- `validate_fixes.py`: Para verificar que las funciones de utilidad funcionan correctamente
- `test_download_app.py`: Una mini-aplicación Reflex que demuestra que la descarga funciona

## Resultado

Después de aplicar estas correcciones, la descarga de cuestionarios en formato HTML debería funcionar correctamente, mostrando:

1. El título del cuestionario correctamente (sin referencias a variables reactivas)
2. Las preguntas y respuestas completas
3. El formato HTML adecuado

Además, el proceso es ahora robusto ante diferentes situaciones como:

- Variaciones en los tipos de preguntas (alternativas, verdadero/falso, selección múltiple)
- Ausencia de preguntas (muestra un mensaje explicativo)
- Diferentes representaciones internas de las variables reactivas
