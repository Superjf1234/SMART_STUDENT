import sys

def fix_evaluaciones():
    try:
        with open('mi_app_estudio/evaluaciones.py', 'r') as f:
            lines = f.readlines()
        
        # Mantener solo las primeras 1020 líneas
        clean_lines = lines[:1020]
        
        # Buscar la parte final del archivo (después de la distribución de preguntas)
        final_part = []
        in_final_part = False
        for line in lines[1020:]:
            if not in_final_part and '    # Verificación post-distribución' in line:
                in_final_part = True
            
            if in_final_part:
                final_part.append(line)
        
        # Si no se encontró la parte final, terminar correctamente
        if not final_part:
            for i in range(1020, len(lines)):
                if '    self.eval_preguntas = preguntas_distribuidas[:MAX_QUESTIONS]' in lines[i]:
                    final_part = lines[i:]
                    break
        
        # Si aún no se encontró, agregar un cierre básico
        if not final_part:
            final_part = [
                '\n',
                '                    # Asignar las preguntas distribuidas a la evaluación\n',
                '                    self.eval_preguntas = preguntas_distribuidas[:MAX_QUESTIONS]\n',
                '                    self.eval_user_answers = {i: "" for i in range(len(self.eval_preguntas))}\n',
                '                    self.is_eval_active = True\n',
                '                    self.eval_total_q = len(self.eval_preguntas)\n',
                '                    self.eval_current_idx = 0\n',
                '                    print(f"DEBUG: Evaluación activada con {self.eval_total_q} preguntas distribuidas")\n',
                '            else:\n',
                '                self.eval_error_message = resultado_logica.get("message", "Error al generar evaluación.")\n',
                '                print(f"ERROR: {self.eval_error_message}")\n',
                '        except Exception as e:\n',
                '            self.eval_error_message = f"Error inesperado: {str(e)}"\n',
                '            print(f"ERROR: Excepción en generate_evaluation: {e}\\n{traceback.format_exc()}")\n',
                '        finally:\n',
                '            self.is_generation_in_progress = False\n',
                '            yield # Mostrar el resultado final\n'
            ]
        
        # Escribir a un nuevo archivo
        with open('mi_app_estudio/evaluaciones.py.fixed', 'w') as f:
            f.writelines(clean_lines)
            f.writelines(final_part)
        
        print("Archivo corregido guardado como mi_app_estudio/evaluaciones.py.fixed")
        return True
    except Exception as e:
        print(f"Error al corregir el archivo: {e}")
        return False

if __name__ == "__main__":
    fix_evaluaciones()
    
    # Verificar la sintaxis del archivo corregido
    import py_compile
    try:
        py_compile.compile("mi_app_estudio/evaluaciones.py.fixed")
        print("Verificación de sintaxis exitosa para el archivo corregido")
        
        # Reemplazar el archivo original
        import os
        os.replace("mi_app_estudio/evaluaciones.py.fixed", "mi_app_estudio/evaluaciones.py")
        print("Archivo original reemplazado con la versión corregida")
    except Exception as e:
        print(f"Error de sintaxis en el archivo corregido: {e}")
