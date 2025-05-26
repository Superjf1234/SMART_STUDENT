#!/usr/bin/env python3
"""
Test for the application's multilingual help system.
This will check if the AppState can correctly provide translated help questions.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

try:
    # Import required modules
    print("Importing modules...")
    from mi_app_estudio.state import AppState
    from mi_app_estudio.help_translations import get_help_questions
    
    print("\nCreating AppState...")
    app_state = AppState()
    
    # Show default language
    print(f"Default language: {app_state.current_language}")
    
    # Get help questions in default language
    print("\nGetting help questions in default language...")
    default_questions = app_state.ayuda_preguntas_respuestas
    print(f"Found {len(default_questions)} questions in {app_state.current_language}")
    print("First question:", default_questions[0]["pregunta"])
    
    # Change language and check questions
    print("\nChanging language to English...")
    app_state.current_language = "en"
    print(f"Language now: {app_state.current_language}")
    
    # Get help questions in English
    print("\nGetting help questions in English...")
    en_questions = app_state.ayuda_preguntas_respuestas
    print(f"Found {len(en_questions)} questions in English")
    print("First question:", en_questions[0]["pregunta"])
    
    print("\nTest completed successfully!")
    
except Exception as e:
    print(f"Error during test: {e}")
    import traceback
    traceback.print_exc()
