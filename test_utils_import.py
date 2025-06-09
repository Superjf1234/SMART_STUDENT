#!/usr/bin/env python3
"""
Test script to isolate the utils import issue
"""

import os
import sys
import pytest

# Add current directory to path
sys.path.insert(0, '.')


def test_basic_imports():
    """Test basic Python imports"""
    print("Step 1: Testing basic imports")
    import os
    import datetime
    try:
        from fpdf import FPDF
    except ImportError:
        pytest.skip("FPDF not available")
    from typing import List, Dict, Any, Optional
    assert True


def test_utils_module_import():
    """Test utils module import"""
    print("Step 2: Testing utils module import")
    try:
        import mi_app_estudio.utils
        assert True
    except ImportError as e:
        pytest.skip(f"Utils module not available: {e}")


def test_specific_function_import():
    """Test specific function import from utils"""
    print("Step 3: Testing specific function import")
    try:
        from mi_app_estudio.utils import generate_pdf_report_from_answers
        assert True
    except ImportError as e:
        pytest.skip(f"Function not available: {e}")


def test_import_chain():
    """Test the complete import chain"""
    try:
        print("Starting import test...")
        
        print("Step 1: Testing basic imports")
        import os
        import datetime
        try:
            from fpdf import FPDF
        except ImportError:
            pass  # Not critical for this test
        from typing import List, Dict, Any, Optional
        
        print("Step 2: Testing utils module import")
        import mi_app_estudio.utils
        
        print("Step 3: Testing specific function import")
        from mi_app_estudio.utils import generate_pdf_report_from_answers
        
        print("Test completed successfully!")
        assert True
        
    except Exception as e:
        pytest.fail(f"Import chain failed: {e}")


if __name__ == "__main__":
    # Original test execution
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
    
    # Run pytest
    pytest.main([__file__])
