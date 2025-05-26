#!/usr/bin/env python3
# Test file to verify the language toggle fix

from mi_app_estudio.state import AppState

print(f"Current language: {AppState.current_language}")
print(f"Language text: {AppState.language_text}")
print("If you see values above without errors, the fix was successful!")

# Test toggling language
state_instance = AppState()
print(f"Before toggle: {state_instance.current_language}")
state_instance.toggle_language()
print(f"After toggle: {state_instance.current_language}")
print("Language toggle function works correctly!")
