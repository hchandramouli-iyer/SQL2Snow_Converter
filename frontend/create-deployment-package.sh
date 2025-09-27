#!/bin/bash

# CodeCraft AI Windows Deployment Package Creator
# Creates a complete Windows deployment package

echo "📦 Creating Windows Deployment Package..."
echo "========================================"

cd "$(dirname "$0")"

# Check if Windows build exists
if [ ! -d "dist/win-unpacked" ]; then
    echo "❌ Windows build not found. Building now..."
    yarn dist-win
    if [ $? -ne 0 ]; then
        echo "❌ Windows build failed"
        exit 1
    fi
fi

# Create deployment directory
DEPLOY_DIR="CodeCraft-AI-Windows-v1.0.0"
echo "📁 Creating deployment directory: $DEPLOY_DIR"

rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy Windows executable and resources
echo "📋 Copying Windows application files..."
cp -r dist/win-unpacked/* "$DEPLOY_DIR/"

# Rename electron.exe to CodeCraftAI.exe if needed
if [ -f "$DEPLOY_DIR/electron.exe" ] && [ ! -f "$DEPLOY_DIR/CodeCraftAI.exe" ]; then
    mv "$DEPLOY_DIR/electron.exe" "$DEPLOY_DIR/CodeCraftAI.exe"
    echo "✅ Renamed electron.exe to CodeCraftAI.exe"
fi

# Copy documentation and scripts
echo "📄 Adding documentation and scripts..."
cp README.txt "$DEPLOY_DIR/"
cp start-codecraft-ai.bat "$DEPLOY_DIR/"

# Create version info
cat > "$DEPLOY_DIR/VERSION.txt" << EOF
CodeCraft AI Desktop - Windows Edition
Version: 1.0.0
Build Date: $(date)
Platform: Windows (64-bit/32-bit compatible)
License: MIT
No Admin Rights Required: YES

File Information:
- CodeCraftAI.exe: Main application ($(du -h "$DEPLOY_DIR/CodeCraftAI.exe" 2>/dev/null | cut -f1 || echo "~200MB"))
- start-codecraft-ai.bat: Launcher script
- README.txt: Complete usage guide
- resources/: Application assets
EOF

# Create deployment instructions
cat > "$DEPLOY_DIR/DEPLOYMENT_INSTRUCTIONS.txt" << EOF
# CodeCraft AI - Windows Deployment Instructions

## For IT Administrators:

### Network Deployment:
1. Copy entire '$DEPLOY_DIR' folder to network share
2. Users can run CodeCraftAI.exe directly from network
3. No installation or admin rights required

### USB Deployment:
1. Copy entire folder to USB drives
2. Distribute to users
3. Users can run from USB or copy to local machine

### Email Deployment:
1. ZIP the entire folder
2. Email to users with README.txt instructions
3. Users extract and run immediately

## For End Users:

### Quick Start:
1. Extract files to any folder (Desktop, Documents, etc.)
2. Double-click CodeCraftAI.exe OR start-codecraft-ai.bat
3. Allow Windows Defender if prompted
4. Start using immediately - no setup required

### Permanent Installation:
1. Copy folder to: C:\Users\%USERNAME%\AppData\Local\Programs\
2. Create desktop shortcut to CodeCraftAI.exe
3. Pin to taskbar for easy access

## Troubleshooting:
- If Windows blocks: Right-click exe → Properties → Unblock
- If antivirus blocks: Add folder to exceptions
- If slow: Ensure 4GB+ RAM available
- If network issues: Check corporate firewall

## Security Notes:
✅ No admin rights required
✅ No system modifications
✅ Sandboxed execution
✅ Corporate environment safe
✅ Portable - runs from any location
EOF

# Create ZIP package for distribution
echo "🗜️ Creating ZIP package for distribution..."
zip -r "${DEPLOY_DIR}.zip" "$DEPLOY_DIR/" > /dev/null 2>&1

# Calculate sizes
DIR_SIZE=$(du -sh "$DEPLOY_DIR" 2>/dev/null | cut -f1)
ZIP_SIZE=$(du -sh "${DEPLOY_DIR}.zip" 2>/dev/null | cut -f1)

echo ""
echo "🎉 Windows Deployment Package Created Successfully!"
echo ""
echo "📁 Deployment Folder: $DEPLOY_DIR/ ($DIR_SIZE)"
echo "🗜️ ZIP Package: ${DEPLOY_DIR}.zip ($ZIP_SIZE)"
echo ""
echo "📋 Package Contents:"
find "$DEPLOY_DIR" -type f -name "*.exe" -o -name "*.bat" -o -name "*.txt" | while read file; do
    size=$(du -h "$file" 2>/dev/null | cut -f1)
    echo "   ✅ $(basename "$file") ($size)"
done
echo ""
echo "🚀 Ready for Windows deployment!"
echo ""
echo "Distribution Options:"
echo "1. 📁 Share folder: $DEPLOY_DIR/"
echo "2. 📧 Email: ${DEPLOY_DIR}.zip"
echo "3. 💾 USB: Copy folder to USB drives"
echo "4. 🌐 Network: Place on shared network drive"
echo ""
echo "Users can run CodeCraftAI.exe without admin rights! 🎯"