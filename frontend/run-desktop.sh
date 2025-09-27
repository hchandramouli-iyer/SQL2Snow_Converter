#!/bin/bash

# CodeCraft AI Desktop App Launcher
# This script builds and runs the CodeCraft AI desktop application

echo "🚀 CodeCraft AI Desktop App Builder"
echo "=================================="

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
echo "🏗️ Building React application..."
yarn build

if [ $? -ne 0 ]; then
    echo "❌ React build failed"
    exit 1
fi

echo "✅ React build completed successfully"

# Check if we should run or build
if [ "$1" = "dev" ]; then
    echo "🔄 Starting Electron in development mode..."
    yarn electron-dev
elif [ "$1" = "build" ]; then
    echo "📦 Building desktop application..."
    yarn dist
elif [ "$1" = "build-win" ]; then
    echo "📦 Building Windows desktop application..."
    yarn dist-win
elif [ "$1" = "build-mac" ]; then
    echo "📦 Building macOS desktop application..."
    yarn dist-mac
elif [ "$1" = "build-linux" ]; then
    echo "📦 Building Linux desktop application..."
    yarn dist-linux
else
    echo "🖥️ Starting desktop application..."
    yarn electron
fi

echo "🎉 CodeCraft AI Desktop App operation completed!"