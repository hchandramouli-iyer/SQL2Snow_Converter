# CodeCraft AI - Live Demo Deployment

## 🎯 Quick Start Deployment Guide

Deploy your CodeCraft AI platform as a fully functional live demo accessible at:
**https://hchandramouli-iyer.github.io/codecraft-ai**

## 📋 Deployment Checklist

### ✅ **Pre-configured Files Created**
- [x] GitHub Actions workflow (`.github/workflows/deploy.yml`)
- [x] Package.json updated with homepage and deploy scripts
- [x] Production environment configuration (`.env.production`)  
- [x] Railway deployment configuration (`railway.json`)
- [x] Docker configuration for backend (`Dockerfile`)
- [x] Deployment automation script (`deploy.sh`)

### 🚀 **Step 1: Create GitHub Repository**
```bash
1. Go to: https://github.com/hchandramouli-iyer
2. Click "New Repository"
3. Repository name: codecraft-ai
4. Description: "CodeCraft AI - AI-Powered Database Development Platform"
5. Public repository (required for GitHub Pages)
6. Create Repository
```

### 📤 **Step 2: Push Code to GitHub**
```bash
# Clone your new repository
git clone https://github.com/hchandramouli-iyer/codecraft-ai.git
cd codecraft-ai

# Copy all CodeCraft AI files to this directory
# (Copy contents from /app/ to your local codecraft-ai folder)

# Add and commit files
git add .
git commit -m "Initial commit: CodeCraft AI platform"
git push origin main
```

### 🗄️ **Step 3: Set Up MongoDB Atlas (Free)**
```bash
1. Visit: https://www.mongodb.com/atlas
2. Sign up for free account
3. Create new cluster (M0 Sandbox - FREE)
4. Create database user: codecraft_user
5. Allow network access from anywhere (0.0.0.0/0)
6. Copy connection string:
   mongodb+srv://codecraft_user:<password>@cluster0.xxxxx.mongodb.net/
```

### 🚂 **Step 4: Deploy Backend to Railway (Free)**
```bash
1. Visit: https://railway.app
2. Sign up with GitHub account
3. Click "New Project" → "Deploy from GitHub repo"
4. Select: hchandramouli-iyer/codecraft-ai
5. Set environment variables:
   - MONGO_URL=mongodb+srv://codecraft_user:<password>@cluster0.xxxxx.mongodb.net/codecraft_ai
   - EMERGENT_LLM_KEY=your_emergent_llm_key_here
   - DB_NAME=codecraft_ai
   - PORT=8001
6. Deploy automatically starts
7. Copy the Railway app URL (e.g., https://codecraft-ai-production.up.railway.app)
```

### 🌐 **Step 5: Update Frontend Configuration**
```bash
# Update frontend/.env.production with your Railway backend URL
REACT_APP_BACKEND_URL=https://your-railway-app.up.railway.app
```

### 📄 **Step 6: Enable GitHub Pages**
```bash
1. Go to your GitHub repository settings
2. Navigate to Pages section
3. Source: Deploy from a branch
4. Branch: gh-pages
5. Folder: / (root)
6. Save
```

### 🚀 **Step 7: Deploy Frontend**
```bash
# Run the deployment script
./deploy.sh

# Or manually deploy
cd frontend
npm run deploy

# GitHub Pages will be available at:
# https://hchandramouli-iyer.github.io/codecraft-ai
```

## 🎉 **Expected Results**

After successful deployment:

### **✅ Live Demo Features**
- **SQL to Snowflake Conversion**: Convert from MySQL, PostgreSQL, SQL Server, Oracle
- **Interactive ER Diagrams**: Generate diagrams from CREATE TABLE statements
- **8 AI Development Tools**: Code generation, assistance, conversion, explanation, enhancement
- **Real-time Chat Assistant**: AI-powered coding help with session management
- **Professional UI**: Clean, responsive interface with modern design

### **🔗 Live URLs**
- **Frontend Demo**: https://hchandramouli-iyer.github.io/codecraft-ai
- **Backend API**: https://your-railway-app.up.railway.app/api/
- **GitHub Repository**: https://github.com/hchandramouli-iyer/codecraft-ai

### **💰 Cost Breakdown**
- **GitHub Pages**: FREE
- **Railway Backend**: FREE (500 hours/month)
- **MongoDB Atlas**: FREE (512MB storage)
- **Total**: $0/month

## 🔧 **Advanced Configuration**

### **Custom Domain (Optional)**
```bash
# Add CNAME file to frontend/public/
echo "your-custom-domain.com" > frontend/public/CNAME

# Then configure DNS:
# CNAME record: your-domain → hchandramouli-iyer.github.io
```

### **Environment Variables Reference**
```bash
# Production Backend Environment
MONGO_URL=mongodb+srv://codecraft_user:<password>@cluster0.xxxxx.mongodb.net/codecraft_ai
EMERGENT_LLM_KEY=your_emergent_llm_key_here
DB_NAME=codecraft_ai
PORT=8001
ENVIRONMENT=production

# Production Frontend Environment  
REACT_APP_BACKEND_URL=https://your-railway-app.up.railway.app
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
```

## 📊 **Testing Your Deployment**

### **1. Backend Health Check**
```bash
curl https://your-railway-app.up.railway.app/api/
# Expected: {"message": "CodeCraft AI API is running"}
```

### **2. Frontend Functionality Test**
```bash
# Visit: https://hchandramouli-iyer.github.io/codecraft-ai
# Test features:
- SQL Conversion with sample MySQL query
- ER Diagram generation with CREATE TABLE statements  
- AI Code Generator with simple request
- Chat Assistant with coding question
```

### **3. Full Integration Test**
```bash
# End-to-end workflow test:
1. Load the demo site
2. Test SQL conversion (MySQL → Snowflake)
3. Generate ER diagram from SQL
4. Use AI code generator
5. Verify all features working
```

## 🎯 **Success Metrics**

Your deployment is successful when:
- ✅ Frontend loads at https://hchandramouli-iyer.github.io/codecraft-ai
- ✅ All CodeCraft AI tools are functional
- ✅ Backend API responds correctly
- ✅ Database operations work (conversion history, ER diagrams)
- ✅ AI features work with Emergent LLM integration
- ✅ Professional, responsive interface across devices

## 🆘 **Troubleshooting**

### **Common Issues & Solutions**

**Frontend not loading:**
```bash
# Check GitHub Pages settings
# Ensure gh-pages branch exists
# Verify homepage URL in package.json
```

**Backend API errors:**
```bash
# Check Railway deployment logs
# Verify environment variables
# Test MongoDB connection
```

**AI features not working:**
```bash
# Verify EMERGENT_LLM_KEY is set correctly
# Check backend logs for API errors
# Test individual AI endpoints
```

## 🚀 **Next Steps After Deployment**

1. **Share Your Demo**: Send the live URL to stakeholders
2. **Monitor Usage**: Check Railway and GitHub Pages analytics  
3. **Iterate**: Add new features based on user feedback
4. **Scale**: Upgrade hosting plans if needed for higher traffic
5. **Custom Domain**: Add professional domain if desired

## 📞 **Support**

If you encounter issues:
1. Check the detailed DEPLOYMENT_GUIDE.md
2. Review TESTING_GUIDE.md for validation steps
3. Check GitHub Actions logs for deployment issues
4. Review Railway logs for backend problems

---

**🎉 Ready to launch your CodeCraft AI live demo!**

Repository: https://github.com/hchandramouli-iyer/codecraft-ai
Live Demo: https://hchandramouli-iyer.github.io/codecraft-ai