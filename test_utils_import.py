#!/usr/bin/env python3
"""
Test script to isolate the utils import issue
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, '.')

print("Starting import test...")

try:
    print("Step 1: Testing basic imports")
    import os
    import datetime
    from fpdf import FPDF
    from typing import List, Dict, Any, Optional
    print("✓ Basic imports successful")
    
    print("Step 2: Testing utils module import")
    import mi_app_estudio.utils
    print("✓ Utils module imported")
    
    print("Step 3: Testing specific function import")
    from mi_app_estudio.utils import generate_pdf_report_from_answers
    print("✓ Function imported successfully")
    
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()

print("Test completed!")
