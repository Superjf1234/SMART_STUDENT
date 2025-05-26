# Corrección Error StringCastedVar en descarga de PDF

## Problema
El error ocurrió al intentar utilizar un objeto `StringCastedVar` (devuelto por `rx.cond()`) con la función `re.sub()`, que espera un objeto string o bytes.

```
TypeError: expected string or bytes-like object, got 'StringCastedVar'
```

El error específicamente ocurría en esta línea:
```python
s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_value)[:50]
```

donde `tema_value` era un objeto `StringCastedVar` obtenido mediante `rx.cond()`.

## Solución
La solución consiste en convertir explícitamente el objeto `StringCastedVar` a un string usando la función `str()` antes de pasarlo a `re.sub()`:

```python
s_tema = re.sub(r'[\\/*?:"<>|]', "", str(tema_value))[:50]
```

Este patrón se aplica también a las variables `libro_value` y `curso_value` que tienen el mismo problema.

## Archivos modificados
- `/workspaces/SMART_STUDENT/mi_app_estudio/state.py`

## Pruebas realizadas
- Se ha creado un script de prueba (`test_string_cast_fix.py`) que verifica que la solución funcione correctamente.
- Se ha creado un script de corrección (`fix_string_cast_pdf.py`) que puede aplicarse a otras instalaciones con el mismo problema.

## Conceptos técnicos
- Cuando se utilizan funciones condicionales de Reflex como `rx.cond()`, estas devuelven tipos especiales (como `StringCastedVar`) que pueden comportarse como strings en muchos contextos, pero no son strings nativos de Python.
- Las funciones que esperan tipos específicos de Python (como `re.sub()` que espera strings) requieren una conversión explícita mediante `str()`.

## Recomendaciones
1. Siempre convertir explícitamente a string (`str()`) los valores devueltos por `rx.cond()` antes de usarlos en funciones como `re.sub()`.
2. Hacer pruebas unitarias específicas para las funciones que manejan tipos de datos especiales de Reflex.
