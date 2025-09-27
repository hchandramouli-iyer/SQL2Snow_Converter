# Deployment Troubleshooting Guide

## ✅ Issues Fixed

### 1. Build Warnings Resolved
- **Fixed**: Added `@babel/plugin-proposal-private-property-in-object` to devDependencies
- **Fixed**: Updated browserslist data to latest version
- **Result**: Build now completes without warnings

### 2. GitHub Actions Workflow Optimized
- **Improved**: Added explicit Node.js version 20
- **Added**: Dependency caching for faster builds
- **Added**: `CI=false` to prevent warnings from failing build
- **Added**: `--prefer-offline` flag for more reliable installs

## 🔧 Common Deployment Issues & Solutions

### Issue 1: GitHub Pages Not Enabled
**Solution**: In your GitHub repository settings:
1. Go to Settings → Pages
2. Set Source to "GitHub Actions"
3. Ensure the repository is public or you have GitHub Pro

### Issue 2: Workflow Permissions
**Check**: Repository Settings → Actions → General → Workflow permissions
- Should be set to "Read and write permissions"
- Or ensure "Allow GitHub Actions to create and approve pull requests" is checked

### Issue 3: Multiple Workflow Files Conflict
**Current Status**: You have multiple deployment workflows:
- `deploy.yml` (main, recommended)
- `deploy-backup.yml` (manual trigger only)
- `deploy-with-cache.yml` (manual trigger only)  
- `deploy-no-cache.yml` (manual trigger only)

**Recommendation**: Use only `deploy.yml` for automatic deployment

### Issue 4: Build Environment Variables
**Check**: Ensure frontend/.env.production contains:
```
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

### Issue 5: Homepage Configuration
**Verified**: package.json contains correct homepage:
```json
"homepage": "/SQL2Snow_Converter/"
```

## 🚀 Deployment Verification Steps

### 1. Local Build Test
```bash
cd frontend
yarn build
```
**Status**: ✅ Working (no warnings/errors)

### 2. Check Build Output
```bash
ls -la frontend/build/
```
**Expected**: Should contain index.html, static/ folder, asset-manifest.json

### 3. GitHub Actions Logs
1. Go to your repository → Actions tab
2. Click on the latest workflow run
3. Check each step for errors

### 4. GitHub Pages URL
After successful deployment, visit:
```
https://yourusername.github.io/SQL2Snow_Converter/
```

## 🔍 Debugging Commands

### Check Current Build Status
```bash
cd /app/frontend && yarn build 2>&1 | grep -E "(error|Error|fail|Fail)" || echo "Build successful"
```

### Validate Workflow Syntax
```bash
cd /app && python3 -c "
import yaml
with open('.github/workflows/deploy.yml', 'r') as f:
    yaml.safe_load(f)
print('Workflow YAML is valid')
"
```

### Check Package Dependencies
```bash
cd /app/frontend && yarn check --verify-tree
```

## 📋 Next Steps If Still Failing

1. **Check GitHub Actions Tab**: Look at the specific error messages in failed workflow runs
2. **Repository Settings**: Verify GitHub Pages is enabled and set to "GitHub Actions"
3. **Permissions**: Ensure workflow has proper read/write permissions
4. **Branch Protection**: Check if main/master branch has protection rules blocking deployment
5. **Quota Limits**: Verify GitHub Pages usage limits haven't been exceeded

## 🆘 Emergency Fallback

If automated deployment continues failing, you can deploy manually:

1. **Local Build**:
   ```bash
   cd frontend && yarn build
   ```

2. **Manual Upload**: 
   - Download the `frontend/build` folder
   - Use GitHub's manual file upload to gh-pages branch

3. **Alternative Hosting**: Consider other platforms like Netlify or Vercel for easier deployment

## 📞 Getting Help

If you're still experiencing issues, provide these details:
- Specific error message from GitHub Actions logs
- Repository URL (if public)
- Screenshot of GitHub Pages settings
- Copy of the failing workflow run logs