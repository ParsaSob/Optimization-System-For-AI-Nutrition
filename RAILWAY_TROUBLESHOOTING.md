# 🚨 Railway Troubleshooting Guide

## 🔍 **Current Issue:**
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

## 🛠️ **Solutions Applied:**

### **Solution 1: Remove Port from Procfile**
- ❌ `web: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1`
- ✅ `web: python start.py`

### **Solution 2: Use Startup Script**
- Created `start.py` that handles port configuration
- Script reads `PORT` from environment variables
- Fallback to port 8000 if not set

### **Solution 3: Environment Variable Handling**
- `main.py` now properly reads `PORT` from environment
- Better logging for debugging
- Fallback port configuration

## 🚀 **Deploy Steps:**

### **1. Push Changes:**
```bash
git add .
git commit -m "Fix Railway PORT issue - use startup script"
git push
```

### **2. In Railway Dashboard:**
1. Go to your project
2. Click "Deploy" or "Redeploy"
3. Wait for deployment to complete
4. Check logs for any errors

### **3. Test Endpoints:**
```bash
# Test root endpoint
curl https://web-production-c541.up.railway.app/

# Test health endpoint  
curl https://web-production-c541.up.railway.app/health
```

## 🔍 **Expected Results:**

### **Startup Logs:**
```
🚀 Starting Meal Optimization API on 0.0.0.0:8000
🔧 Railway PORT: 8000
```

### **Root Endpoint Response:**
```json
{
  "message": "Meal Optimization API is running",
  "status": "healthy",
  "port": 8000,
  "host": "0.0.0.0",
  "components_ready": true,
  "railway_info": {
    "port": 8000,
    "port_env": "8000",
    "python_version": "not_set"
  }
}
```

## 🚨 **If Still Getting 502:**

### **Check 1: Railway Logs**
- Go to Railway dashboard
- Click on your service
- Check "Deployments" tab
- Look for error messages

### **Check 2: Port Configuration**
- Verify `start.py` is being used
- Check if `PORT` environment variable is set
- Look for port binding errors

### **Check 3: Dependencies**
- Ensure all packages in requirements.txt are available
- Check Python version compatibility

## 📝 **Success Indicators:**
- ✅ No more "$PORT" errors
- ✅ Application starts successfully
- ✅ Root endpoint returns 200
- ✅ Health endpoint shows components ready

## 🆘 **Emergency Fallback:**
If this still doesn't work:
1. Use Docker deployment
2. Check Railway support
3. Verify project configuration
4. Try different port configurations

## 🔧 **Alternative Procfile Options:**

### **Option 1: Direct uvicorn (no port)**
```
web: uvicorn main:app --host 0.0.0.0 --workers 1
```

### **Option 2: Python startup script**
```
web: python start.py
```

### **Option 3: Simple Python command**
```
web: python -m uvicorn main:app --host 0.0.0.0 --workers 1
```
