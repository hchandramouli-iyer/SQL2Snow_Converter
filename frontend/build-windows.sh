#!/bin/bash

# CodeCraft AI Windows Desktop App Builder
# Creates Windows executables that run without admin rights

echo "🪟 CodeCraft AI Windows Desktop App Builder"
echo "=========================================="

cd "$(dirname "$0")"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ to continue."
    exit 1
fi

# Check if Yarn is installed
if ! command -v yarn &> /dev/null; then
    echo "❌ Yarn is not installed. Please install Yarn to continue."
    exit 1
fi

echo "✅ Node.js and Yarn are available"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    yarn install
fi

# Build the React app
echo "🏗️ Building React application for Windows..."
yarn build

if [ $? -ne 0 ]; then
    echo "❌ React build failed"
    exit 1
fi

echo "✅ React build completed successfully"

echo "📦 Building Windows desktop applications..."
echo "   This will create:"
echo "   • Portable executable (no installation needed)"
echo "   • User-level installer (no admin rights required)"
echo "   • ZIP package (extract and run)"

# Build Windows versions
yarn dist-win

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Windows builds completed successfully!"
    echo ""
    echo "📁 Build outputs:"
    if [ -d "dist" ]; then
        find dist -name "*.exe" -o -name "*.zip" | while read file; do
            size=$(du -h "$file" 2>/dev/null | cut -f1)
            echo "   ✅ $file ($size)"
        done
    fi
    echo ""
    echo "📋 Usage Instructions:"
    echo "   • Portable .exe: Double-click to run (no installation)"
    echo "   • Installer .exe: Installs to user folder (no admin needed)"
    echo "   • .zip file: Extract and run CodeCraft AI.exe"
    echo ""
    echo "🚀 Ready for deployment to Windows machines!"
else
    echo "❌ Windows build failed. Check the output above for errors."
    exit 1
fi