#!/usr/bin/env python3
"""
Test script to verify that help tab questions change based on the language.
"""

from mi_app_estudio.state import AppState
from mi_app_estudio.help_translations import get_help_questions

# Create an instance of AppState
state = AppState()

# Print the default language questions
print("Initial language:", state.current_language)
es_questions = state.ayuda_preguntas_respuestas
print("Spanish Questions (first 3):")
for i, q in enumerate(es_questions[:3]):
    print(f"{i+1}. {q['pregunta']}")

# Change language to English
state.current_language = "en"
print("\nAfter changing to English:", state.current_language)
en_questions = state.ayuda_preguntas_respuestas
print("English Questions (first 3):")
for i, q in enumerate(en_questions[:3]):
    print(f"{i+1}. {q['pregunta']}")

# Change back to Spanish
state.current_language = "es"
print("\nAfter changing back to Spanish:", state.current_language)
es_questions_again = state.ayuda_preguntas_respuestas
print("Spanish Questions (first 3):")
for i, q in enumerate(es_questions_again[:3]):
    print(f"{i+1}. {q['pregunta']}")

print("\nTest completed!")
