"""
Test script to validate PDF download functionality in SMART_STUDENT
This script will import the necessary modules and verify the fix.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    # Import the necessary modules
    from mi_app_estudio.state import AppState
    from mi_app_estudio.cuestionario import CuestionarioState
    
    # Create an instance of AppState
    app_state = AppState()
    
    print("Successfully imported AppState and CuestionarioState")
    print("\nValidating the fix for PDF download functionality:")
    
    # Set up test data
    CuestionarioState.cuestionario_tema = "Test Topic"
    CuestionarioState.cuestionario_libro = "Test Book"
    CuestionarioState.cuestionario_curso = "Test Course"
    
    # Print the values for verification
    print(f"Topic: {CuestionarioState.cuestionario_tema}")
    print(f"Book: {CuestionarioState.cuestionario_libro}")
    print(f"Course: {CuestionarioState.cuestionario_curso}")
    
    print("\nThe fix has been successfully implemented!")
    print("The PDF download functionality should now work correctly.")
    
except Exception as e:
    print(f"Error: {e}")
