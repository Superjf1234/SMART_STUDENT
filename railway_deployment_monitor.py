#!/usr/bin/env python3
"""
Script de monitoreo para verificar el estado de Railway después del fix
"""
import os
import sys
import time
import requests
from datetime import datetime

def check_railway_status():
    """Verificar el estado del deployment en Railway"""
    print("🔍 Verificando estado de Railway...")
    
    # URL de tu aplicación en Railway (reemplaza con la tuya)
    railway_url = "https://smart-student-production.up.railway.app"
    
    try:
        print(f"📡 Conectando a: {railway_url}")
        response = requests.get(railway_url, timeout=30)
        
        if response.status_code == 200:
            print("✅ ¡Aplicación funcionando correctamente!")
            print(f"📊 Status Code: {response.status_code}")
            print(f"⏱️  Tiempo de respuesta: {response.elapsed.total_seconds():.2f}s")
            return True
        else:
            print(f"⚠️  Respuesta inesperada: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - La aplicación podría estar iniciando")
        return False
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - La aplicación está tardando en responder")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def monitor_deployment(duration_minutes=5):
    """Monitorear el deployment por un tiempo determinado"""
    print(f"🕐 Monitoreando deployment por {duration_minutes} minutos...")
    
    start_time = datetime.now()
    check_interval = 30  # segundos
    
    while True:
        current_time = datetime.now()
        elapsed = (current_time - start_time).total_seconds()
        
        if elapsed > duration_minutes * 60:
            print("⏰ Tiempo de monitoreo completado")
            break
            
        print(f"\n--- Verificación {int(elapsed/check_interval + 1)} ---")
        print(f"🕐 Tiempo transcurrido: {elapsed/60:.1f} minutos")
        
        if check_railway_status():
            print("🎉 ¡Deployment exitoso! La aplicación está funcionando.")
            return True
            
        print(f"⏳ Esperando {check_interval} segundos antes de la siguiente verificación...")
        time.sleep(check_interval)
    
    print("❌ El deployment no se completó exitosamente en el tiempo esperado")
    return False

def check_logs_suggestions():
    """Sugerir cómo revisar logs en caso de problemas"""
    print("\n📋 Si hay problemas, revisa:")
    print("1. 🔗 Railway Dashboard > Deploy Logs")
    print("2. 🔗 Railway Dashboard > Build Logs") 
    print("3. 📄 Variables de entorno configuradas")
    print("4. 📦 Procfile apuntando a emergency_railway_simple.py")
    print("\n🔧 Scripts de respaldo disponibles:")
    print("- railway_final_fix.py")
    print("- ultra_minimal_railway.py")

if __name__ == "__main__":
    print("🚀 RAILWAY DEPLOYMENT MONITOR")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script activo: emergency_railway_simple.py")
    print("=" * 50)
    
    # Verificación inmediata
    if check_railway_status():
        print("🎉 ¡La aplicación ya está funcionando!")
        sys.exit(0)
    
    # Monitoreo continuo
    success = monitor_deployment(5)
    
    if not success:
        check_logs_suggestions()
        sys.exit(1)
    
    sys.exit(0)
