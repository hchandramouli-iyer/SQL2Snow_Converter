# GitHub Pages Setup Fix

## 🚨 **Error Analysis**
```
Error: Get Pages site failed. Please verify that the repository has Pages enabled and configured to build using GitHub Actions
```

**Root Cause**: GitHub Pages is not enabled or not configured to use GitHub Actions for deployment.

## 🔧 **Step-by-Step Fix**

### **Step 1: Enable GitHub Pages**
1. Go to your repository: `https://github.com/hchandramouli-iyer/SQL2Snow_Converter`
2. Click **Settings** tab (at the top of the repository)
3. Scroll down to **Pages** section (left sidebar)
4. Under **Source**, select **"GitHub Actions"** (NOT "Deploy from a branch")

### **Step 2: Configure GitHub Actions Deployment**
In the Pages settings:
- **Source**: GitHub Actions ✅
- **Build and deployment**: GitHub Actions ✅
- **Do NOT select**: Deploy from a branch (this is the old method)

### **Step 3: Update Workflow File**
The current workflow should work, but let's add the `enablement` parameter as suggested:

```yaml
- name: Setup Pages
  uses: actions/configure-pages@v4
  with:
    enablement: true  # Add this line
```

## 🛠️ **Alternative: Simplified Workflow**

If the above doesn't work, use this simpler approach:

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          
      - name: Install and Build
        run: |
          cd frontend
          yarn install --frozen-lockfile
          yarn build
          
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend/build
```

## 📋 **Repository Naming Issue**

I notice your repository is named `SQL2Snow_Converter` but we configured it for `codecraft-ai`. You have two options:

### **Option A: Rename Repository**
1. Go to Settings → General
2. Scroll down to "Repository name"
3. Change from `SQL2Snow_Converter` to `codecraft-ai`
4. Update homepage in package.json accordingly

### **Option B: Update Configuration**
Update the homepage in `frontend/package.json`:
```json
{
  "homepage": "https://hchandramouli-iyer.github.io/SQL2Snow_Converter"
}
```

## 🎯 **Expected Pages URL**
After fixing:
- Current repo name: `https://hchandramouli-iyer.github.io/SQL2Snow_Converter`
- If renamed: `https://hchandramouli-iyer.github.io/codecraft-ai`