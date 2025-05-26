#!/usr/bin/env python3
"""Simple test for the help_translations module."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    # Test importing the module
    print("Importing help_translations...")
    from mi_app_estudio.help_translations import get_help_questions
    print("Successfully imported get_help_questions")
    
    # Test getting questions in different languages
    print("\nGetting Spanish questions...")
    es_questions = get_help_questions("es")
    print(f"Spanish questions count: {len(es_questions)}")
    
    print("\nGetting English questions...")
    en_questions = get_help_questions("en")
    print(f"English questions count: {len(en_questions)}")
    
    # Compare the first question in both languages
    print("\nFirst Spanish question:", es_questions[0]["pregunta"])
    print("First English question:", en_questions[0]["pregunta"])
    
    print("\nTest completed successfully!")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
