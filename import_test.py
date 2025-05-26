#!/usr/bin/env python3
"""
Simple test for imports.
"""
import sys
print(f"Python path: {sys.path}")

try:
    from mi_app_estudio.help_translations import get_help_questions
    print("Successfully imported get_help_questions")
    en_questions = get_help_questions("en")
    print(f"English questions count: {len(en_questions)}")
    print(f"First question: {en_questions[0]['pregunta']}")
except Exception as e:
    print(f"Error importing: {e}")
    import traceback
    traceback.print_exc()
