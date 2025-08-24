# 🚀 Railway Shell Script Fix

## 🔍 **مشکل حل شده:**
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

## 🛠️ **راه‌حل جدید: Shell Script + Environment Variable Handling**

### **کلید حل مشکل:**
Railway نمی‌تونه `$PORT` رو به درستی substitute کنه، پس ما با shell script handle می‌کنیم.

## 📁 **فایل‌های کلیدی:**

### **1. start.sh (Shell Script):**
```bash
#!/bin/bash

# Railway Startup Script
# Handles PORT environment variable and starts uvicorn properly

echo "🚀 Starting Meal Optimization API"
echo "🔧 Environment: PORT=$PORT"

# Set default port if not provided
if [ -z "$PORT" ]; then
    PORT=8000
    echo "⚠️ No PORT set, using default: $PORT"
fi

# Validate PORT is a number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "❌ Invalid PORT value: $PORT, using default 8000"
    PORT=8000
fi

echo "🌍 Using port: $PORT"

# Start uvicorn with proper port
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

### **2. Procfile:**
```
web: bash start.sh
```

### **3. main.py:**
- بدون host و port specification
- Railway-friendly logging
- Better error handling

## 🚀 **مراحل Deploy:**

### **1. Push تغییرات:**
```bash
git add .
git commit -m "Use shell script for Railway PORT handling"
git push
```

### **2. در Railway Dashboard:**
1. **Redeploy** کن
2. **Logs** رو چک کن
3. **Environment Variables** رو پاک کن (اختیاری)

### **3. تست:**
```bash
# Test root endpoint
curl https://web-production-c541.up.railway.app/

# Test health endpoint
curl https://web-production-c541.up.railway.app/health
```

## 🔍 **Expected Results:**

### **Startup Logs:**
```
🚀 Starting Meal Optimization API
🔧 Environment: PORT=8000
🌍 Using port: 8000
```

### **Root Endpoint:**
```json
{
  "message": "Meal Optimization API is running",
  "status": "healthy",
  "components_ready": true,
  "railway_info": {
    "port_env": "8000",
    "python_version": "not_set",
    "message": "Using shell script for Railway compatibility"
  }
}
```

## 🔧 **چرا این راه‌حل کار می‌کنه:**

1. **Shell Script**: خودمون PORT رو handle می‌کنیم
2. **Environment Variable**: `$PORT` رو مستقیماً می‌گیریم
3. **Validation**: چک می‌کنیم که PORT عدد باشه
4. **Fallback**: اگر PORT invalid باشه، از default استفاده می‌کنیم
5. **Exec**: با `exec` uvicorn رو start می‌کنیم

## 🚨 **اگر هنوز مشکل داشت:**

### **Check 1: Railway Logs**
- Go to Railway dashboard
- Click on your service
- Check "Deployments" tab
- Look for shell script errors

### **Check 2: File Permissions**
- Ensure `start.sh` is executable
- Check file exists in repository

### **Check 3: Shell Availability**
- Verify bash is available
- Check shell script syntax

## 📝 **Success Indicators:**
- ✅ No more "$PORT" errors
- ✅ Shell script starts successfully
- ✅ Uvicorn starts with correct port
- ✅ Application responds to requests
- ✅ Root endpoint returns 200
- ✅ Health endpoint shows components ready

## 🔧 **Alternative Approaches:**

### **Option 1: Shell Script (current)**
```
web: bash start.sh
```

### **Option 2: Direct Shell Command**
```
web: bash -c "PORT=\${PORT:-8000}; uvicorn main:app --host 0.0.0.0 --port \$PORT --workers 1"
```

### **Option 3: Environment Variable Default**
```
web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
```

## 🎯 **نکات مهم:**
1. **Shell Script**: خودمون PORT رو handle می‌کنیم
2. **Environment Variable**: `$PORT` رو مستقیماً می‌گیریم
3. **Validation**: چک می‌کنیم که PORT عدد باشه
4. **Fallback**: Fallback به default port
5. **Exec**: Safe command execution

## 🔍 **مزایای این روش:**

- **قابل اعتماد**: خودمون PORT رو handle می‌کنیم
- **Environment Variable**: مستقیماً از Railway می‌گیریم
- **Validation**: چک می‌کنیم که PORT valid باشه
- **Fallback**: Fallback mechanisms
- **Railway Friendly**: Minimal Procfile command

**حالا تغییرات رو push کن و Railway رو redeploy کن. Shell script خودش PORT رو handle می‌کنه!** 🚀
