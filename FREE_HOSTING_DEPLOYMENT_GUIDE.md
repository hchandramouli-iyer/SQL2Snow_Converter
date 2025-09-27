# Free Hosting Deployment Guide for CodeCraft AI

## 🌟 Recommended Free Hosting Stack

### **Option 1: Premium Free Stack (Recommended)**
- **Frontend**: Vercel (Free custom domain + excellent performance)
- **Backend**: Railway ($5/month free credit - best for FastAPI) 
- **Database**: MongoDB Atlas (512MB free)
- **Domain**: Free subdomain (yourapp.vercel.app) or custom domain

### **Option 2: Fully Free Stack**
- **Frontend**: Netlify (Free hosting + subdomain)
- **Backend**: Render (Free with limitations)
- **Database**: MongoDB Atlas (512MB free)
- **Domain**: Free subdomain (yourapp.netlify.app)

## 🚀 Step-by-Step Deployment Instructions

### Step 1: Database Setup (MongoDB Atlas)
1. **Create Account**: Visit [mongodb.com](https://mongodb.com) and sign up
2. **Create Free Cluster**: Select M0 (512MB) free tier
3. **Security Setup**:
   - Create database user with read/write permissions
   - Add network access (0.0.0.0/0 for development)
4. **Get Connection String**: Copy the connection URI for later use

### Step 2: Backend Deployment (Railway)
1. **Create Railway Account**: Visit [railway.app](https://railway.app) and sign up with GitHub
2. **Deploy Backend**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Deploy from backend directory
   cd backend
   railway deploy
   ```
3. **Set Environment Variables**:
   - `MONGODB_URI`: Your Atlas connection string
   - `SECRET_KEY`: Generate secure key
   - `DATABASE_NAME`: Your database name
   - `ALLOWED_ORIGINS`: ["https://yourapp.vercel.app"]

4. **Custom Domain** (Optional):
   - Add custom domain in Railway dashboard (e.g., api.yourapp.com)
   - Update DNS records as instructed

### Step 3: Frontend Deployment (Vercel)
1. **Create Vercel Account**: Visit [vercel.com](https://vercel.com) and sign up with GitHub
2. **Deploy Frontend**:
   - Import your GitHub repository
   - Select the frontend folder as root directory
   - Set build command: `npm run build`
   - Set output directory: `build`

3. **Environment Variables**:
   - `REACT_APP_API_URL`: Your Railway backend URL
   - `REACT_APP_ENVIRONMENT`: production

4. **Custom Domain** (Optional):
   - Add domain in Vercel dashboard
   - Update DNS records as instructed
   - Vercel provides free SSL certificates

### Step 4: CI/CD Setup (GitHub Actions)
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Free Hosting

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway login --token ${{ secrets.RAILWAY_TOKEN }}
          cd backend && railway deploy
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: |
          npm install -g vercel
          cd frontend
          vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```

## 🎯 Alternative Free Options

### **Netlify + Render Stack**
- **Frontend**: Netlify (Free hosting + forms + functions)
- **Backend**: Render (Free tier with 750 hours/month)
- **Pros**: Completely free, good performance
- **Cons**: Render free tier has cold starts (services sleep)

### **GitHub Pages + Railway**
- **Frontend**: GitHub Pages (Free but limited)
- **Backend**: Railway ($5 free credits)
- **Pros**: Simple setup, good for static sites
- **Cons**: GitHub Pages has limitations for React apps

### **Firebase Hosting**
- **Full Stack**: Firebase (Generous free tier)
- **Includes**: Hosting, Database, Authentication
- **Pros**: Google infrastructure, real-time database
- **Cons**: Learning curve for Firebase-specific patterns

## 💰 Cost Breakdown

### Free Tier Limits:
- **MongoDB Atlas**: 512MB storage, shared resources
- **Railway**: $5 monthly credits (usually enough for small apps)
- **Vercel**: 100GB bandwidth, unlimited personal projects
- **Netlify**: 100GB bandwidth, 300 build minutes
- **Render**: 750 hours/month (enough for one always-on service)

### Estimated Monthly Costs:
- **Option 1 (Vercel + Railway)**: $0-5/month 
- **Option 2 (Netlify + Render)**: $0/month
- **Custom Domain**: $10-15/year (optional)

## 🔧 Quick Deploy Commands

### Railway Backend Deploy:
```bash
# One-time setup
npm install -g @railway/cli
railway login
cd backend
railway init
railway add

# Deploy
railway deploy

# Set environment variables
railway variables set MONGODB_URI="your-connection-string"
railway variables set SECRET_KEY="your-secret-key"
```

### Vercel Frontend Deploy:
```bash
# One-time setup
npm install -g vercel
cd frontend
vercel login

# Deploy
vercel --prod

# Set environment variables
vercel env add REACT_APP_API_URL production
```

## 📋 Domain Options

### **Free Subdomains**:
- `yourapp.vercel.app` (Vercel)
- `yourapp.netlify.app` (Netlify)  
- `yourapp.onrender.com` (Render)
- `yourname.github.io/reponame` (GitHub Pages)

### **Free Domain Providers**:
- **Freenom**: .tk, .ml, .ga, .cf domains (free for 1 year)
- **GitHub Student Pack**: Free .me domain for students
- **Cloudflare**: Domain registration at cost

### **Custom Domain Setup**:
1. Register domain with provider
2. Update DNS records:
   - Frontend: Point to hosting provider
   - Backend: Point to Railway/Render
3. Enable SSL (automatic with Vercel/Netlify)

## 🎛️ Environment Configuration

### Backend (.env):
```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
SECRET_KEY=your-secure-secret-key
DATABASE_NAME=production
ALLOWED_ORIGINS=["https://yourapp.vercel.app"]
```

### Frontend (.env):
```env
REACT_APP_API_URL=https://yourapp.railway.app
REACT_APP_ENVIRONMENT=production
```

## ✅ Deployment Checklist

### Pre-Deployment:
- [ ] MongoDB Atlas cluster created and configured
- [ ] Environment variables documented
- [ ] GitHub repository organized (frontend/backend folders)
- [ ] Build scripts tested locally

### Backend Deployment:
- [ ] Railway account created and linked to GitHub
- [ ] Backend deployed successfully
- [ ] Environment variables configured
- [ ] Health check endpoint working
- [ ] CORS configured for frontend domain

### Frontend Deployment:
- [ ] Vercel account created and linked to GitHub
- [ ] Frontend deployed successfully  
- [ ] Environment variables configured
- [ ] API calls working to backend
- [ ] Build optimization completed

### Post-Deployment:
- [ ] End-to-end testing completed
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificates working
- [ ] CI/CD pipeline tested
- [ ] Monitoring and logging set up

## 🆘 Troubleshooting

### Common Issues:
1. **CORS Errors**: Update ALLOWED_ORIGINS in backend
2. **API Connection Failed**: Check REACT_APP_API_URL
3. **Database Connection**: Verify MongoDB Atlas IP whitelist
4. **Build Failures**: Check node version compatibility
5. **Environment Variables**: Verify all required vars are set

### Debug Commands:
```bash
# Check Railway logs
railway logs

# Check Vercel deployment
vercel logs

# Test API endpoints
curl https://yourapp.railway.app/health

# Test frontend build
cd frontend && npm run build
```

## 📞 Support Resources

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Vercel**: [vercel.com/docs](https://vercel.com/docs)
- **MongoDB Atlas**: [docs.mongodb.com](https://docs.mongodb.com)
- **GitHub Actions**: [docs.github.com/actions](https://docs.github.com/actions)

---

**Next Steps**: Choose your preferred hosting stack and follow the deployment instructions above. The Vercel + Railway combination is recommended for the best balance of performance, features, and cost.