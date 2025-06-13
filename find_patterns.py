import os, re

def find_patterns():
    project_dir = "/workspaces/SMART_STUDENT"
    patterns = [
        # Direct .get() usage
        r'EvaluationState\.eval_user_answers\.get\(',
        # Lambda with EvaluationState.eval_user_answers
        r'lambda.*EvaluationState\.eval_user_answers',
        # Common expressions that might be near the error
        r'EvaluationState\.eval_user_answers.*\!=\s*None',
        # Any rx.cond with eval_user_answers
        r'rx\.cond\(.*eval_user_answers',
        # Anything on line 259
        r'^.*$'
    ]
    
    special_files = [
        '/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py'
    ]
    
    for filepath in special_files:
        print(f"\n=== Checking line 259 in {filepath} ===")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) >= 259:
                    context = 5
                    start = max(0, 259 - 1 - context)
                    end = min(len(lines), 259 + context)
                    print(f"Context around line 259:")
                    for i in range(start, end):
                        prefix = ">>> " if i == 259-1 else "    "
                        print(f"{prefix}{i+1}: {lines[i].rstrip()}")
                else:
                    print(f"File has fewer than 259 lines.")
        except Exception as e:
            print(f"Error reading file: {e}")

    for pattern in patterns:
        print(f"\n=== Searching for pattern: {pattern} ===")
        results = []
        for root, dirs, files in os.walk(project_dir):
            if 'venv' in root or '.git' in root:
                continue  # Skip venv and .git directories
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                if re.search(pattern, line):
                                    if pattern != r'^.*$' or i == 258:  # Only report line 259 for the catch-all pattern
                                        results.append((filepath, i+1, line.strip()))
                    except:
                        pass
        
        print(f"Found {len(results)} matches:")
        for filepath, line_num, line in results:
            print(f"{filepath}:{line_num}: {line}")

find_patterns()
