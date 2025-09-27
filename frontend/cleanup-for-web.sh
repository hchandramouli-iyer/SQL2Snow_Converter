#!/bin/bash

# CodeCraft AI Repository Cleanup Script
# Converts from desktop app back to standalone web application

echo "🧹 CodeCraft AI - Repository Cleanup for Web Application"
echo "========================================================"
echo ""
echo "This will remove all desktop-specific files and restore the app as a standalone website."
echo ""

cd "$(dirname "$0")"

# Remove desktop-specific build outputs
echo "🗑️  Removing desktop build outputs..."
rm -rf dist/
rm -rf CodeCraft-AI-Windows-v1.0.0/
rm -f *.zip
rm -f *build*.log
rm -f windows_build*.log
rm -f electron_build.log

# Remove desktop-specific files
echo "🖥️  Removing desktop application files..."
rm -f electron.js
rm -f *.bat
rm -f build-windows.sh
rm -f run-desktop.sh
rm -f create-deployment-package.sh

# Remove desktop-specific assets
echo "📁 Removing desktop assets..."
rm -rf assets/

# Remove desktop-specific documentation
echo "📄 Removing desktop documentation..."
rm -f DESKTOP_APP_STATUS.md
rm -f WINDOWS_DEPLOYMENT*.md
rm -f README.txt

# Remove Electron and build dependencies from package.json
echo "📦 Cleaning up package.json..."

# Create clean package.json
cat > package.json << 'EOF'
{
  "name": "codecraft-ai-web",
  "version": "1.0.0",
  "private": true,
  "homepage": "https://hchandramouli-iyer.github.io/SQL2Snow_Converter",
  "dependencies": {
    "@hookform/resolvers": "^5.0.1",
    "@radix-ui/react-accordion": "^1.2.8",
    "@radix-ui/react-alert-dialog": "^1.1.11",
    "@radix-ui/react-aspect-ratio": "^1.1.4",
    "@radix-ui/react-avatar": "^1.1.7",
    "@radix-ui/react-checkbox": "^1.2.3",
    "@radix-ui/react-collapsible": "^1.1.8",
    "@radix-ui/react-context-menu": "^2.2.12",
    "@radix-ui/react-dialog": "^1.1.11",
    "@radix-ui/react-dropdown-menu": "^2.1.12",
    "@radix-ui/react-hover-card": "^1.1.11",
    "@radix-ui/react-label": "^2.1.4",
    "@radix-ui/react-menubar": "^1.1.12",
    "@radix-ui/react-navigation-menu": "^1.2.10",
    "@radix-ui/react-popover": "^1.1.11",
    "@radix-ui/react-progress": "^1.1.4",
    "@radix-ui/react-radio-group": "^1.3.4",
    "@radix-ui/react-scroll-area": "^1.2.6",
    "@radix-ui/react-select": "^2.2.2",
    "@radix-ui/react-separator": "^1.1.4",
    "@radix-ui/react-slider": "^1.3.2",
    "@radix-ui/react-slot": "^1.2.0",
    "@radix-ui/react-switch": "^1.2.2",
    "@radix-ui/react-tabs": "^1.1.9",
    "@radix-ui/react-toast": "^1.2.11",
    "@radix-ui/react-toggle": "^1.1.6",
    "@radix-ui/react-toggle-group": "^1.1.7",
    "@radix-ui/react-tooltip": "^1.2.4",
    "axios": "^1.8.4",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "cmdk": "^1.1.1",
    "cra-template": "1.2.0",
    "date-fns": "^4.1.0",
    "embla-carousel-react": "^8.6.0",
    "input-otp": "^1.4.2",
    "lucide-react": "^0.507.0",
    "next-themes": "^0.4.6",
    "react": "^19.0.0",
    "react-day-picker": "8.10.1",
    "react-dom": "^19.0.0",
    "react-hook-form": "^7.56.2",
    "react-resizable-panels": "^3.0.1",
    "react-router-dom": "^7.5.1",
    "react-scripts": "5.0.1",
    "sonner": "^2.0.3",
    "tailwind-merge": "^3.2.0",
    "tailwindcss-animate": "^1.0.7",
    "vaul": "^1.1.2",
    "vis-data": "^8.0.3",
    "vis-network": "^10.0.2",
    "zod": "^3.24.4"
  },
  "scripts": {
    "start": "craco start",
    "build": "craco build",
    "test": "craco test",
    "predeploy": "yarn build",
    "deploy": "gh-pages -d build"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "@babel/plugin-proposal-private-property-in-object": "^7.21.11",
    "@craco/craco": "^7.1.0",
    "@eslint/js": "9.23.0",
    "autoprefixer": "^10.4.20",
    "eslint": "9.23.0",
    "eslint-plugin-import": "2.31.0",
    "eslint-plugin-jsx-a11y": "6.10.2",
    "eslint-plugin-react": "7.37.4",
    "gh-pages": "^6.3.0",
    "globals": "15.15.0",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.17"
  },
  "packageManager": "yarn@1.22.22+sha512.a6b2f7906b721bba3d67d4aff083df04dad64c399707841b7acf00f6b133b7ac24255f2652fa22ae3534329dc6180534e98d17432037ff6fd140556e2bb3137e"
}
EOF

# Remove Electron utilities from React app
echo "⚛️  Cleaning up React components..."
rm -f src/utils/electron.js

# Update .gitignore for web application
echo "🚫 Updating .gitignore..."
cat > .gitignore << 'EOF'
# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# production
/build

# misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

# logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
*.log

# IDE
.vscode/
.idea/

# Build outputs
dist/
*.zip
*.exe
*.dmg
*.deb
*.rpm
*.AppImage

# Desktop app files
electron.js
assets/icon.*
*.bat
EOF

# Remove Electron dependencies from node_modules and yarn.lock
echo "🧼 Cleaning dependencies..."
echo "⚠️  Note: Run 'yarn install' after this cleanup to refresh dependencies"

echo ""
echo "✅ Repository cleanup completed!"
echo ""
echo "📋 What was cleaned:"
echo "  ✅ Desktop build outputs removed (dist/, *.zip, *.exe)"
echo "  ✅ Electron configuration files removed"
echo "  ✅ Desktop-specific scripts and documentation removed"
echo "  ✅ Package.json restored for web application"
echo "  ✅ .gitignore updated for web development"
echo "  ✅ Desktop assets and utilities removed"
echo ""
echo "🚀 Next steps:"
echo "  1. Run: yarn install (to clean up dependencies)"
echo "  2. Run: yarn build (to test web build)"
echo "  3. Run: yarn start (to test locally)"
echo "  4. Deploy: yarn deploy (for GitHub Pages)"
echo ""
echo "🌐 Your CodeCraft AI is now a clean web application!"
echo "   Ready for GitHub Pages deployment at: https://hchandramouli-iyer.github.io/SQL2Snow_Converter"