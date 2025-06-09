#!/usr/bin/env python3

def find_unmatched_parens(filename):
    """Encuentra paréntesis no balanceados en un archivo Python."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    stack = []
    paren_map = {'(': ')', '[': ']', '{': '}'}
    
    for line_num, line in enumerate(lines, 1):
        in_string = False
        in_comment = False
        escape_next = False
        string_char = None
        
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
            elif char in paren_map.values():
                if not stack:
                    print(f"Error: Closing '{char}' without opening at line {line_num}, column {col_num + 1}")
                    return
                    
                opening, open_line, open_col = stack.pop()
                expected = paren_map[opening]
                if char != expected:
                    print(f"Error: Mismatched brackets. Expected '{expected}' but found '{char}' at line {line_num}, column {col_num + 1}")
                    print(f"Opening '{opening}' was at line {open_line}, column {open_col}")
                    return
    
    if stack:
        print("Unclosed brackets found:")
        for bracket, line_num, col_num in stack:
            print(f"  '{bracket}' at line {line_num}, column {col_num}")
            # Show the line context
            if line_num <= len(lines):
                context_line = lines[line_num - 1].rstrip()
                print(f"    {line_num}: {context_line}")
                print(f"    {' ' * (len(str(line_num)) + 1 + col_num)}{'^'}")
        return False
    else:
        print("All brackets are properly balanced!")
        return True

if __name__ == "__main__":
    find_unmatched_parens("/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py")
