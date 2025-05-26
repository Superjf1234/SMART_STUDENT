"""
Simple script to test the translations implementation.
"""
from mi_app_estudio.translations import get_translations

# Test English translations
en_translations = get_translations("en")
print("English translations:")
print("sign_out:", en_translations.get("sign_out"))
print("tab_inicio:", en_translations.get("tab_inicio"))

# Test Spanish translations
es_translations = get_translations("es")
print("\nSpanish translations:")
print("sign_out:", es_translations.get("sign_out"))
print("tab_inicio:", es_translations.get("tab_inicio"))
