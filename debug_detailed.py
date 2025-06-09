#!/usr/bin/env python3

def find_unmatched_parens_detailed(filename):
    """Encuentra paréntesis no balanceados con más detalle."""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to compile first
    try:
        compile(content, filename, 'exec')
        print("File compiles successfully!")
        return True
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        print(f"Line {e.lineno}: {e.text.strip() if e.text else 'N/A'}")
    
    # Manual bracket checking
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    stack = []
    paren_map = {'(': ')', '[': ']', '{': '}'}
    
    for line_num, line in enumerate(lines, 1):
        if line_num < 930 or line_num > 970:  # Focus on problem area
            continue
            
        in_string = False
        in_comment = False
        escape_next = False
        string_char = None
        
        print(f"Line {line_num}: {line.rstrip()}")
        
        for col_num, char in enumerate(line):
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\' and in_string:
                escape_next = True
                continue
                
            if char == '#' and not in_string:
                in_comment = True
                break
                
            if char in ['"', "'"] and not in_comment:
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                continue
                
            if in_string or in_comment:
                continue
                
            if char in paren_map:
                stack.append((char, line_num, col_num + 1))
                print(f"  OPEN '{char}' at column {col_num + 1}")
            elif char in paren_map.values():
                if not stack:
                    print(f"  ERROR: Closing '{char}' without opening at column {col_num + 1}")
                    return
                    
                opening, open_line, open_col = stack.pop()
                expected = paren_map[opening]
                if char != expected:
                    print(f"  ERROR: Mismatched brackets. Expected '{expected}' but found '{char}' at column {col_num + 1}")
                    print(f"  Opening '{opening}' was at line {open_line}, column {open_col}")
                    return
                else:
                    print(f"  CLOSE '{char}' at column {col_num + 1} (matches line {open_line})")
    
    if stack:
        print("\nUnclosed brackets found in focus area:")
        for bracket, line_num, col_num in stack:
            print(f"  '{bracket}' at line {line_num}, column {col_num}")
        return False
    else:
        print("\nAll brackets in focus area are properly balanced!")
        return True

if __name__ == "__main__":
    find_unmatched_parens_detailed("/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py")
