#!/bin/bash

echo "=== DEPLOYMENT TO RAILWAY - FINAL FIX ==="
echo "Deploying with unified port configuration and production setup"

# Verificar archivos críticos
echo "Checking critical files..."

if [ ! -f "railway_production.py" ]; then
    echo "❌ railway_production.py missing"
    exit 1
fi

if [ ! -f "Procfile" ]; then
    echo "❌ Procfile missing"
    exit 1
fi

if [ ! -f "rxconfig.py" ]; then
    echo "❌ rxconfig.py missing"
    exit 1
fi

echo "✅ All critical files present"

# Mostrar configuración actual
echo ""
echo "=== CURRENT CONFIGURATION ==="
echo "Procfile:"
cat Procfile
echo ""

echo "rxconfig.py port section:"
grep -A 5 -B 5 "port.*=" rxconfig.py

echo ""
echo "=== DEPLOY COMMANDS ==="
echo "Run these commands to deploy:"
echo ""
echo "git add ."
echo "git commit -m 'Fix: Unified port configuration for Railway deployment'"
echo "git push origin main"
echo ""
echo "Or if using Railway CLI:"
echo "railway up"
echo ""
echo "=== POST-DEPLOY VERIFICATION ==="
echo "After deployment, check:"
echo "1. Railway logs for startup messages"
echo "2. App accessibility at your Railway URL"
echo "3. No 'Not Found' errors"
echo ""
echo "Expected behavior:"
echo "- Single port (8080) serving both frontend and backend"
echo "- No localhost:3000 references in logs"
echo "- App accessible via Railway public URL"
