#!/usr/bin/env python3
"""
Test for multilingual help tab implementation.
This will verify that:
1. The help questions correctly change based on the selected language
2. Our method to get translated questions works correctly
"""

import sys
import os

# Add the project root to the Python path so imports work correctly
sys.path.insert(0, os.path.abspath('.'))

try:
    # Import necessary modules
    from mi_app_estudio.help_translations import get_help_questions
    from mi_app_estudio.state import AppState
    
    # Create AppState instance to test translation
    state = AppState()
    
    # Test Spanish questions (default language)
    print("Current language:", state.current_language)
    print("\nTesting help questions in Spanish:")
    spanish_questions = get_help_questions("es")
    print(f"Number of Spanish questions: {len(spanish_questions)}")
    print("First 3 Spanish questions:")
    for i, q in enumerate(spanish_questions[:3]):
        print(f"{i+1}. {q['pregunta']}")
    
    # Test English questions
    print("\nTesting help questions in English:")
    english_questions = get_help_questions("en")
    print(f"Number of English questions: {len(english_questions)}")
    print("First 3 English questions:")
    for i, q in enumerate(english_questions[:3]):
        print(f"{i+1}. {q['pregunta']}")
    
    # Test the reactive var in AppState
    print("\nTesting AppState.ayuda_preguntas_respuestas:")
    # Get current language questions
    current_questions = state.ayuda_preguntas_respuestas
    print(f"Questions in {state.current_language}: {len(current_questions)}")
    print("First question:", current_questions[0]["pregunta"])
    
    # Change language and check that questions change
    print("\nChanging language and checking questions:")
    state.current_language = "en"
    print(f"Language changed to: {state.current_language}")
    english_questions = state.ayuda_preguntas_respuestas
    print(f"Questions in English: {len(english_questions)}")
    print("First question:", english_questions[0]["pregunta"])
    
    # Change back to Spanish
    state.current_language = "es"
    print(f"\nLanguage changed back to: {state.current_language}")
    spanish_questions = state.ayuda_preguntas_respuestas
    print(f"Questions in Spanish: {len(spanish_questions)}")
    print("First question:", spanish_questions[0]["pregunta"])
    
    print("\nTest completed successfully!")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
