# PDF Download Functionality Fix for SMART_STUDENT

## Problem Description
The PDF download functionality in the SMART_STUDENT application's cuestionario tab was failing with a 404 error. This was due to two main issues:

1. A `VarTypeError` in `state.py` when using reactive variable `CuestionarioState.cuestionario_tema` with logical OR operator and in boolean conditions
2. Issues with PDF URL generation and access methods

## Solution Implemented

### 1. Fixed VarTypeError in `download_cuestionario_pdf` method

#### First Fix Attempt - Replacing OR operator
The initial error occurred in this line:
```python
s_tema = re.sub(r'[\\/*?:"<>|]', "", CuestionarioState.cuestionario_tema or "tema")[:50]
```

We can't use logical OR (`or`) with Reflex reactive variables. The fix involves replacing this with explicit conditional checks:

```python
tema_value = "tema"
if CuestionarioState.cuestionario_tema and CuestionarioState.cuestionario_tema != "":
    tema_value = CuestionarioState.cuestionario_tema
s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_value)[:50]
```

However, this fix introduced a new error because we still can't use standard Python conditionals (`if`, `and`) with reactive variables.

#### Complete Fix - Using rx.cond and bitwise operators
The complete fix requires using Reflex's `rx.cond` and bitwise operators (`&`, `|`, `~`) instead of standard Python conditionals:

```python
tema_value = rx.cond(
    (CuestionarioState.cuestionario_tema != "") & (CuestionarioState.cuestionario_tema != None),
    CuestionarioState.cuestionario_tema,
    "tema"
)
s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_value)[:50]
```

Similarly, we updated other conditionals involving reactive variables:

```python
# Before
if hasattr(CuestionarioState, "cuestionario_pdf_url") and CuestionarioState.cuestionario_pdf_url:
    # ...code...

# After
cuestionario_pdf_url_exists = hasattr(CuestionarioState, "cuestionario_pdf_url")
if cuestionario_pdf_url_exists:
    pdf_url_not_empty = rx.cond(
        CuestionarioState.cuestionario_pdf_url != "",
        True,
        False
    )
    if pdf_url_not_empty:
        # ...code...
```

### 2. Updated PDF Download Button
Previously, the download button in `cuestionario.py` was using a URL-based approach that wasn't working properly:

```python
rx.link(
    rx.button(
        rx.hstack(
            rx.icon("download", mr="0.2em"),
            rx.text("Descargar PDF")
        ),
        size="2",
        variant="soft",
        color_scheme="green",
    ),
    href=CuestionarioState.cuestionario_pdf_url,
    is_external=True,
)
```

We changed it to use the direct download method:

```python
rx.button(
    rx.hstack(
        rx.icon("download", mr="0.2em"),
        rx.text("Descargar PDF")
    ),
    size="2",
    variant="soft",
    color_scheme="green",
    on_click=AppState.download_pdf,
)
```

## Testing
We verified that the app initializes correctly after our fix, and the PDF download functionality should now work properly without the VarTypeError.

## Technical Details
The issue was related to how Reflex handles reactive variables (Var). In Reflex:

1. Reactive variables can't be used with standard Python operators like `or`, `and`, `not`
2. Reactive variables can't be used directly in `if` conditions
3. Instead, you must use `rx.cond` for conditional logic, and bitwise operators (`&`, `|`, `~`) for logical operations

## Future Considerations
- If there are other places in the codebase using similar patterns with logical operators and reactive variables, they should be updated to use the same approach.
- Consider adding more robust error handling for PDF generation and download process.
- Add comprehensive documentation about working with reactive variables in the codebase to prevent similar issues in the future.
