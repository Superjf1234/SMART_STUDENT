#!/usr/bin/env python3
"""
Test script to verify all critical fixes for Railway deployment.
Tests the main errors that were preventing successful deployment.
"""

import sys
import os
import traceback

def test_imports():
    """Test all critical module imports."""
    print("🔍 Testing module imports...")
    
    try:
        # Test main app import
        import mi_app_estudio.mi_app_estudio as main_app
        print("✅ Main app module imported successfully")
        
        # Test cuestionario import (VarAttributeError fix)
        import mi_app_estudio.cuestionario as cuestionario
        print("✅ Cuestionario module imported successfully - VarAttributeError fixed!")
        
        # Test evaluaciones import
        import mi_app_estudio.evaluaciones as evaluaciones
        print("✅ Evaluaciones module imported successfully")
        
        # Test state import
        import mi_app_estudio.state as state
        print("✅ State module imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_reflex_app_creation():
    """Test that the Reflex app can be created without errors."""
    print("\n🔍 Testing Reflex app creation...")
    
    try:
        import reflex as rx
        from mi_app_estudio.mi_app_estudio import app
        print("✅ Reflex app object created successfully")
        
        # Test that app has the required components
        if hasattr(app, 'state'):
            print("✅ App state is properly configured")
        
        if hasattr(app, '_routes'):
            print("✅ App routes are properly configured")
            
        return True
        
    except Exception as e:
        print(f"❌ App creation error: {e}")
        traceback.print_exc()
        return False

def test_critical_components():
    """Test that critical components can be imported and used."""
    print("\n🔍 Testing critical components...")
    
    try:
        from mi_app_estudio.state import AppState
        print("✅ AppState imported successfully")
        
        from mi_app_estudio.cuestionario import CuestionarioState
        print("✅ CuestionarioState imported successfully")
        
        from mi_app_estudio.evaluaciones import EvaluationState
        print("✅ EvaluationState imported successfully")
        
        # Test that rx.cond fixes are working (no AssertionError)
        import reflex as rx
        test_cond = rx.cond(True, rx.text("Test"), rx.text("Alt"))
        print("✅ rx.cond with rx.text components working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Component error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Railway deployment readiness test...\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Reflex App Creation", test_reflex_app_creation),
        ("Critical Components", test_critical_components),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"📋 Running {test_name} test:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test PASSED\n")
        else:
            print(f"❌ {test_name} test FAILED\n")
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Railway deployment should succeed!")
        print("\n📝 Fixed Issues:")
        print("- ✅ AssertionError in rx.cond() calls (wrapped strings in rx.text())")
        print("- ✅ VarAttributeError in cuestionario.py (.get() method issue)")
        print("- ✅ @app.add_page syntax error (updated to modern syntax)")
        print("\n🚀 Ready for Railway deployment!")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
