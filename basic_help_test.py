#!/usr/bin/env python3

"""
Simple standalone test for help translations.
"""

import os
import sys

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Python path:", sys.path)

# Add the project root to the path
sys.path.insert(0, os.getcwd())
print("Updated Python path:", sys.path)

try:
    # Import the help translations module
    print("\nImporting help_translations module...")
    from mi_app_estudio.help_translations import get_help_questions
    
    # Test getting translations
    print("\nTesting get_help_questions function...")
    
    # Get Spanish questions
    es_questions = get_help_questions("es")
    print(f"Spanish questions: {len(es_questions)}")
    
    # Get English questions
    en_questions = get_help_questions("en")
    print(f"English questions: {len(en_questions)}")
    
    # Print first question in each language
    print("\nFirst question in Spanish:", es_questions[0]["pregunta"])
    print("First question in English:", en_questions[0]["pregunta"])
    
    # Now try to import the AppState
    print("\nImporting AppState...")
    from mi_app_estudio.state import AppState
    
    # Create an instance
    state = AppState()
    print("Current language:", state.current_language)
    
    # Get current questions
    current_questions = state.ayuda_preguntas_respuestas
    print(f"Questions in current language: {len(current_questions)}")
    print("First question:", current_questions[0]["pregunta"])
    
    print("\nTest successful!")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
