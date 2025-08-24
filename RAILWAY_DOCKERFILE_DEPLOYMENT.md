# 🚀 Railway Dockerfile Deployment Guide

## 🔍 **مشکل حل شده:**
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
PORT environment variable not expanding in Dockerfile CMD
```

## 🛠️ **راه‌حل صحیح: Shell Script + PORT Expansion**

### **کلید حل مشکل:**
Dockerfile نمی‌تونه $PORT رو expand کنه. Shell script این کار رو انجام می‌ده.

## 📁 **فایل‌های کلیدی:**

### **1. start.sh (Shell Script):**
```bash
#!/bin/bash

# Get port from environment variable or default to 8000
PORT=${PORT:-8000}

echo "🚀 Starting Meal Optimization API on port $PORT"

# Start uvicorn with the resolved port
exec uvicorn main:app --host 0.0.0.0 --port $PORT
```

**توضیح:**
- **`PORT=${PORT:-8000}`**: Shell expansion برای PORT
- **`exec uvicorn`**: Start uvicorn با port resolved شده
- **Proper Expansion**: Shell script $PORT رو درست expand می‌کنه

### **2. Dockerfile (Using start.sh):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Make start.sh executable
RUN chmod +x start.sh

# Expose port (will be set by Railway)
EXPOSE $PORT

# Use start.sh script to handle PORT expansion
CMD ["./start.sh"]
```

**توضیح:**
- **`RUN chmod +x start.sh`**: Make script executable
- **`CMD ["./start.sh"]`**: Use shell script for PORT expansion
- **Shell Expansion**: Shell script $PORT رو درست handle می‌کنه

### **3. main.py:**
- Railway-friendly logging
- Better error handling
- Dynamic port approach
- Railway PORT environment variable

## 🚀 **مراحل Deploy:**

### **1. Push تغییرات:**
```bash
git add .
git commit -m "Use shell script for proper PORT expansion in Dockerfile"
git push
```

### **2. در Railway Dashboard:**
1. **Redeploy** کن (automatic after push)
2. **Logs** رو چک کن
3. **No need to change start command** (Dockerfile handles it)

### **3. تست:**
```bash
# Test root endpoint
curl https://web-production-c541.up.railway.app/

# Test health endpoint
curl https://web-production-c541.up.railway.app/health
```

## 🔍 **Expected Results:**

### **Build Logs:**
```
Building Docker image...
Installing dependencies...
Making start.sh executable...
Starting service...
```

### **Startup Logs:**
```
🚀 Starting Meal Optimization API on port 8080
INFO: Uvicorn running on http://0.0.0.0:8080
```

### **Root Endpoint:**
```json
{
  "message": "Meal Optimization API is running",
  "status": "healthy",
  "components_ready": true,
  "railway_info": {
    "port_env": "8080",
    "python_version": "not_set",
    "message": "Railway deployment - using port 8080"
  }
}
```

## 🔧 **چرا این راه‌حل کار می‌کنه:**

1. **Shell Script**: $PORT رو درست expand می‌کنه
2. **Dockerfile CMD**: از shell script استفاده می‌کنه
3. **Proper Expansion**: Shell script environment variables رو handle می‌کنه
4. **Host Binding**: Bind به همه interfaces
5. **Dynamic Configuration**: Railway خودش port رو handle می‌کنه

## 🚨 **اگر هنوز مشکل داشت:**

### **Check 1: Railway Logs**
- Go to Railway dashboard
- Click on your service
- Check "Deployments" tab
- Look for "Starting Meal Optimization API on port XXXX" message

### **Check 2: Shell Script**
- Ensure start.sh is executable: `chmod +x start.sh`
- Check for typos in start.sh
- Verify shell script syntax

### **Check 3: Environment Variables**
- Check Railway dashboard for PORT environment variable
- Verify PORT is set (should be something like 8080)

## 📝 **Success Indicators:**
- ✅ Docker build successful
- ✅ Shell script executes properly
- ✅ PORT environment variable expands correctly
- ✅ Uvicorn starts on correct port
- ✅ Application responds to requests
- ✅ Root endpoint returns 200

## 🔧 **Alternative Approaches:**

### **Option 1: Shell Script (current)**
```dockerfile
CMD ["./start.sh"]
```

### **Option 2: Direct Shell Command**
```dockerfile
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

## 🎯 **نکات مهم:**
1. **Shell Script**: $PORT رو درست expand می‌کنه
2. **Dockerfile CMD**: از shell script استفاده می‌کنه
3. **Proper Expansion**: Shell script environment variables رو handle می‌کنه
4. **Host Binding**: Bind به همه interfaces
5. **Dynamic Configuration**: Railway خودش port رو handle می‌کنه

## 🔍 **مزایای این روش:**

- **قابل اعتماد**: Shell script $PORT رو درست expand می‌کنه
- **Proper Expansion**: Environment variables درست handle می‌شن
- **Dynamic Port**: Railway خودش port رو handle می‌کنه
- **Host Binding**: Bind به همه interfaces
- **Simple**: ساده و قابل فهم

## 🚀 **مراحل بعدی:**

1. **Push تغییرات** (start.sh + Dockerfile + main.py)
2. **Railway auto-redeploys** از Dockerfile
3. **Check Railway Logs** برای "Starting Meal Optimization API on port XXXX"
4. **Test endpoints** برای functionality
5. **Monitor performance** برای stability

**حالا تغییرات رو push کن و Railway خودش از Dockerfile استفاده می‌کنه. Shell script $PORT رو درست expand می‌کنه!** 🚀
