#!/usr/bin/env python3

def check_parentheses_balance(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    stack = []
    line_number = 1
    char_position = 0
    
    open_chars = {'(': ')', '[': ']', '{': '}'}
    close_chars = {')': '(', ']': '[', '}': '{'}
    
    in_string = False
    string_char = None
    escape_next = False
    in_comment = False
    
    for i, char in enumerate(content):
        char_position += 1
        
        if char == '\n':
            line_number += 1
            char_position = 0
            in_comment = False
            continue
            
        if in_comment:
            continue
            
        if escape_next:
            escape_next = False
            continue
            
        if char == '\\' and in_string:
            escape_next = True
            continue
            
        if char == '#' and not in_string:
            in_comment = True
            continue
            
        if char in ['"', "'"] and not in_string:
            in_string = True
            string_char = char
            continue
        elif char == string_char and in_string:
            in_string = False
            string_char = None
            continue
            
        if in_string:
            continue
            
        if char in open_chars:
            stack.append((char, line_number, char_position))
        elif char in close_chars:
            if not stack:
                print(f"Error: Closing '{char}' without opening at line {line_number}, position {char_position}")
                return False
                
            open_char, open_line, open_pos = stack.pop()
            expected_close = open_chars[open_char]
            
            if char != expected_close:
                print(f"Error: Mismatched brackets. Expected '{expected_close}' but found '{char}' at line {line_number}, position {char_position}")
                print(f"Opening '{open_char}' was at line {open_line}, position {open_pos}")
                return False
    
    if stack:
        print("Unclosed brackets:")
        for char, line, pos in stack:
            print(f"  '{char}' opened at line {line}, position {pos}")
        return False
    
    print("All brackets are balanced!")
    return True

if __name__ == "__main__":
    file_path = "/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py"
    check_parentheses_balance(file_path)
