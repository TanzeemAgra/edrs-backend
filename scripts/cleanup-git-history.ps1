# Git History Cleanup Script
# This script removes sensitive data from git history

# IMPORTANT: Run these commands to completely remove secrets from git history

# 1. Install BFG Repo-Cleaner (recommended method)
# Download from: https://rtyley.github.io/bfg-repo-cleaner/
# Or install via package manager

# 2. Create a file with patterns to remove
echo "OPENAI_API_KEY" > secrets.txt
echo "AWS_ACCESS_KEY_ID" > secrets.txt  
echo "AWS_SECRET_ACCESS_KEY" > secrets.txt
echo "AWS_SES_SMTP_PASSWORD" > secrets.txt
echo "sk-proj-" >> secrets.txt
echo "AKIA" >> secrets.txt
echo "localpassword123" >> secrets.txt

# 3. Run BFG to remove secrets from history
# java -jar bfg.jar --replace-text secrets.txt --no-blob-protection .

# 4. Clean up the repository
# git reflog expire --expire=now --all && git gc --prune=now --aggressive

# 5. Force push the cleaned history (WARNING: This rewrites history)
# git push --force-with-lease origin main

# Alternative manual method (if BFG not available):
# git filter-branch --force --index-filter \
#   'git rm --cached --ignore-unmatch backend/.env backend/.env.local' \
#   --prune-empty --tag-name-filter cat -- --all

Write-Host "⚠️  SECURITY CLEANUP REQUIRED ⚠️"
Write-Host ""
Write-Host "The repository history still contains exposed secrets."
Write-Host "You need to clean the git history to completely remove them."
Write-Host ""
Write-Host "Options:"
Write-Host "1. Use BFG Repo-Cleaner (recommended)"
Write-Host "2. Use git filter-branch (manual)"
Write-Host "3. Create a new repository (nuclear option)"
Write-Host ""
Write-Host "See SECURITY.md for detailed instructions."