#!/usr/bin/env python3
"""
EMERGENCIA ULTRA SIMPLE - Sin flags
"""
import os
import subprocess
import sys

# Setup mínimo
os.environ["PORT"] = os.environ.get("PORT", "8080")
os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
os.chdir("/app/mi_app_estudio")

# Comando básico sin flags problemáticos
cmd = [sys.executable, "-m", "reflex", "run", "--backend-host", "0.0.0.0", "--backend-port", os.environ["PORT"]]
subprocess.run(cmd)
