print("Testing V/F comparison:")
test_cases = [
    ("verdadero", "Verdadero", True), 
    ("falso", "Falso", True), 
    ("falso", "falso", True),
    ("Falso", "falso", True),
    ("verdadero", "falso", False),
    ("falso", "verdadero", False)
]

for user, correct, expected in test_cases:
    user_normalized = ""
    u_ans_lower = user.lower()
    if u_ans_lower in ["verdadero", "true", "v", "t"]:
        user_normalized = "verdadero"
    elif u_ans_lower in ["falso", "false", "f"]:
        user_normalized = "falso"
    else:
        user_normalized = u_ans_lower
    
    correct_normalized = ""
    c_ans_lower = correct.lower()
    if c_ans_lower in ["verdadero", "true", "v", "t"]:
        correct_normalized = "verdadero"
    elif c_ans_lower in ["falso", "false", "f"]:
        correct_normalized = "falso"
    else:
        correct_normalized = c_ans_lower
    
    result = user_normalized == correct_normalized
    print(f"User: {user}, Correct: {correct}")
    print(f"User norm: {user_normalized}, Correct norm: {correct_normalized}")
    print(f"Result: {result}, Match expected: {result == expected}\n")
