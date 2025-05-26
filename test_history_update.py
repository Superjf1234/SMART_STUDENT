"""
Test script to verify score calculation and history update logic.
"""
import asyncio
import sys
import os
from typing import Dict, List, Set, Union, Any, Optional

# Ensure our app's modules are in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our app modules
from mi_app_estudio.evaluaciones import EvaluationState
from mi_app_estudio.state import AppState

def test_score_calculation():
    """Test score calculation with zero correct answers"""
    eval_state = EvaluationState()
    eval_state.eval_preguntas = [
        {"pregunta": "Test Q1", "tipo": "verdadero_falso", "correcta": "verdadero"},
        {"pregunta": "Test Q2", "tipo": "verdadero_falso", "correcta": "falso"},
        {"pregunta": "Test Q3", "tipo": "verdadero_falso", "correcta": "verdadero"},
    ]
    
    # Case 1: Zero correct answers
    eval_state.eval_user_answers = {0: "falso", 1: "verdadero", 2: "falso"}
    eval_state.calculate_eval_score_sync()
    print(f"Score with 0 correct answers: {eval_state.eval_score}%")
    
    # Case 2: One correct answer
    eval_state.eval_user_answers = {0: "verdadero", 1: "verdadero", 2: "falso"}
    eval_state.calculate_eval_score_sync()
    print(f"Score with 1 correct answer: {eval_state.eval_score}%")
    
    # Case 3: All correct answers
    eval_state.eval_user_answers = {0: "verdadero", 1: "falso", 2: "verdadero"}
    eval_state.calculate_eval_score_sync()
    print(f"Score with all correct answers: {eval_state.eval_score}%")

def test_history_connection():
    """Test the connection between evaluation completion and history update"""
    eval_state = EvaluationState()
    
    # Set up a mock evaluation
    eval_state.logged_in_username = "test_user"
    eval_state.eval_preguntas = [
        {"pregunta": "Test Q1", "tipo": "verdadero_falso", "correcta": "verdadero"},
        {"pregunta": "Test Q2", "tipo": "verdadero_falso", "correcta": "falso"},
    ]
    eval_state.eval_user_answers = {0: "verdadero", 1: "falso"}
    
    # Simulate completing an evaluation
    print("Starting test for history connection...")
    try:
        # This would normally save to DB in a real app
        eval_state.calculate_eval_score_sync()
        print(f"Evaluation completed with score: {eval_state.eval_score}%")
        print("Check if _guardar_resultado_en_bd was called properly")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    print("\n=== Testing Score Calculation ===")
    test_score_calculation()
    
    print("\n=== Testing History Connection ===")
    test_history_connection()
