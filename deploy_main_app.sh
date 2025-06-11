#!/bin/bash
# Deploy the fixed application to Railway

echo "===== DEPLOYING FIXED APP TO RAILWAY ====="
echo "This script will deploy the corrected application to Railway"

# Create Procfile for deployment
cat > Procfile << EOL
web: reflex init && reflex run --env prod --backend-only
EOL

echo "Created Procfile for main application"

# Add to git
git add Procfile
git commit -m "Fix: Update Procfile for Railway deployment with fixed code"

# Push to Railway
echo "Pushing to Railway..."
git push railway main

echo "===== DEPLOYMENT COMPLETE ====="
echo "Check your Railway dashboard for deployment status"
