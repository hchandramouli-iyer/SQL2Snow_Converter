#!/bin/bash

# Repository Cleanup Script
# Removes large executable files from Git repository

echo "🧹 Cleaning up repository - removing large executable files"
echo "==========================================================="

# Remove the large deployment folder from repository
echo "📁 Removing CodeCraft-AI-Windows-v1.0.0/ from Git tracking..."
git rm -r --cached frontend/CodeCraft-AI-Windows-v1.0.0/ 2>/dev/null || echo "  ℹ️  Folder not tracked by Git (already clean)"

# Add to .gitignore to prevent future accidental commits
echo "🚫 Adding executables to .gitignore..."
cat >> .gitignore << 'EOF'

# Desktop App Build Outputs (use GitHub Releases instead)
frontend/dist/
frontend/*.zip
frontend/CodeCraft-AI-Windows-*/
frontend/*.exe
EOF

# Clean any accidentally committed ZIP files
echo "🗑️ Removing any ZIP files from Git tracking..."
git rm --cached frontend/*.zip 2>/dev/null || echo "  ℹ️  No ZIP files to remove"

echo ""
echo "✅ Repository cleanup complete!"
echo ""
echo "📋 What was cleaned:"
echo "  • Large executable files removed from Git"
echo "  • .gitignore updated to prevent future commits"
echo "  • Repository now contains only source code"
echo ""
echo "🚀 Next steps:"
echo "  1. Commit these changes: git commit -m 'Clean up: remove large files, use releases for distribution'"
echo "  2. Push to GitHub: git push"
echo "  3. Create GitHub Release with ZIP file"
echo ""
echo "💡 Remember: Users will download the app from GitHub Releases, not from the repository files."