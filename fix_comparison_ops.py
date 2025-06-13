#!/usr/bin/env python3
import re
import os

def fix_comparisons(file_path, output_path):
    print(f"Reading file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all problematic patterns with corrected versions
    
    # Fix patterns like ((EvaluationState.eval_score < 4)0)
    content = re.sub(r'\(\(EvaluationState\.eval_score\s*<\s*4\)0\)', '(EvaluationState.eval_score < 40)', content)
    content = re.sub(r'\(\(EvaluationState\.eval_score\s*<\s*6\)0\)', '(EvaluationState.eval_score < 60)', content)
    content = re.sub(r'\(\(EvaluationState\.eval_score\s*<\s*8\)0\)', '(EvaluationState.eval_score < 80)', content)
    content = re.sub(r'\(\(EvaluationState\.eval_score\s*<\s*9\)0\)', '(EvaluationState.eval_score < 90)', content)
    
    # Fix patterns like ((EvaluationState.eval_score >= 4)0)
    content = re.sub(r'\(\(EvaluationState\.eval_score\s*>=\s*4\)0\)', '(EvaluationState.eval_score >= 40)', content)
    content = re.sub(r'\(\(EvaluationState\.eval_score\s*>=\s*6\)0\)', '(EvaluationState.eval_score >= 60)', content)
    content = re.sub(r'\(\(EvaluationState\.eval_score\s*>=\s*8\)0\)', '(EvaluationState.eval_score >= 80)', content)
    content = re.sub(r'\(\(EvaluationState\.eval_score\s*>=\s*9\)0\)', '(EvaluationState.eval_score >= 90)', content)
    
    # Fix patterns without parentheses
    content = re.sub(r'(\s)EvaluationState\.eval_score\s*<\s*40([,\s])', r'\1(EvaluationState.eval_score < 40)\2', content)
    content = re.sub(r'(\s)EvaluationState\.eval_score\s*<\s*60([,\s])', r'\1(EvaluationState.eval_score < 60)\2', content)
    content = re.sub(r'(\s)EvaluationState\.eval_score\s*<\s*80([,\s])', r'\1(EvaluationState.eval_score < 80)\2', content)
    content = re.sub(r'(\s)EvaluationState\.eval_score\s*<\s*90([,\s])', r'\1(EvaluationState.eval_score < 90)\2', content)
    
    content = re.sub(r'(\s)EvaluationState\.eval_score\s*>=\s*40([,\s])', r'\1(EvaluationState.eval_score >= 40)\2', content)
    content = re.sub(r'(\s)EvaluationState\.eval_score\s*>=\s*60([,\s])', r'\1(EvaluationState.eval_score >= 60)\2', content)
    content = re.sub(r'(\s)EvaluationState\.eval_score\s*>=\s*80([,\s])', r'\1(EvaluationState.eval_score >= 80)\2', content)
    content = re.sub(r'(\s)EvaluationState\.eval_score\s*>=\s*90([,\s])', r'\1(EvaluationState.eval_score >= 90)\2', content)
    
    print(f"Writing to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Done fixing {output_path}")

# Fix the file
fix_comparisons('/workspaces/SMART_STUDENT/mi_app_estudio_backup.py', '/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py')
