"""
Entry point for the SMART_STUDENT application.
This file imports the actual application from the mi_app_estudio package.
"""

# Import the necessary modules from the package
from mi_app_estudio.mi_app_estudio import *

# This ensures that when Reflex runs this file, it finds all the necessary components
if __name__ == "__main__":
    app.compile()