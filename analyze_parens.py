# Script para analizar paréntesis en un archivo
import sys

def analyze_file(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        open_parens = content.count('(')
        close_parens = content.count(')')
        
        print(f'Paréntesis abiertos: {open_parens}')
        print(f'Paréntesis cerrados: {close_parens}')
        print(f'Diferencia: {open_parens - close_parens}')
        
        # Analizar línea por línea para encontrar desbalances
        lines = content.splitlines()
        open_count = 0
        for i, line in enumerate(lines):
            open_count += line.count('(') - line.count(')')
            if open_count > 10:  # Un valor alto sugiere un paréntesis sin cerrar
                print(f'Posible paréntesis sin cerrar en la línea {i+1}: {line}')
                print(f'Balance acumulado: {open_count}')
        
    except Exception as e:
        print(f"Error al analizar el archivo: {e}")

if __name__ == "__main__":
    analyze_file('mi_app_estudio/mi_app_estudio.py')
