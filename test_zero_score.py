# Test to verify that evaluations with 0 correct answers show exactly 0%
# rather than being incorrectly rounded to 1%

from mi_app_estudio.evaluaciones import EvaluationState

def test_zero_score_calculation():
    """Test that zero correct answers results in a 0% score, not 1%"""
    # Create a test instance
    test_state = EvaluationState()
    
    # Mock evaluation data with no correct answers
    test_state.eval_preguntas = [{'tipo': 'verdadero_falso', 'correcta': 'verdadero'} for _ in range(5)]
    test_state.eval_user_answers = {i: 'falso' for i in range(5)}  # All wrong answers
    
    # Calculate score
    test_state.calculate_eval_score_sync()
    
    # Check that score is exactly 0.0 and not rounded
    print(f"Score for 0 correct answers: {test_state.eval_score}%")
    assert test_state.eval_score == 0.0, f"Expected 0.0, got {test_state.eval_score}"
    print("✅ Zero score test passed! Score remains exactly 0% with no correct answers.")
    
    # Also test rounding logic for scores > 0
    test_state.eval_preguntas = [{'tipo': 'verdadero_falso', 'correcta': 'verdadero'} for _ in range(10)]
    test_state.eval_user_answers = {
        0: 'verdadero',  # 1 correct
        1: 'falso',      # wrong
        2: 'falso',      # wrong
        3: 'falso',      # wrong
        4: 'falso',      # wrong
        5: 'falso',      # wrong
        6: 'falso',      # wrong
        7: 'falso',      # wrong
        8: 'falso',      # wrong
        9: 'falso'       # wrong
    }
    
    # Calculate score
    test_state.calculate_eval_score_sync()
    
    # Check rounding for non-zero scores (should round up to 10%)
    expected = 10.0  # 1/10 = 10%, rounded up from 10%
    print(f"Score for 1 out of 10 correct answers: {test_state.eval_score}%")
    assert test_state.eval_score == expected, f"Expected {expected}, got {test_state.eval_score}"
    print("✅ Standard rounding test passed! Score is correctly calculated for non-zero scores.")

if __name__ == "__main__":
    test_zero_score_calculation()
    print("All tests PASSED! ✅")