#!/usr/bin/env python3
"""
RAILWAY ROOT EXEC: Execute from /app root directory
"""
import os
import sys

print("🎯 RAILWAY ROOT EXEC")
port = os.environ.get('PORT', '8080')
os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"

# ALWAYS execute from /app (root) where rxconfig.py is
os.chdir('/app')
print(f"📁 Working from: {os.getcwd()}")

# Simple reflex command
cmd = [sys.executable, '-m', 'reflex', 'run', '--backend-host', '0.0.0.0', '--backend-port', port]
os.execv(sys.executable, cmd)
