# Guía completa para solucionar errores de tipo en Reflex

Este documento recopila soluciones para los tres tipos de errores de tipo comunes al trabajar con Reflex.

## 1. Error: StringCastedVar en funciones estándar de Python

**Síntoma**: Error al usar variables reactivas con funciones estándar como `re.sub()` que esperan strings.

```
TypeError: expected string or bytes-like object, got 'StringCastedVar'
```

**Solución**: Convertir explícitamente la variable reactiva a string usando `str()`.

```python
# INCORRECTO ❌
s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_value)[:50]

# CORRECTO ✅
s_tema = re.sub(r'[\\/*?:"<>|]', "", str(tema_value))[:50]
```

## 2. Error: VarTypeError en condicionales

**Síntoma**: Error al usar variables reactivas en condicionales `if`, `and`, `or`, `not`.

```
VarTypeError: Cannot convert Var to bool for use with `if`, `and`, `or`, and `not`. Instead use `rx.cond`...
```

**Solución**: Usar `rx.cond()` en lugar de condicionales directas.

```python
# INCORRECTO ❌
pdf_url_not_empty = rx.cond(
    CuestionarioState.cuestionario_pdf_url != "",
    True,
    False
)
if pdf_url_not_empty:
    # código

# CORRECTO ✅
pdf_url_empty = CuestionarioState.cuestionario_pdf_url == ""

# Opción 1: Usar variables Python normales derivadas de comparaciones
is_empty = pdf_url_empty
if not is_empty:
    # código

# Opción 2: Usar rx.cond() para bifurcaciones
rx.cond(
    ~pdf_url_empty,
    lambda: función_true(),
    lambda: función_false()
)
```

## 3. Error: Funciones definidas localmente en rx.cond()

**Síntoma**: Error al pasar una función definida localmente a `rx.cond()`.

```
TypeError: Unsupported type <class 'function'> for LiteralVar. Tried to create a LiteralVar from <function...>
```

**Solución**: Usar expresiones lambda directamente en lugar de funciones definidas.

```python
# INCORRECTO ❌
def process_with_url():
    print(f"DEBUG: URL: {url}")
    return str(url).lstrip('/')

pdf_path = rx.cond(
    ~url_empty,
    process_with_url,  # ❌ Función definida localmente
    lambda: ""
)

# CORRECTO ✅
pdf_path = rx.cond(
    ~url_empty,
    lambda: str(url).lstrip('/'),  # ✅ Lambda directamente
    lambda: ""
)

# Manejar código auxiliar fuera de rx.cond()
if not url_empty:
    print(f"DEBUG: URL: {url}")
```

## Buenas prácticas generales para Reflex

### Variables reactivas

1. **Conversión de tipos**: Convertir variables reactivas a tipos Python básicos antes de usarlas con funciones estándar.
   ```python
   str(var_reactiva), int(var_reactiva), float(var_reactiva)
   ```

2. **Concatenación de strings**: Usar conversión a string explícita antes de concatenar.
   ```python
   f"Texto: {str(var_reactiva)}"
   ```

### Condicionales

1. **Comparaciones**: Usar comparaciones explícitas en lugar de conversión implícita a booleano.
   ```python
   var == ""  # en lugar de if var:
   var != ""  # en lugar de if var:
   ```

2. **Operadores lógicos**: Usar operadores bitwise en lugar de operadores lógicos.
   ```python
   (condicion_a & condicion_b)  # en lugar de (condicion_a and condicion_b)
   (condicion_a | condicion_b)  # en lugar de (condicion_a or condicion_b)
   ~condicion  # en lugar de not condicion
   ```

3. **Bifurcaciones condicionales**: Usar `rx.cond()` para lógica condicional con variables reactivas.
   ```python
   resultado = rx.cond(
       condicion,
       lambda: valor_si_true,
       lambda: valor_si_false
   )
   ```

### Funciones

1. **Lambdas vs. funciones**: Usar lambdas en `rx.cond()` en lugar de funciones definidas.
   ```python
   # En lugar de:
   def my_func(): return valor
   rx.cond(condicion, my_func, lambda: otro_valor)
   
   # Usar:
   rx.cond(condicion, lambda: valor, lambda: otro_valor)
   ```

2. **Código auxiliar**: Mover código auxiliar complejo fuera de las expresiones lambda.
   ```python
   # Preparar valores antes de rx.cond()
   valor_complejo = calcular_algo()
   
   # Usar valores preparados en lambdas simples
   rx.cond(condicion, lambda: valor_complejo, lambda: otro_valor)
   ```

## Scripts de corrección incluidos

1. `fix_string_cast_pdf.py`: Corrige problemas de StringCastedVar con re.sub()
2. `fix_var_type_error.py`: Corrige problemas de VarTypeError en condicionales if
3. `fix_functions_in_rxcond.py`: Corrige problemas de funciones definidas en rx.cond()
4. `fix_reflex_type_issues.py`: Solución completa para los tres problemas
5. `test_pdf_download_complete.py`: Verifica que las soluciones estén aplicadas correctamente

## Referencias

1. [Documentación oficial de Reflex sobre Vars](https://reflex.dev/docs/vars/overview/)
2. [Patrones condicionales en Reflex](https://reflex.dev/docs/library/layout/cond/)
3. [Mejores prácticas para aplicaciones Reflex](https://reflex.dev/docs/best-practices/overview/)
