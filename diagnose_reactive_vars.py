#!/usr/bin/env python
"""
Script de diagnóstico para entender las variables reactivas de Reflex.
Este script analiza cómo están estructuradas internamente las variables de CuestionarioState.
"""
import sys
import os
import inspect
import traceback
from pathlib import Path

# Agregar la raíz del proyecto al path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    print("\n=== DIAGNÓSTICO DE VARIABLES REACTIVAS EN REFLEX ===\n")
    
    # Importar el módulo cuestionario
    print("1. Importando módulos...")
    from mi_app_estudio.cuestionario import CuestionarioState
    print("   ✓ Módulos importados correctamente\n")
    
    # Examinar cuestionario_preguntas
    print("2. Examinando CuestionarioState.cuestionario_preguntas...")
    
    # Verificar si el atributo existe
    if hasattr(CuestionarioState, "cuestionario_preguntas"):
        print("   ✓ Atributo cuestionario_preguntas existe")
        
        # Obtener el objeto
        preguntas = CuestionarioState.cuestionario_preguntas
        
        # Examinar el tipo
        print(f"   - Tipo: {type(preguntas)}")
        
        # Verificar si tiene _var_value
        if hasattr(preguntas, "_var_value"):
            var_value = preguntas._var_value
            print(f"   - _var_value existe (tipo: {type(var_value)})")
            
            if isinstance(var_value, list):
                print(f"   - _var_value es una lista con {len(var_value)} elementos")
                
                # Mostrar primer elemento si existe
                if var_value:
                    print(f"   - Primer elemento: {type(var_value[0])}")
                    print(f"   - Contenido del primer elemento: {var_value[0]}")
                    
        # Ver qué métodos y atributos tiene
        print("\n3. Atributos y métodos disponibles:")
        for attr in dir(preguntas):
            if not attr.startswith("__"):
                attr_type = type(getattr(preguntas, attr))
                print(f"   - {attr}: {attr_type}")
        
        # Intentar acceder como lista
        print("\n4. Intentando acceder como lista:")
        try:
            primer_elemento = preguntas[0]
            print(f"   ✓ Se puede acceder por índice: preguntas[0] = {type(primer_elemento)}")
            
            # Verificar si el primer elemento tiene _var_value
            if hasattr(primer_elemento, "_var_value"):
                print(f"   - primer_elemento._var_value = {primer_elemento._var_value}")
            
            # Intentar iterar
            print("\n5. Intentando iterar:")
            try:
                elementos = []
                for i, pregunta in enumerate(preguntas):
                    if i < 3:  # Mostrar solo los primeros 3
                        print(f"   - Elemento {i}: {type(pregunta)}")
                        elementos.append(pregunta)
                print(f"   ✓ Se puede iterar, encontrados {len(elementos)} elementos")
            except Exception as e:
                print(f"   ✗ Error al iterar: {e}")
            
        except Exception as e:
            print(f"   ✗ Error al acceder por índice: {e}")
            
        # Intentar convertir a lista explícitamente
        print("\n6. Intentando convertir a lista:")
        try:
            lista_preguntas = list(preguntas)
            print(f"   ✓ Conversión a lista exitosa: {len(lista_preguntas)} elementos")
        except Exception as e:
            print(f"   ✗ Error al convertir a lista: {e}")
        
        # Intentar obtener como dict
        print("\n7. Intentando obtener como dict:")
        try:
            if hasattr(preguntas, "to_dict"):
                dict_preguntas = preguntas.to_dict()
                print(f"   ✓ Método to_dict() disponible: {type(dict_preguntas)}")
                if isinstance(dict_preguntas, list):
                    print(f"   - to_dict() devuelve una lista con {len(dict_preguntas)} elementos")
            else:
                print("   ✗ Método to_dict() no disponible")
        except Exception as e:
            print(f"   ✗ Error al obtener como dict: {e}")
        
        # Intentar evaluar representación como string
        print("\n8. Evaluando representación como string:")
        try:
            str_val = str(preguntas)
            print(f"   - str(preguntas) = {str_val[:100]}..." if len(str_val) > 100 else str_val)
            
            if str_val.startswith("[") and str_val.endswith("]"):
                print("   - Parece ser una representación de lista")
                import ast
                try:
                    # Intentar interpretar como una lista literal de Python
                    parsed_list = ast.literal_eval(str_val)
                    if isinstance(parsed_list, list):
                        print(f"   ✓ Parsed como lista con {len(parsed_list)} elementos")
                except:
                    print("   ✗ No se pudo interpretar como lista literal")
        except Exception as e:
            print(f"   ✗ Error evaluando string representation: {e}")
    else:
        print("   ✗ Atributo cuestionario_preguntas no existe")
    
    print("\n=== FIN DEL DIAGNÓSTICO ===")
    
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
