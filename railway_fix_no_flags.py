#!/usr/bin/env python3
"""
RAILWAY FIX: Sin flags no existentes
"""

import os
import sys

print("🆘 RAILWAY EMERGENCY FIX")

# Setup
port = os.environ.get("PORT", "8080")
os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
os.environ["PYTHONPATH"] = "/app:/app/mi_app_estudio"

# Change dir
os.chdir("/app/mi_app_estudio")
print(f"Dir: {os.getcwd()}")

# Import test
sys.path.insert(0, "/app")
sys.path.insert(0, "/app/mi_app_estudio")
import mi_app_estudio.mi_app_estudio
print("✅ Import OK")

# Start - ONLY basic flags
cmd = [
    sys.executable, "-m", "reflex", "run",
    "--backend-host", "0.0.0.0", 
    "--backend-port", port
]

print(f"CMD: {' '.join(cmd)}")
os.execv(sys.executable, cmd)
