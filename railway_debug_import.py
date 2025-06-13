#!/usr/bin/env python3
"""
RAILWAY DEBUG IMPORT: Debug module import issues
"""
import os
import sys
import subprocess

print("🔍 RAILWAY DEBUG IMPORT")
print(f"📁 Current directory: {os.getcwd()}")
print(f"🐍 Python path: {sys.path}")

# List files in current directory
print("\n📂 Files in current directory:")
for item in os.listdir('.'):
    print(f"  {item}")

# Check if mi_app_estudio directory exists
if os.path.exists('mi_app_estudio'):
    print("\n📂 Files in mi_app_estudio directory:")
    for item in os.listdir('mi_app_estudio'):
        print(f"  {item}")

# Try importing
print("\n🔍 Testing imports:")
try:
    import mi_app_estudio
    print("✅ Successfully imported mi_app_estudio")
except ImportError as e:
    print(f"❌ Failed to import mi_app_estudio: {e}")

try:
    from mi_app_estudio import mi_app_estudio
    print("✅ Successfully imported mi_app_estudio.mi_app_estudio")
except ImportError as e:
    print(f"❌ Failed to import mi_app_estudio.mi_app_estudio: {e}")

try:
    import mi_app_estudio.mi_app_estudio
    print("✅ Successfully imported mi_app_estudio.mi_app_estudio as module")
except ImportError as e:
    print(f"❌ Failed to import mi_app_estudio.mi_app_estudio as module: {e}")

# Check reflex config
print("\n⚙️ Checking reflex config:")
try:
    import reflex as rx
    config = rx.Config()
    print(f"  app_name: {config.app_name}")
except Exception as e:
    print(f"❌ Error reading config: {e}")

# Set environment and try starting
port = os.environ.get('PORT', '8080')
os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"

print(f"\n🚀 Attempting to start reflex on port {port}")
cmd = [sys.executable, '-m', 'reflex', 'run', '--backend-host', '0.0.0.0', '--backend-port', port]
print(f"Command: {' '.join(cmd)}")

# Execute the command
os.execv(sys.executable, cmd)
