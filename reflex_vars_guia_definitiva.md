# Guía definitiva: Variables reactivas en Reflex

## Problema principal

En Reflex, las variables reactivas (también conocidas como "Vars") no pueden ser utilizadas directamente en construcciones estándar de Python como:

1. Condiciones: `if`, `and`, `or`, `not`
2. Bucles: `for`, `while`
3. Iteraciones: `for item in lista_reactiva`
4. Funciones Python que esperan tipos específicos

## Soluciones para cada caso

### Solución 1: StringCastedVar con funciones Python

**Problema:** Al usar una variable reactiva con una función que espera un string.
```python
# ERROR ❌
s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_value)[:50]
```

**Solución correcta:** Convertir explícitamente a string.
```python
# CORRECTO ✅
s_tema = re.sub(r'[\\/*?:"<>|]', "", str(tema_value))[:50]
```

### Solución 2: VarTypeError en condicionales if

**Problema:** Usar una variable reactiva en una condición `if`.
```python
# ERROR ❌
pdf_url_not_empty = CuestionarioState.cuestionario_pdf_url != ""
if pdf_url_not_empty:  # ❌ Error - pdf_url_not_empty es una Var
    # código
```

**Solución correcta:** Convertir a variables Python estándar.
```python
# CORRECTO ✅
# 1. Convertir variable reactiva a Python estándar
has_pdf_url = hasattr(CuestionarioState, "cuestionario_pdf_url")
pdf_url = str(CuestionarioState.cuestionario_pdf_url) if has_pdf_url else ""
is_pdf_url_not_empty = pdf_url != ""

# 2. Usar la variable Python estándar en la condición
if is_pdf_url_not_empty:
    # código
```

### Solución 3: Funciones o lambdas en rx.cond()

**Problema:** Usar funciones definidas o lambdas en `rx.cond()`.
```python
# ERROR ❌
def process_url():
    return str(url).lstrip('/')

pdf_path = rx.cond(
    condition,
    process_url,  # ❌ Error
    lambda: ""    # ❌ Error
)
```

**Solución correcta:** Evitar `rx.cond()` para lógica compleja y usar condicionales Python estándar.
```python
# CORRECTO ✅
has_url = hasattr(Class, "url")
url_str = str(Class.url) if has_url else ""
is_url_not_empty = url_str != ""

if is_url_not_empty:
    pdf_path = url_str.lstrip('/')
else:
    pdf_path = ""
```

### Solución 4: Iteración sobre listas reactivas

**Problema:** Iterar directamente sobre una lista reactiva.
```python
# ERROR ❌
for i, pregunta in enumerate(CuestionarioState.cuestionario_preguntas):
    # código
```

**Solución correcta:** Convertir a una lista Python estándar.
```python
# CORRECTO ✅
# 1. Verificar si el atributo existe
has_preguntas = hasattr(CuestionarioState, "cuestionario_preguntas")

# 2. Convertir a lista Python estándar
preguntas_lista = list(CuestionarioState.cuestionario_preguntas) if has_preguntas else []

# 3. Iterar sobre la lista Python estándar
for i, pregunta in enumerate(preguntas_lista):
    # código
```

## Reglas de oro para Reflex

1. **Nunca** usar variables reactivas directamente en:
   - Condiciones `if`, `and`, `or`, `not`
   - Bucles `for`, `while`
   - Iteraciones `for item in lista_reactiva`
   - Funciones que esperan tipos específicos

2. **Siempre** convertir a tipos Python estándar:
   - `python_str = str(var_reactiva)`
   - `python_int = int(var_reactiva)`
   - `python_bool = python_str != ""` (después de convertir a string)
   - `python_list = list(lista_reactiva)`

3. Para **comparaciones** con variables reactivas:
   - Primero crear variables Python estándar de las comparaciones
   - Luego usar esas variables en la lógica condicional

4. Para **condicionales complejos** con bifurcaciones:
   - Evitar `rx.cond()` para lógica compleja que requiera funciones
   - Usar condicionales Python estándar con variables no reactivas

## Ejemplos adicionales

### Ejemplo 1: Manejo seguro de atributos que podrían no existir

```python
# Verificar si el atributo existe
has_attribute = hasattr(MyState, "some_attribute")

# Obtener valor de forma segura
attribute_value = str(MyState.some_attribute) if has_attribute else ""

# Usar en condicional
if attribute_value != "":
    # código
```

### Ejemplo 2: Convertir valores numéricos

```python
# Variables reactivas
reactivo_a = MyState.valor_a
reactivo_b = MyState.valor_b

# Convertir a Python estándar
python_a = int(reactivo_a) if str(reactivo_a).isdigit() else 0
python_b = int(reactivo_b) if str(reactivo_b).isdigit() else 0

# Ahora podemos hacer operaciones aritméticas
resultado = python_a + python_b
```

### Ejemplo 3: Listas reactivas

```python
# Lista reactiva
lista_reactiva = MyState.mi_lista

# Convertir a lista Python estándar
lista_python = list(lista_reactiva) if hasattr(MyState, "mi_lista") else []

# Ahora podemos iterar
for item in lista_python:
    # código
```

### Ejemplo 4: Diccionarios reactivos

```python
# Diccionario reactivo
dict_reactivo = MyState.mi_dict

# Convertir a diccionario Python estándar
dict_python = dict(dict_reactivo) if hasattr(MyState, "mi_dict") else {}

# Ahora podemos iterar o acceder
for key, value in dict_python.items():
    # código
```

## Resumen de lo aprendido

Las variables reactivas en Reflex son especiales y tienen limitaciones. La clave para evitar errores es siempre convertirlas a tipos Python estándar antes de usarlas en lógica de programación Python convencional. Esta conversión asegura que tu código funcione correctamente sin errores como `StringCastedVar`, `VarTypeError`, o problemas con iteraciones y funciones.
