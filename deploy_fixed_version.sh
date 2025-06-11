#!/bin/bash
# Deploy the fixed version to Railway

echo "===== DEPLOYING FIXED VERSION TO RAILWAY ====="
echo "This script will deploy the simplified version to fix the Railway error"

# Create simplified Procfile for deployment
cat > Procfile << EOL
web: python -m railway_fix
EOL

echo "Created simplified Procfile"

# Add simplified version to git
git add railway_fix.py Procfile
git commit -m "Fix: Deploy simplified version to debug Railway issue"

# Push to Railway
echo "Pushing to Railway..."
git push railway main

echo "===== DEPLOYMENT COMPLETE ====="
echo "Check your Railway dashboard for deployment status"
