# GitHub Actions Deployment Troubleshooting Guide

## 🔧 Common Issues & Solutions

### **Issue 1: Cache Dependencies Error**
```
Error: Some specified paths were not resolved, unable to cache dependencies.
```

**Cause**: The workflow is looking for `package-lock.json` but the project uses Yarn (`yarn.lock`)

**Solution**: Update the workflow to use Yarn caching:

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'yarn'                           # Changed from 'npm'
    cache-dependency-path: frontend/yarn.lock  # Changed from package-lock.json

- name: Install dependencies
  run: |
    cd frontend
    yarn install --frozen-lockfile         # Changed from npm ci
```

### **Issue 2: Build Failures**
```
Error: Cannot find module 'react-scripts'
```

**Solution**: Ensure all dependencies are installed correctly:

```yaml
- name: Install dependencies
  run: |
    cd frontend
    yarn install --frozen-lockfile
    # Alternative: yarn install --production=false
```

### **Issue 3: GitHub Pages Not Updating**
**Cause**: Pages may be deploying from wrong branch or folder

**Solution**: Check repository settings:
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: gh-pages
4. Folder: / (root)

### **Issue 4: Environment Variables Not Found**
**Cause**: Production environment variables not properly configured

**Solution**: Ensure `.env.production` exists in frontend folder:
```bash
# frontend/.env.production
REACT_APP_BACKEND_URL=https://your-backend-url.railway.app
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
```

### **Issue 5: Permission Denied Errors**
**Cause**: GitHub Actions doesn't have proper permissions

**Solution**: Ensure workflow has correct permissions:
```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

## 🛠️ **Alternative Workflows**

### **Option 1: Simplified Workflow (No Caching)**
Use `/app/.github/workflows/deploy-no-cache.yml` if caching issues persist.

### **Option 2: Manual Deployment**
```bash
# Build locally and deploy
cd frontend
yarn install
yarn build
yarn deploy
```

### **Option 3: Different Deployment Action**
```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./frontend/build
```

## 📋 **Debugging Steps**

### **Step 1: Check Workflow Logs**
1. Go to repository Actions tab
2. Click on failed workflow run
3. Expand failed step to see detailed error

### **Step 2: Verify File Structure**
Ensure these files exist:
```
├── .github/
│   └── workflows/
│       └── deploy.yml
├── frontend/
│   ├── package.json
│   ├── yarn.lock          # Should exist for Yarn projects
│   └── .env.production     # Required for production build
└── README.md
```

### **Step 3: Test Build Locally**
```bash
# Test the build process locally
cd frontend
yarn install
yarn build

# Should create frontend/build/ directory
ls -la build/
```

### **Step 4: Check GitHub Pages Settings**
1. Repository Settings → Pages
2. Source should be "Deploy from a branch"
3. Branch should be "gh-pages" 
4. Folder should be "/ (root)"

## 🔄 **Workflow File Selection**

### **Use Primary Workflow** (`deploy.yml`)
- When yarn.lock exists in frontend directory
- For optimal performance with caching
- Most projects should use this

### **Use Backup Workflow** (`deploy-no-cache.yml`)  
- If caching issues persist
- For quick deployment without optimization
- When troubleshooting cache-related problems

### **Manual Deployment Script**
```bash
#!/bin/bash
# manual-deploy.sh

echo "🚀 Manual GitHub Pages Deployment"

# Build the project
cd frontend
echo "📦 Installing dependencies..."
yarn install

echo "🔨 Building application..."
yarn build

echo "🌐 Deploying to GitHub Pages..."
yarn deploy

echo "✅ Deployment complete!"
echo "🌍 Site will be available at: https://hchandramouli-iyer.github.io/codecraft-ai"
```

## 📊 **Monitoring Deployment**

### **Check Deployment Status**
```bash
# GitHub Pages deployment URL
https://github.com/hchandramouli-iyer/codecraft-ai/deployments

# Live site URL  
https://hchandramouli-iyer.github.io/codecraft-ai
```

### **Common Success Indicators**
- ✅ Workflow runs without errors
- ✅ gh-pages branch is created/updated
- ✅ Site loads at expected URL
- ✅ All features work correctly

### **Performance Monitoring**
- Check GitHub Actions usage in repository Insights
- Monitor site performance with browser dev tools
- Verify all assets load correctly

## 🆘 **Emergency Fixes**

### **If Workflow Completely Fails**
```bash
# Option 1: Manual deployment
cd frontend && yarn deploy

# Option 2: Delete and recreate workflow
rm .github/workflows/deploy.yml
# Copy from deploy-no-cache.yml and rename

# Option 3: Reset to working state
git checkout HEAD~1 .github/workflows/deploy.yml
```

### **If Site Doesn't Load**
```bash
# Check build output
cd frontend && yarn build
ls -la build/

# Verify environment variables
cat .env.production

# Test locally
yarn start
```

## 🎯 **Best Practices**

1. **Always test builds locally** before pushing
2. **Use specific action versions** (e.g., @v4 instead of @latest)  
3. **Keep workflows simple** - avoid complex conditional logic
4. **Monitor action usage** to stay within GitHub limits
5. **Use secrets for sensitive data** (API keys, tokens)

## 📞 **Getting Help**

If issues persist:
1. Check [GitHub Actions Documentation](https://docs.github.com/en/actions)
2. Review [GitHub Pages Documentation](https://docs.github.com/en/pages)  
3. Search GitHub Community discussions
4. Review workflow logs for specific error messages

**Most common solution**: Use the no-cache workflow version for immediate deployment, then optimize later.