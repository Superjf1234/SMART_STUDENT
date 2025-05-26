#!/usr/bin/env python3
# Test file for validating the verdadero/falso fix

import sys
import os

print("=== Basic String Normalization Tests ===")
test_cases = [
    ("verdadero", "Verdadero", True), 
    ("falso", "Falso", True), 
    ("falso", "falso", True),
    ("Falso", "falso", True),
    ("verdadero", "falso", False),
    ("falso", "verdadero", False)
]

for user, correct, expected in test_cases:
    user_normalized = ""
    u_ans_lower = user.lower()
    if u_ans_lower in ["verdadero", "true", "v", "t"]:
        user_normalized = "verdadero"
    elif u_ans_lower in ["falso", "false", "f"]:
        user_normalized = "falso"
    else:
        user_normalized = u_ans_lower
    
    correct_normalized = ""
    c_ans_lower = correct.lower()
    if c_ans_lower in ["verdadero", "true", "v", "t"]:
        correct_normalized = "verdadero"
    elif c_ans_lower in ["falso", "false", "f"]:
        correct_normalized = "falso"
    else:
        correct_normalized = c_ans_lower
    
    result = user_normalized == correct_normalized
    print(f"User: {user}, Correct: {correct}")
    print(f"User norm: {user_normalized}, Correct norm: {correct_normalized}")
    print(f"Result: {result}, Match expected: {result == expected}\n")

# Integration test with actual EvaluationState
print("\n=== Testing EvaluationState ===")

# Add project path for imports
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_dir)

try:
    from mi_app_estudio.evaluaciones import EvaluationState
    
    def test_verdadero_falso_questions():
        """Test that true/false questions are correctly evaluated."""
        print("\n=== Testing True/False Question Evaluation ===")
        
        # Create a test instance
        eval_state = EvaluationState()
        
        # Setup test questions
        eval_state.eval_preguntas = [
            {
                "pregunta": "¿La Tierra es plana?",
                "tipo": "verdadero_falso",
                "correcta": "falso"
            },
            {
                "pregunta": "¿El agua hierve a 100°C a nivel del mar?",
                "tipo": "verdadero_falso",
                "correcta": "Verdadero"
            },
            {
                "pregunta": "¿Los humanos pueden respirar bajo el agua?",
                "tipo": "verdadero_falso",
                "correcta": "Falso"
            }
        ]
        
        # Test different ways the user might answer
        test_cases = [
            # Question 0 - correct answer is "falso"
            (0, "falso", True, "lowercase falso"),
            (0, "Falso", True, "capitalized Falso"),
            (0, "FALSO", True, "uppercase FALSO"),
            (0, "false", True, "English 'false'"),
            (0, "f", True, "single letter f"),
            (0, "verdadero", False, "incorrect answer 'verdadero'"),
            # Question 1 - correct answer is "Verdadero"
            (1, "verdadero", True, "lowercase verdadero"),
            (1, "Verdadero", True, "capitalized Verdadero"),
            (1, "VERDADERO", True, "uppercase VERDADERO"),
            (1, "true", True, "English 'true'"),
            (1, "v", True, "single letter v"),
            (1, "falso", False, "incorrect answer 'falso'"),
            # Question 2 - correct answer is "Falso" with capital F
            (2, "falso", True, "lowercase falso"),
            (2, "Falso", True, "capitalized Falso"),
            (2, "FALSO", True, "uppercase FALSO"),
            (2, "f", True, "single letter f"),
            (2, "verdadero", False, "incorrect answer 'verdadero'")
        ]
        
        success_count = 0
        total_tests = len(test_cases)
        
        for question_idx, answer, expected_result, description in test_cases:
            # Set the current question index
            eval_state.eval_current_idx = question_idx
            
            # Set the user's answer
            eval_state.eval_user_answers = {question_idx: answer}
            
            # Check if the question is correct in review mode
            result = eval_state.is_current_question_correct_in_review
            
            # Print the result
            status = "PASS" if result == expected_result else "FAIL"
            if result == expected_result:
                success_count += 1
            print(f"{status}: Question {question_idx}, Answer: '{answer}', Expected: {expected_result}, Description: {description}")
        
        print(f"\nTest Summary: {success_count}/{total_tests} tests passed ({(success_count/total_tests)*100:.1f}%)")
    
    test_verdadero_falso_questions()
    
except ImportError as e:
    print(f"Error importing EvaluationState: {e}")
    print("Basic string normalization tests completed, but EvaluationState tests could not be run.")
