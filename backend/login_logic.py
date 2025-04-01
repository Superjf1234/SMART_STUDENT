# backend/login_logic.py
# Contiene la lógica de validación de login, llamando a config_logic.

import sys
import traceback

# Importar la función de validación adaptada de config_logic
try:
    # Intenta importar relativamente desde el mismo paquete 'backend'
    from .config_logic import validar_credenciales as validar_credenciales_real

    print("INFO (login_logic): Usando 'validar_credenciales' desde .config_logic")
except ImportError:
    # Fallback si falla la relativa (ej. al ejecutar standalone o estructura diferente)
    try:
        from config_logic import validar_credenciales as validar_credenciales_real

        print(
            "WARN (login_logic): Usando importación directa de config_logic (fallback)."
        )
    except ImportError:
        # Último recurso: definir un fallback dummy si todo falla
        print(
            "ERROR CRITICO (login_logic): No se encontró 'validar_credenciales' en config_logic.",
            file=sys.stderr,
        )

        def validar_credenciales_real(username, password):
            print(
                "ERROR (login_logic): USANDO VALIDACIÓN DUMMY (FALLBACK FINAL)",
                file=sys.stderr,
            )
            return False  # Fallback muy básico que siempre falla


def verificar_login(username, password):
    """
    Verifica las credenciales del usuario llamando a la función de config_logic.
    Retorna True si son válidas, False en caso contrario o si hay error.
    """
    if not username or not password:
        print("WARN (login_logic): Intento de login con usuario o contraseña vacíos.")
        return False

    try:
        # Llama a la función importada (que ahora usa passlib desde config_logic)
        es_valido = validar_credenciales_real(username, password)
        # Los prints de DEBUG/INFO ya están dentro de la función validar_credenciales_real
        return es_valido
    except Exception as e_val:
        # Captura cualquier error inesperado durante la validación
        print(
            f"ERROR (login_logic): Excepción durante la llamada a validación: {e_val}",
            file=sys.stderr,
        )
        traceback.print_exc()
        return False  # Considerar el login como fallido si hay un error interno


# --- NO hay interfaz gráfica aquí ---

if __name__ == "__main__":
    # Ejemplo de cómo usar la lógica directamente (requiere config_logic funcional)
    print("\n--- Probando lógica de login_logic.py ---")
    # Asumiendo que los hashes en config_logic corresponden a esto:
    user_ok = "felipe"
    pwd_ok = "1234"
    user_fail = "felipe"
    pwd_fail = "incorrecta"
    user_noexiste = "usuario_inventado"

    print(f"Probando {user_ok}/{pwd_ok}:")
    if verificar_login(user_ok, pwd_ok):
        print("  -> Login OK")
    else:
        print("  -> Login Fallido")

    print(f"Probando {user_fail}/{pwd_fail}:")
    if verificar_login(user_fail, pwd_fail):
        print("  -> Login OK")
    else:
        print("  -> Login Fallido")

    print(f"Probando {user_noexiste}/password:")
    if verificar_login(user_noexiste, "password"):
        print("  -> Login OK")
    else:
        print("  -> Login Fallido")

    print("--- Pruebas login_logic.py finalizadas ---")
