# CodeCraft AI - Complete Deployment Guide

## 🚀 Live Demo Deployment Strategy

This guide will help you deploy a fully functional CodeCraft AI platform with:
- **Frontend**: React app on GitHub Pages (`DataWhiz.github.io`)
- **Backend**: FastAPI on Railway/Render (free hosting)  
- **Database**: MongoDB Atlas (free tier)
- **LLM Integration**: Emergent LLM key for AI features

## 📋 Pre-Deployment Checklist

### **1. GitHub Repository Setup**
```bash
# Create repository exactly named:
Repository name: codecraft-ai (under hchandramouli-iyer)
Description: CodeCraft AI - AI-Powered Database Development Platform
Public repository (required for GitHub Pages)
```

### **2. Required Accounts**
- ✅ **GitHub Account** (for Pages hosting)
- ✅ **Railway Account** (for backend hosting) - Sign up with GitHub
- ✅ **MongoDB Atlas Account** (for database) - Free tier available
- ✅ **Emergent LLM Key** (for AI features) - Available in your current environment

## 🎯 Step-by-Step Deployment Process

### **Phase 1: Repository Setup & Code Preparation**

#### **1.1 Create GitHub Repository**
```bash
1. Go to GitHub.com
2. Click "New Repository"
3. Repository name: codecraft-ai (under hchandramouli-iyer)
4. Description: "CodeCraft AI - AI-Powered Database Development Platform"
5. Public repository
6. Initialize with README
7. Create Repository
```

#### **1.2 Prepare Frontend for Deployment**
The frontend needs modifications for production deployment:
- Update API base URL configuration
- Add GitHub Pages deployment configuration
- Create production build scripts
- Add deployment workflows

#### **1.3 Prepare Backend for Railway Deployment**
The backend needs Railway-specific configuration:
- Add Railway deployment configuration
- Environment variable setup
- Health check endpoints
- Production optimizations

### **Phase 2: Database Setup (MongoDB Atlas)**

#### **2.1 Create MongoDB Atlas Account**
```bash
1. Go to mongodb.com/atlas
2. Sign up for free account
3. Create new cluster (M0 Sandbox - FREE)
4. Choose cloud provider and region
5. Create cluster (takes 1-3 minutes)
```

#### **2.2 Configure Database Access**
```bash
1. Database Access → Add New Database User
   - Username: codecraft_user
   - Password: Generate secure password
   - Database User Privileges: Read and write to any database

2. Network Access → Add IP Address
   - Add Current IP Address
   - Allow Access from Anywhere (0.0.0.0/0) for development
   
3. Connect → Connect your application
   - Copy connection string
   - Format: mongodb+srv://codecraft_user:<password>@cluster0.xxxxx.mongodb.net/
```

### **Phase 3: Backend Deployment (Railway)**

#### **3.1 Setup Railway Account**
```bash
1. Go to railway.app
2. Sign up with GitHub account
3. Connect GitHub repository (backend code)
4. Deploy from GitHub
```

#### **3.2 Configure Environment Variables**
```bash
# In Railway dashboard → Variables
MONGO_URL=mongodb+srv://codecraft_user:<password>@cluster0.xxxxx.mongodb.net/codecraft_ai
EMERGENT_LLM_KEY=your_emergent_llm_key_here
DB_NAME=codecraft_ai
PORT=8001
```

#### **3.3 Deploy Backend**
```bash
# Railway will automatically:
1. Detect Python/FastAPI application
2. Install dependencies from requirements.txt
3. Start the application on assigned port
4. Provide public URL (e.g., https://codecraft-ai-production.up.railway.app)
```

### **Phase 4: Frontend Deployment (GitHub Pages)**

#### **4.1 Configure Frontend Environment**
```bash
# Update frontend/.env for production
REACT_APP_BACKEND_URL=https://your-railway-app.up.railway.app
```

#### **4.2 Build and Deploy**
```bash
# Build production version
cd /app/frontend
npm run build

# Deploy to GitHub Pages
npm run deploy
```

### **Phase 5: GitHub Actions Automation**

Automated deployment workflow for continuous integration. **Note**: The project uses Yarn, so the workflow is configured accordingly:

```yaml
# .github/workflows/deploy.yml
name: Deploy CodeCraft AI to GitHub Pages
on:
  push:
    branches: [ main, master ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'yarn'
          cache-dependency-path: frontend/yarn.lock
      - name: Install and Build
        run: |
          cd frontend
          yarn install --frozen-lockfile
          yarn build
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './frontend/build'
  deploy:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

**Troubleshooting**: If you encounter cache dependency errors, use the backup workflow in `.github/workflows/deploy-no-cache.yml`

## 🔧 Configuration Files

### **Frontend Package.json Updates**
```json
{
  "homepage": "https://hchandramouli-iyer.github.io/codecraft-ai",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  },
  "devDependencies": {
    "gh-pages": "^5.0.0"
  }
}
```

### **Backend Railway Configuration**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## 🎯 Environment Variables Reference

### **Production Environment Variables**

#### **Frontend (.env.production)**
```bash
REACT_APP_BACKEND_URL=https://your-railway-app.up.railway.app
REACT_APP_ENVIRONMENT=production
```

#### **Backend (Railway Environment)**
```bash
MONGO_URL=mongodb+srv://codecraft_user:<password>@cluster0.xxxxx.mongodb.net/codecraft_ai
EMERGENT_LLM_KEY=your_emergent_llm_key_here
DB_NAME=codecraft_ai
PORT=8001
ENVIRONMENT=production
```

## 🚀 Deployment Verification

### **1. Backend Health Check**
```bash
# Test backend deployment
curl https://your-railway-app.up.railway.app/api/
# Expected: {"message": "CodeCraft AI API is running"}
```

### **2. Frontend Verification**
```bash
# Visit deployed site
https://hchandramouli-iyer.github.io/codecraft-ai
# Should load CodeCraft AI interface
```

### **3. Full Integration Test**
```bash
# Test SQL conversion feature
# Test ER diagram generation
# Test AI tools functionality
# Verify all features working end-to-end
```

## 🎉 Expected Results

After successful deployment:

1. **Live Demo URL**: https://hchandramouli-iyer.github.io/codecraft-ai
2. **Full Functionality**: All CodeCraft AI features operational
3. **Professional Presentation**: Production-ready interface
4. **Scalable Infrastructure**: Can handle multiple users
5. **Automated Updates**: Push to GitHub → automatic deployment

## 📊 Cost Breakdown

- **GitHub Pages**: FREE
- **Railway Backend**: FREE tier (500 hours/month)
- **MongoDB Atlas**: FREE tier (512MB storage)
- **Domain**: FREE (.github.io subdomain)
- **Total Monthly Cost**: $0 (FREE)

## 🔒 Security Considerations

- Environment variables properly configured
- API keys secured in hosting platform
- Database access properly restricted
- HTTPS encryption enabled by default
- CORS properly configured for production

## 📈 Performance Optimization

- React build optimized for production
- Static assets served via GitHub Pages CDN
- Database queries optimized
- API response caching where appropriate
- Monitoring and logging enabled

This deployment strategy provides a professional, fully functional demo of CodeCraft AI that showcases all the platform's capabilities while maintaining zero hosting costs.

## 🚀 Next Steps

1. **Follow Phase 1-5** in sequence
2. **Test each component** before proceeding
3. **Verify full integration** after deployment
4. **Update documentation** with live URLs
5. **Share live demo** with stakeholders

The result will be a production-ready CodeCraft AI platform accessible to anyone worldwide via https://hchandramouli-iyer.github.io/codecraft-ai!