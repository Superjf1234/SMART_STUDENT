# Simple file to identify where the error is occurring
import reflex as rx
import mi_app_estudio.evaluaciones
import mi_app_estudio.mi_app_estudio
import mi_app_estudio.cuestionario
from mi_app_estudio.evaluaciones import EvaluationState

def check_usage():
    # Check if the function exists as described in the error
    import inspect
    from mi_app_estudio.mi_app_estudio import vista_pregunta_activa
    
    # Get the source code
    src = inspect.getsource(vista_pregunta_activa)
    # Check for specific patterns
    if "EvaluationState.eval_user_answers.get" in src:
        print("Found problematic pattern in vista_pregunta_activa")
        
    # Look for lambda functions that might cause issues
    import re
    lambdas = re.findall(r'lambda.*EvaluationState\.eval_user_answers', src)
    if lambdas:
        print(f"Found {len(lambdas)} lambda functions using eval_user_answers:")
        for l in lambdas:
            print(f"  {l[:100]}...")

check_usage()
