#!/usr/bin/env python3
import reflex as rx
import os
import sys

# Set PYTHONPATH
current_dir = os.getcwd()
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "mi_app_estudio"))

try:
    # Attempt import
    from mi_app_estudio.evaluaciones import EvaluationState
    from mi_app_estudio.mi_app_estudio import vista_pregunta_activa
    
    print("Successfully imported modules!")
    
    # Create simple app using the components
    app = rx.App()
    def index():
        return rx.fragment(
            rx.vstack(
                rx.heading("Test App"),
                rx.text("Testing vista_pregunta_activa functionality"),
                rx.divider(),
            )
        )
    
    print("Successfully initialized test app!")
    
except Exception as e:
    import traceback
    print("Error:", str(e))
    traceback.print_exc()

print("Test complete!")
