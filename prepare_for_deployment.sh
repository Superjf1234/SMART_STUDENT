#!/bin/bash
# Script to prepare all fixed files for deployment

echo "===== PREPARING ALL FIXED FILES FOR DEPLOYMENT ====="

# List of files to stage
files_to_add=(
  "/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py"
  "/workspaces/SMART_STUDENT/Procfile"
  "/workspaces/SMART_STUDENT/railway_direct_fix.py"
  "/workspaces/SMART_STUDENT/RAILWAY_ASSERTION_ERROR_FIX.md"
  "/workspaces/SMART_STUDENT/verify_railway_fix.sh"
)

# Add all files to git
for file in "${files_to_add[@]}"; do
  if [ -f "$file" ]; then
    git add "$file"
    echo "✅ Added $file to git staging"
  else
    echo "⚠️ Warning: $file not found, skipping"
  fi
done

echo ""
echo "All files have been staged for commit."
echo ""
echo "To complete the deployment:"
echo "1. Commit the changes:"
echo "   git commit -m \"Fix: Add missing components to rx.cond() calls\""
echo ""
echo "2. Push to GitHub:"
echo "   git push origin main"
echo ""
echo "3. Deploy to Railway using your preferred method"
echo "   (GitHub integration or Railway CLI)"
echo ""
echo "===== PREPARATION COMPLETE ====="
