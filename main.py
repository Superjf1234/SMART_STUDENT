"""
Entry point for the SMART_STUDENT application.
This file imports the actual application from the mi_app_estudio package.
"""
import os
import sys

# Add the current directory to the path to help with imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app from the mi_app_estudio package
from mi_app_estudio.mi_app_estudio import app

# Initialize the database if needed
from backend import db_logic
db_logic.inicializar_db()

# This ensures that when Reflex runs this file, it finds all the necessary components
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        # Standard way to run the app with reflex run
        import reflex as rx
        rx.run()
    else:
        # For backward compatibility, use the private method
        app._compile()