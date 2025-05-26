#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Ruta del archivo a modificar
file_path = 'mi_app_estudio/state.py'

# Crear un respaldo
backup_file = f"{file_path}.bak_manual"
import shutil
shutil.copy2(file_path, backup_file)
print(f"Respaldo creado en {backup_file}")

# Leer el contenido del archivo
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Contenido del método corregido
old_method = """    def open_contact_form(self):
        \"\"\"Abre el formulario de contacto o redirige al correo de soporte.\"\"\"
        # En una implementación completa, esto mostraría un modal con un formulario de contacto
        # Por ahora, simplemente abrimos el cliente de correo del usuario
        print("DEBUG: Abriendo formulario de contacto o cliente de correo")
        import webbrowser
        try:
            webbrowser.open("mailto:support@smartstudent.cl?subject=Consulta%20desde%20SMART%20STUDENT")
        except Exception as e:
            self.error_message_ui = "No se pudo abrir el cliente de correo. Por favor, envía un correo a support@smartstudent.cl"
            print(f"ERROR: No se pudo abrir el cliente de correo: {e}")
        yield"""

# Nuevo método (exactamente igual pero rescrito manualmente para evitar problemas de caracteres ocultos)
new_method = """    def open_contact_form(self):
        \"\"\"Abre el formulario de contacto o redirige al correo de soporte.\"\"\"
        # En una implementación completa, esto mostraría un modal con un formulario de contacto
        # Por ahora, simplemente abrimos el cliente de correo del usuario
        print("DEBUG: Abriendo formulario de contacto o cliente de correo")
        import webbrowser
        try:
            webbrowser.open("mailto:support@smartstudent.cl?subject=Consulta%20desde%20SMART%20STUDENT")
        except Exception as e:
            self.error_message_ui = "No se pudo abrir el cliente de correo. Por favor, envía un correo a support@smartstudent.cl"
            print(f"ERROR: No se pudo abrir el cliente de correo: {e}")
        yield"""

# Reemplazar el método
if old_method in content:
    content = content.replace(old_method, new_method)
    print("Método reemplazado con éxito.")
else:
    print("No se encontró el método exacto para reemplazar.")
    
    # Reemplazar versión alternativa
    start_marker = "    def open_contact_form(self):"
    end_marker = "    def set_ayuda_search_query"
    
    if start_marker in content and end_marker in content:
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker, start_idx)
        
        if start_idx >= 0 and end_idx > start_idx:
            # Extraer el contenido entre los marcadores
            old_section = content[start_idx:end_idx]
            print(f"Encontrada sección a reemplazar:\n{repr(old_section)}")
            
            # Crear nuevo contenido con el método correcto
            new_section = new_method + "\n        \n"
            
            # Reemplazar la sección
            content = content[:start_idx] + new_section + content[end_idx:]
            print("Sección reemplazada con éxito.")
        else:
            print("No se pudieron localizar correctamente los marcadores de inicio y fin.")
    else:
        print("No se encontraron los marcadores para reemplazar la sección.")

# Guardar el contenido modificado
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(content)

print("Archivo modificado guardado.")
