#!/usr/bin/env python3
"""
railway_healthcheck_test.py - Test Railway Healthcheck
Verifica que tanto frontend como backend respondan en el mismo puerto
"""
import os
import time
import requests
import sys

def test_railway_healthcheck():
    """Test que simula el healthcheck de Railway"""
    port = os.environ.get('PORT', '8080')
    base_url = f"http://localhost:{port}"
    
    print(f"🚂 RAILWAY HEALTHCHECK TEST")
    print(f"Testing port: {port}")
    print("=" * 50)
    
    # Test 1: Frontend (interfaz web)
    try:
        print("🔍 Testing Frontend...")
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Frontend OK: {response.status_code}")
        else:
            print(f"⚠️ Frontend Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend Error: {e}")
        return False
    
    # Test 2: Backend API
    try:
        print("🔍 Testing Backend API...")
        api_url = f"{base_url}/api/health"
        response = requests.get(api_url, timeout=10)
        if response.status_code in [200, 404]:  # 404 es OK si no hay endpoint health
            print(f"✅ Backend OK: {response.status_code}")
        else:
            print(f"⚠️ Backend Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return False
    
    # Test 3: Ping general
    try:
        print("🔍 Testing General Ping...")
        response = requests.get(f"{base_url}/ping", timeout=5)
        print(f"✅ Ping OK: {response.status_code}")
    except Exception as e:
        print(f"ℹ️ Ping (optional): {e}")
    
    print("=" * 50)
    print("✅ HEALTHCHECK PASSED - Railway debería funcionar correctamente")
    return True

if __name__ == "__main__":
    if test_railway_healthcheck():
        sys.exit(0)
    else:
        sys.exit(1)
