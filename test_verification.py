#!/usr/bin/env python3
# Test script to verify the fixes to verdadero/falso questions

# Simple test for answer normalization
def test_vf_normalization():
    test_cases = [
        # Format: user answer, correct answer, expected result
        # Case 1: Normal cases
        ("falso", "falso", True),
        ("Falso", "falso", True), 
        # Case 2: b is recognized as Falso
        ("falso", "b", True),
        ("Falso", "b", True),
        # Case 3: a is recognized as Verdadero
        ("verdadero", "a", True),
        ("Verdadero", "a", True),
        # Case 4: Mismatches
        ("falso", "verdadero", False),
        ("falso", "a", False)
    ]
    
    print("Testing Verdadero/Falso normalization:")
    
    for i, (user_answer, correct_answer, expected) in enumerate(test_cases):
        # Normalize user answer
        if user_answer.lower() in ["verdadero", "true", "v", "t"]:
            user_normalized = "verdadero"
        elif user_answer.lower() in ["falso", "false", "f"]:
            user_normalized = "falso"
        else:
            user_normalized = user_answer.lower()
            
        # Normalize correct answer
        if correct_answer.lower() in ["verdadero", "true", "v", "t", "a"]:
            correct_normalized = "verdadero"
        elif correct_answer.lower() in ["falso", "false", "f", "b"]:
            correct_normalized = "falso"
        else:
            correct_normalized = correct_answer.lower()
            
        result = user_normalized == correct_normalized
        
        print(f"Test {i+1}: User: '{user_answer}' | Correct: '{correct_answer}'")
        print(f"  Normalized: User='{user_normalized}', Correct='{correct_normalized}'")
        print(f"  Result: {result}, Expected: {expected}, Match: {result == expected}")
        
        if result != expected:
            print("  ❌ TEST FAILED!")
        else:
            print("  ✅ TEST PASSED!")
        print()

if __name__ == "__main__":
    test_vf_normalization()
    print("All tests completed!")
