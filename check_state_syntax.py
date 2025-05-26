"""
Quick test to check for syntax errors in state.py
"""
import sys
import os
import traceback

try:
    # Import the state module
    print("Importing state module...")
    from mi_app_estudio.state import AppState
    print("Successfully imported AppState")
    
    # Import the cuestionario module
    print("Importing cuestionario module...")
    from mi_app_estudio.cuestionario import CuestionarioState
    print("Successfully imported CuestionarioState")
    
    # Check if download_cuestionario_pdf method exists
    print("\nChecking for download_cuestionario_pdf method...")
    if hasattr(AppState, 'download_cuestionario_pdf'):
        print("✓ download_cuestionario_pdf method exists")
    else:
        print("✗ download_cuestionario_pdf method does not exist")
    
    # Check if download_pdf method exists
    print("\nChecking for download_pdf method...")
    if hasattr(AppState, 'download_pdf'):
        print("✓ download_pdf method exists")
    else:
        print("✗ download_pdf method does not exist")
    
    print("\nAll imports successful. No syntax errors detected.")
    
except Exception as e:
    print(f"Error: {str(e)}")
    print("\nTraceback:")
    traceback.print_exc()
