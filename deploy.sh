#!/bin/bash

# CodeCraft AI Deployment Script
# This script helps prepare the project for deployment

echo "🚀 CodeCraft AI Deployment Preparation"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] && [ ! -d "frontend" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

print_status "Checking project structure..."

# Check required files
if [ ! -d "frontend" ]; then
    print_error "Frontend directory not found"
    exit 1
fi

if [ ! -d "backend" ]; then
    print_error "Backend directory not found" 
    exit 1
fi

if [ ! -f "frontend/package.json" ]; then
    print_error "Frontend package.json not found"
    exit 1
fi

if [ ! -f "backend/requirements.txt" ]; then
    print_error "Backend requirements.txt not found"
    exit 1
fi

print_success "Project structure validated"

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
if command -v yarn &> /dev/null; then
    yarn install
else
    npm install
fi

if [ $? -eq 0 ]; then
    print_success "Frontend dependencies installed"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi

# Build frontend for production
print_status "Building frontend for production..."
if command -v yarn &> /dev/null; then
    yarn build
else
    npm run build
fi

if [ $? -eq 0 ]; then
    print_success "Frontend build completed"
else
    print_error "Frontend build failed"
    exit 1
fi

cd ..

# Check if gh-pages is installed
print_status "Checking deployment dependencies..."
cd frontend
if yarn list gh-pages &> /dev/null; then
    print_success "gh-pages is already installed"
else
    print_warning "Installing gh-pages for GitHub Pages deployment..."
    if command -v yarn &> /dev/null; then
        yarn add --dev gh-pages
    else
        npm install --save-dev gh-pages
    fi
fi

cd ..

print_success "Deployment preparation completed!"
echo
echo "📋 Next Steps:"
echo "=============="
echo "1. 🔗 Create GitHub repository: hchandramouli-iyer/codecraft-ai"
echo "2. 🚀 Push this code to your GitHub repository"
echo "3. ⚙️  Set up MongoDB Atlas database"
echo "4. 🌐 Deploy backend to Railway/Render"
echo "5. 🔧 Update frontend/.env.production with backend URL"
echo "6. 📄 Enable GitHub Pages in repository settings"
echo
echo "🎯 Repository URL: https://github.com/hchandramouli-iyer/codecraft-ai"
echo "🌐 Live Demo URL: https://hchandramouli-iyer.github.io/codecraft-ai"
echo
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"

# Optional: Create a quick deployment summary
cat > DEPLOYMENT_SUMMARY.md << EOF
# CodeCraft AI Deployment Summary

## 📊 Deployment Status
- ✅ Frontend configured for GitHub Pages
- ✅ Backend configured for Railway deployment  
- ✅ GitHub Actions workflow created
- ✅ Production environment files created

## 🔗 Repository Information
- **GitHub Username**: hchandramouli-iyer
- **Repository Name**: codecraft-ai
- **Repository URL**: https://github.com/hchandramouli-iyer/codecraft-ai
- **Live Demo URL**: https://hchandramouli-iyer.github.io/codecraft-ai

## 🚀 Deployment Commands
\`\`\`bash
# Deploy frontend to GitHub Pages
cd frontend && npm run deploy

# Or using yarn
cd frontend && yarn deploy
\`\`\`

## 🔧 Environment Variables Needed
### Backend (Railway)
- MONGO_URL=mongodb+srv://...
- EMERGENT_LLM_KEY=your_key_here
- DB_NAME=codecraft_ai

### Frontend (Update .env.production)
- REACT_APP_BACKEND_URL=https://your-backend-url.railway.app

## 📋 TODO
- [ ] Create GitHub repository
- [ ] Set up MongoDB Atlas
- [ ] Deploy backend to Railway
- [ ] Update backend URL in frontend
- [ ] Deploy frontend to GitHub Pages
- [ ] Test live demo functionality
EOF

print_success "Deployment summary created: DEPLOYMENT_SUMMARY.md"