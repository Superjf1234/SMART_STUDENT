#!/usr/bin/env python3
"""
RAILWAY DIRECT - COPY CONFIG STRATEGY
"""

import os
import sys
import shutil

def main():
    """STRATEGY: Copy rxconfig.py to working directory"""
    
    print("� RAILWAY DIRECT - COPY CONFIG")
    print("=" * 50)
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"🔌 Puerto: {port}")
    print(f"🌐 Host: {host}")
    
    # GEMINI API KEY (fallback)
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("🔑 GEMINI_API_KEY configurado")
    
    # Paths
    base_path = '/app'
    app_path = '/app/mi_app_estudio'
    
    print(f"📁 Base: {base_path}")
    print(f"📁 App: {app_path}")
    
    # STRATEGY: Copy rxconfig.py to app directory and run from there
    try:
        # Check if rxconfig.py exists in base
        if os.path.exists(f'{base_path}/rxconfig.py'):
            print("✅ rxconfig.py found in base")
            
            # Copy to app directory
            shutil.copy(f'{base_path}/rxconfig.py', f'{app_path}/rxconfig.py')
            print("📋 Copied rxconfig.py to app dir")
            
        else:
            print("❌ rxconfig.py not found in base")
        
        # Always change to app directory
        os.chdir(app_path)
        print(f"📁 Working dir: {os.getcwd()}")
        
        # Verify rxconfig.py exists
        if os.path.exists('rxconfig.py'):
            print("✅ rxconfig.py available")
        else:
            print("⚠️ rxconfig.py not available, but continuing...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        # Continue anyway
    
    # Command
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}")
    
    # Execute
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
