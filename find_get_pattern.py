import os, re

def find_get_pattern():
    project_dir = "/workspaces/SMART_STUDENT"
    pattern = r'EvaluationState\.eval_user_answers\.get\('
    
    results = []
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if re.search(pattern, line):
                                results.append((filepath, i+1, line.strip()))
                except:
                    pass
    
    print(f"Found {len(results)} matches:")
    for filepath, line_num, line in results:
        print(f"{filepath}:{line_num}: {line}")

find_get_pattern()
