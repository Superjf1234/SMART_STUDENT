"""
Fix all uses of .get() on EvaluationState.eval_user_answers in mi_app_estudio.py
"""

import re
import os

def fix_get_method_pattern():
    file_path = "/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py"
    backup_path = "/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py.bak"
    
    # Create a backup
    os.system(f"cp {file_path} {backup_path}")
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find: EvaluationState.eval_user_answers.get(EvaluationState.eval_current_idx)
    pattern = r'(EvaluationState\.eval_user_answers)\.get\((.*?)\)'
    
    # Replace with safe access pattern
    replacement = r'\1[\2] if \2 in \1 else None'
    
    # Apply the replacement
    new_content = re.sub(pattern, replacement, content)
    
    # Write the changes
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {file_path}")
    print("Backup created at", backup_path)

if __name__ == "__main__":
    fix_get_method_pattern()
