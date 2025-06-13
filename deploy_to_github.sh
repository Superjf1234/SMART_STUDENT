#!/bin/bash
# Script to push changes to GitHub, from where Railway can be configured to auto-deploy

echo "===== PUSHING FIXED VERSION TO GITHUB ====="
echo "This script will push the fixed version to GitHub"

# Add all changes
git add .

# Commit the changes
git commit -m "Fix: Railway deployment error - AssertionError in rx.cond()"

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

echo "===== PUSH TO GITHUB COMPLETE ====="
echo "Now you can set up Railway to deploy from your GitHub repository"
echo "1. Go to https://railway.app/"
echo "2. Create a new project"
echo "3. Select 'Deploy from GitHub repository'"
echo "4. Select your SMART_STUDENT repository"
echo "5. Railway will automatically deploy the project"
