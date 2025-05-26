"""
Simple script to test the translations implementation.
"""
from mi_app_estudio.state import AppState
from mi_app_estudio.translations import get_translations

# Create an AppState instance
state = AppState()

# Test translate method
print("Current language:", state.current_language)
print("Translate 'sign_out':", state.translate("sign_out"))

# Toggle language
state.toggle_language()
print("After toggle, current language:", state.current_language)
print("Translate 'sign_out' after toggle:", state.translate("sign_out"))

# Test tab translations
print("\nTab text in English:")
state.current_language = "en"
tab_texts = state.get_tab_text
for tab, text in tab_texts.items():
    print(f"{tab}: {text}")

print("\nTab text in Spanish:")
state.current_language = "es"
tab_texts = state.get_tab_text
for tab, text in tab_texts.items():
    print(f"{tab}: {text}")
