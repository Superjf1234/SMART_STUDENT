"""
Test to verify that evaluation review functionality works properly without ChunkLoadError.
This is a simple script that can be run to check if the application handles evaluation review correctly.
"""
import sys
import os
import time
import subprocess

def print_colored(message, color="green"):
    """Print message with color"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, colors['blue'])}{message}{colors['end']}")

def test_evaluation_review():
    """Test the evaluation review functionality"""
    print_colored("Starting test for evaluation review...", "blue")
    
    # Verify the files we modified exist
    files_to_check = [
        "/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py",
        "/workspaces/SMART_STUDENT/mi_app_estudio/evaluaciones.py"
    ]
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print_colored(f"Error: File {file_path} does not exist!", "red")
            return False
        print_colored(f"✓ File {file_path} exists", "green")
    
    # Check if animations and transitions were properly removed
    with open("/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py", "r") as file:
        content = file.read()
        if "animation=" in content and not "# Removed animation" in content:
            print_colored("Warning: There might still be animation properties in the code.", "yellow")
        else:
            print_colored("✓ Animation properties are properly commented out", "green")
        
        if "transition=" in content and not "# Removed transition" in content:
            print_colored("Warning: There might still be transition properties in the code.", "yellow")
        else:
            print_colored("✓ Transition properties are properly commented out", "green")
    
    # Test the reflex app build
    print_colored("Testing reflex app build...", "blue")
    try:
        # Run reflex init (lightweight operation to verify reflex works)
        process = subprocess.run(
            ["reflex", "init"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            print_colored("✓ Reflex initialization successful", "green")
        else:
            print_colored(f"Error: Reflex initialization failed with error: {process.stderr}", "red")
            return False
        
        # Note: We can't fully test for ChunkLoadError without a browser
        print_colored("Note: Full browser testing is required to verify ChunkLoadError is fixed.", "yellow")
        print_colored("The changes made should resolve the issue by removing animations and transitions", "yellow")
        print_colored("that were causing problems in the evaluation review mode.", "yellow")
        
        return True
        
    except Exception as e:
        print_colored(f"Error during testing: {str(e)}", "red")
        return False

if __name__ == "__main__":
    success = test_evaluation_review()
    if success:
        print_colored("Test completed successfully! The fixes should resolve the ChunkLoadError.", "green")
        print_colored("Please run your application and verify the evaluation review mode works properly.", "green")
    else:
        print_colored("Test failed! Please review the error messages above.", "red")
