# 🚀 Railway Deployment Guide for Meal Optimization API

## 📋 **Prerequisites:**
- Railway account
- Git repository with your code
- Python 3.11.9

## 🔧 **Deployment Steps:**

### **1. Connect to Railway:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link your project
railway link
```

### **2. Deploy:**
```bash
# Deploy to Railway
railway up
```

### **3. Set Environment Variables:**
In Railway Dashboard:
- `PYTHON_VERSION`: `3.11.9`
- `PORT`: `8000` (Railway sets this automatically)

## 🚨 **Troubleshooting 502 Bad Gateway:**

### **Check 1: Railway Logs**
```bash
# View deployment logs
railway logs

# View real-time logs
railway logs --follow
```

### **Check 2: Application Health**
```bash
# Test root endpoint
curl https://your-app.up.railway.app/

# Test health endpoint
curl https://your-app.up.railway.app/health
```

### **Check 3: Common Issues**

#### **Issue: Dependencies not installed**
**Solution:** Use `railway-startup.py` script

#### **Issue: Port binding problems**
**Solution:** Ensure using `$PORT` environment variable

#### **Issue: Python version mismatch**
**Solution:** Set `PYTHON_VERSION=3.11.9`

#### **Issue: Application crashes on startup**
**Solution:** Check database initialization errors

## 📁 **File Structure for Railway:**
```
├── main.py                    # FastAPI application
├── railway-startup.py         # Railway startup script
├── Procfile                   # Railway process file
├── requirements.txt           # Python dependencies
├── railway.json              # Railway configuration
├── runtime.txt               # Python version
└── .dockerignore             # Docker ignore file
```

## 🔍 **Debugging Commands:**

### **Local Testing:**
```bash
# Test with Railway environment
PORT=8000 python railway-startup.py

# Test individual components
python -c "import main; print('Main module OK')"
python -c "import optimization_engine; print('Engine OK')"
python -c "import database; print('Database OK')"
```

### **Railway Testing:**
```bash
# Test API endpoints
curl -X POST https://your-app.up.railway.app/optimize-rag-meal \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 📊 **Monitoring:**

### **Health Check Endpoints:**
- `/` - Root endpoint with component status
- `/health` - Detailed health information
- `/ingredients` - Test database connection

### **Expected Responses:**
```json
// Root endpoint
{
  "message": "Meal Optimization API is running",
  "status": "healthy",
  "port": 8000,
  "host": "0.0.0.0",
  "components_ready": true
}

// Health endpoint
{
  "status": "healthy",
  "message": "Meal Optimization API is running",
  "database_ready": true,
  "engine_ready": true
}
```

## 🚀 **Quick Fix Commands:**

### **If 502 persists:**
```bash
# 1. Check logs
railway logs

# 2. Redeploy
railway up

# 3. Restart service
railway service restart

# 4. Check environment
railway variables
```

### **Force Python version:**
```bash
# Add to railway.json
{
  "environments": {
    "production": {
      "variables": {
        "PYTHON_VERSION": "3.11.9"
      }
    }
  }
}
```

## 📝 **Success Indicators:**
- ✅ Root endpoint returns 200
- ✅ Health endpoint shows components ready
- ✅ Ingredients endpoint returns data
- ✅ RAG optimization endpoint accepts requests
- ✅ No 502 errors in logs

## 🆘 **Emergency Fallback:**
If Railway continues to fail:
1. Use Docker deployment
2. Check Python compatibility
3. Verify dependency versions
4. Review startup logs
