#!/usr/bin/env python3
"""
RAILWAY MODULE FIX: Final solution for module import errors
"""
import os
import sys
import subprocess
import shutil

print("🚀 RAILWAY MODULE FIX - Solving Import Issues")

# Set environment variables
port = os.environ.get('PORT', '8080')
os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"

print(f"🌐 Port: {port}")
print(f"📁 Initial working directory: {os.getcwd()}")

# Ensure we're in the right directory (/app)
if not os.getcwd().endswith('/app'):
    os.chdir('/app')
    print(f"📁 Changed to: {os.getcwd()}")

# Debug: Check what files exist
print("\n📂 Files in /app:")
for item in sorted(os.listdir('.')):
    if os.path.isdir(item):
        print(f"  📁 {item}/")
    else:
        print(f"  📄 {item}")

# Check mi_app_estudio directory
if os.path.exists('mi_app_estudio'):
    print("\n📂 Files in mi_app_estudio/:")
    for item in sorted(os.listdir('mi_app_estudio')):
        if os.path.isdir(f'mi_app_estudio/{item}'):
            print(f"  📁 {item}/")
        else:
            print(f"  📄 {item}")

# Test imports
print("\n🔍 Testing imports:")
try:
    import mi_app_estudio
    print("✅ Successfully imported mi_app_estudio package")
    
    # Try to get the app
    try:
        from mi_app_estudio import app
        print("✅ Successfully imported app from mi_app_estudio")
    except ImportError as e:
        print(f"⚠️  Could not import app from mi_app_estudio: {e}")
        print("   Trying direct import...")
        try:
            from mi_app_estudio.mi_app_estudio import app
            print("✅ Successfully imported app via direct path")
        except ImportError as e2:
            print(f"❌ Failed direct import: {e2}")
            
except ImportError as e:
    print(f"❌ Failed to import mi_app_estudio package: {e}")
    print("   This means Python can't find the mi_app_estudio module")

# Final attempt to verify everything is working
print("\n🎯 Final verification:")
try:
    # This is what reflex will try to do
    import mi_app_estudio.mi_app_estudio
    print("✅ Module mi_app_estudio.mi_app_estudio is importable")
    
    # Check if it has an app
    if hasattr(mi_app_estudio.mi_app_estudio, 'app'):
        print("✅ Module has 'app' attribute")
    else:
        print("⚠️  Module does not have 'app' attribute")
        
except ImportError as e:
    print(f"❌ Cannot import mi_app_estudio.mi_app_estudio: {e}")
    print("   This is the exact error Reflex is encountering")

# Start Reflex
print(f"\n🚀 Starting Reflex on port {port}")
cmd = [
    sys.executable, '-m', 'reflex', 'run', 
    '--backend-host', '0.0.0.0', 
    '--backend-port', port
]

print(f"Command: {' '.join(cmd)}")
print("=" * 50)

# Execute
try:
    os.execv(sys.executable, cmd)
except Exception as e:
    print(f"❌ Failed to execute reflex: {e}")
    sys.exit(1)
