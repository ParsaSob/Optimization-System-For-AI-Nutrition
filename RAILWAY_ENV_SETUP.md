# 🔧 Railway Environment Variables Setup

## 🚨 **مشکل فعلی:**
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

## 🛠️ **راه‌حل: Environment Variables**

### **1. در Railway Dashboard:**
1. برو به project
2. روی service کلیک کن
3. به تب "Variables" برو
4. این variables رو اضافه کن:

```
PORT=8000
HOST=0.0.0.0
PYTHON_VERSION=3.11.9
NODE_ENV=production
```

### **2. یا از Railway CLI:**
```bash
# Set environment variables
railway variables set PORT=8000
railway variables set HOST=0.0.0.0
railway variables set PYTHON_VERSION=3.11.9
railway variables set NODE_ENV=production

# Deploy
railway up
```

### **3. یا از فایل .env:**
فایل `env_example.txt` رو کپی کن و به `.env` تغییر نام بده:

```bash
cp env_example.txt .env
```

## 📁 **فایل‌های Environment:**

### **env_example.txt:**
```
PORT=8000
HOST=0.0.0.0
PYTHON_VERSION=3.11.9
NODE_ENV=production
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
LOG_LEVEL=info
```

### **start.py:**
- از `python-dotenv` استفاده می‌کنه
- Environment variables رو load می‌کنه
- Fallback values داره

### **main.py:**
- Environment variables رو درست handle می‌کنه
- Railway port رو درست می‌خونه
- Better logging داره

## 🚀 **مراحل Deploy:**

### **1. Push تغییرات:**
```bash
git add .
git commit -m "Add environment variables support with python-dotenv"
git push
```

### **2. در Railway Dashboard:**
1. Environment variables رو set کن
2. Redeploy کن
3. Logs رو چک کن

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
🚀 Starting Meal Optimization API on 0.0.0.0:8000
🔧 Railway PORT: 8000
🔧 Environment HOST: 0.0.0.0
🔧 Environment PORT: 8000
```

### **Root Endpoint:**
```json
{
  "message": "Meal Optimization API is running",
  "status": "healthy",
  "port": 8000,
  "host": "0.0.0.0",
  "railway_info": {
    "port": 8000,
    "port_env": "8000",
    "host_env": "0.0.0.0"
  }
}
```

## 🚨 **اگر هنوز مشکل داشت:**

### **Check 1: Environment Variables**
- Railway dashboard رو چک کن
- Variables درست set شدن
- `PORT=8000` وجود داره

### **Check 2: Dependencies**
- `python-dotenv` در requirements.txt هست
- Railway dependencies رو install کرده

### **Check 3: Logs**
- Railway logs رو چک کن
- Environment variables درست load شدن

## 📝 **Success Indicators:**
- ✅ No more "$PORT" errors
- ✅ Environment variables load شدن
- ✅ Application روی port 8000 start شد
- ✅ Root endpoint returns 200
