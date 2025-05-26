#!/usr/bin/env python3
# Debug script to print the structure of a verdadero_falso question

import json
import sqlite3
import sys

def print_colored_text(text, color_code):
    """Print text with color."""
    print(f"\033[{color_code}m{text}\033[0m")

def get_latest_evaluations(db_path="student_stats.db", limit=10):
    """Get the latest evaluation data from the database."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the evaluations table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='evaluaciones';
        ''')
        
        if not cursor.fetchone():
            print_colored_text("No 'evaluaciones' table found in the database.", 91)
            return []
        
        # Get column names
        cursor.execute('PRAGMA table_info(evaluaciones)')
        columns = [col[1] for col in cursor.fetchall()]
        
        # Check if the table has the expected columns
        expected_columns = ['curso', 'libro', 'tema', 'preguntas_json']
        missing_columns = [col for col in expected_columns if col not in columns]
        
        if missing_columns:
            print_colored_text(f"Missing columns in evaluaciones table: {missing_columns}", 91)
            print_colored_text(f"Available columns: {columns}", 93)
            return []
        
        # Query to get the latest evaluations
        cursor.execute('''
            SELECT id, username, curso, libro, tema, preguntas_json, fecha
            FROM evaluaciones
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        
        return cursor.fetchall()
        
    except sqlite3.Error as e:
        print_colored_text(f"Database error: {e}", 91)
        return []
    finally:
        if conn:
            conn.close()

def analyze_questions(evaluations):
    """Analyze the questions from evaluations, focusing on verdadero_falso."""
    if not evaluations:
        print_colored_text("No evaluations found to analyze.", 91)
        return
    
    vf_questions = []
    
    for eval_data in evaluations:
        eval_id, username, curso, libro, tema, preguntas_json, fecha = eval_data
        
        try:
            preguntas = json.loads(preguntas_json) if preguntas_json else []
            for i, pregunta in enumerate(preguntas):
                if pregunta.get("tipo") == "verdadero_falso":
                    vf_questions.append({
                        "eval_id": eval_id,
                        "username": username,
                        "course": f"{curso} > {libro} > {tema}",
                        "date": fecha,
                        "question_idx": i,
                        "question": pregunta
                    })
        except json.JSONDecodeError:
            print_colored_text(f"Error decoding JSON for evaluation {eval_id}", 91)
    
    print_colored_text(f"\nFound {len(vf_questions)} verdadero_falso questions in recent evaluations", 92)
    
    if not vf_questions:
        return
    
    for i, q_data in enumerate(vf_questions):
        print_colored_text(f"\n===== Question {i+1}/{len(vf_questions)} =====", 94)
        print(f"Evaluation: {q_data['eval_id']} - {q_data['course']}")
        print(f"Date: {q_data['date']}")
        
        question = q_data['question']
        print_colored_text(f"Text: {question.get('texto', 'N/A')}", 96)
        print(f"Type: {question.get('tipo', 'N/A')}")
        
        # Check how the correct answer is stored
        correct_answer = question.get('correcta', question.get('respuesta_correcta'))
        correct_type = type(correct_answer).__name__
        
        print_colored_text(f"Correct answer: {correct_answer} (type: {correct_type})", 93)
        
        # Check if there's an explanation
        if 'explicacion' in question:
            print(f"Explanation: {question['explicacion']}")
        
        # Normalize the correct answer as done in the code
        normalized = None
        if correct_answer is not None:
            if isinstance(correct_answer, bool):
                normalized = "verdadero" if correct_answer else "falso"
            else:
                c_ans_lower = str(correct_answer).strip().lower()
                if c_ans_lower in ["verdadero", "true", "v", "t"]:
                    normalized = "verdadero"
                elif c_ans_lower in ["falso", "false", "f"]:
                    normalized = "falso"
                else:
                    normalized = c_ans_lower
        
        print_colored_text(f"Normalized correct answer: {normalized}", 92)
        
        # Check answer options
        if 'opciones' in question:
            print(f"Options: {question['opciones']}")
        if 'alternativas' in question:
            print(f"Alternatives: {question['alternativas']}")
            
        print_colored_text("Raw question data:", 95)
        print(json.dumps(question, indent=2, ensure_ascii=False))

def main():
    print_colored_text("VERDADERO/FALSO QUESTION DEBUGGER", 94)
    print_colored_text("================================\n", 94)
    
    evaluations = get_latest_evaluations()
    analyze_questions(evaluations)

if __name__ == "__main__":
    main()