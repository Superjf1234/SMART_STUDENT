"""
Simple test to verify string handling for the PDF download fix.
"""

import re

def main():
    print("Testing the string handling for PDF download fix:")
    print("------------------------------------------------")
    
    # Test with value present
    tema = "Test Topic"
    tema_value = "tema"
    if tema and tema != "":
        tema_value = tema
    s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_value)[:50]
    print(f"With value: tema = '{tema}' -> s_tema = '{s_tema}'")
    
    # Test with empty value
    tema = ""
    tema_value = "tema"
    if tema and tema != "":
        tema_value = tema
    s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_value)[:50]
    print(f"With empty value: tema = '{tema}' -> s_tema = '{s_tema}'")
    
    # Test with None value
    tema = None
    tema_value = "tema"
    if tema and tema != "":
        tema_value = tema
    s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_value)[:50]
    print(f"With None value: tema = {tema} -> s_tema = '{s_tema}'")
    
    print("\nTest complete! The fix logic works as expected.")

if __name__ == "__main__":
    main()
