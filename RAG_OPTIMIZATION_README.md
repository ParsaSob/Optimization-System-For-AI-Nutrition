# سیستم بهینه‌سازی RAG برای برنامه‌ریزی غذایی

## 🎯 خلاصه

این سیستم یک موتور بهینه‌سازی پیشرفته برای برنامه‌ریزی غذایی است که از سیستم RAG (Retrieval-Augmented Generation) استفاده می‌کند. سیستم با استفاده از الگوریتم‌های ژنتیک و بهینه‌سازی ریاضی، مواد غذایی RAG را دریافت کرده و آنها را برای رسیدن به اهداف تغذیه‌ای بهینه می‌کند.

## 🚀 ویژگی‌های کلیدی

- **بهینه‌سازی الگوریتم ژنتیک**: استفاده از الگوریتم‌های ژنتیک برای تنظیم مقادیر مواد
- **تحلیل مواد RAG**: محاسبه خودکار کالری، پروتئین، کربوهیدرات و چربی موجود
- **بهینه‌سازی هوشمند**: شناسایی کمبودها و افزودن مواد تکمیلی
- **رعایت ترجیحات کاربر**: احترام به محدودیت‌های غذایی و آلرژی‌ها
- **بهینه‌سازی هزینه**: انتخاب مواد مقرون به صرفه
- **پشتیبانی از زبان فارسی**: رابط کاربری و پیام‌های فارسی

## 🏗️ معماری سیستم

### مدل‌های داده

```typescript
// فرمت ورودی RAG
interface RAGIngredient {
  name: string;
  amount: string | number;
  unit: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

interface RAGSuggestion {
  mealTitle?: string;
  description?: string;
  ingredients: RAGIngredient[];
  totalCalories?: number;
  totalProtein?: number;
  totalCarbs?: number;
  totalFat?: number;
  instructions?: string;
}

interface RAGResponse {
  suggestions: RAGSuggestion[];
  success: boolean;
  message?: string;
}

// درخواست بهینه‌سازی
interface SingleMealOptimizationRequest {
  rag_response: RAGResponse;
  target_macros: {
    calories: number;
    protein: number;
    carbohydrates: number;
    fat: number;
  };
  user_preferences: {
    dietary_restrictions: string[];
    allergies: string[];
    preferred_cuisines: string[];
    calorie_preference: 'low' | 'moderate' | 'high';
    protein_preference: 'low' | 'moderate' | 'high';
    carb_preference: 'low' | 'moderate' | 'high';
    fat_preference: 'low' | 'moderate' | 'high';
  };
  user_id: string;
  meal_type: string;
}

// پاسخ مورد انتظار
interface SingleMealOptimizationResponse {
  optimization_result: {
    success: boolean;
    method: string;
    computation_time: number;
    target_achieved?: boolean;
  };
  meal: {
    meal_time: string;
    total_calories: number;
    total_protein: number;
    total_carbs: number;
    total_fat: number;
    items: {
      ingredient: string;
      quantity_grams: number;
      calories: number;
      protein: number;
      carbs: number;
      fat: number;
    }[];
  };
  target_achievement: {
    calories_achieved: boolean;
    protein_achieved: boolean;
    carbs_achieved: boolean;
    fat_achieved: boolean;
    notes?: string;
  };
  recommendations: string[];
  rag_enhancement: {
    original_macros?: {
      calories: number;
      protein: number;
      carbs: number;
      fat: number;
    };
    added_ingredients?: RAGIngredient[];
    enhancement_notes?: string;
    enhancement_method?: string;
    original_ingredients?: number;
    supplements_added?: number;
    total_ingredients?: number;
  };
  user_id?: string;
}
```

## 🔧 نصب و راه‌اندازی

### پیش‌نیازها

- Python 3.8+
- pip

### نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### راه‌اندازی سرور

```bash
python backend_server.py
```

سرور روی پورت 5000 راه‌اندازی می‌شود.

## 📡 API Endpoints

### 1. بررسی سلامت سیستم
```
GET /health
```

### 2. بهینه‌سازی تک وعده غذایی اصلی
```
POST /optimize-single-meal
```

### 3. بهینه‌سازی تک وعده غذایی با RAG
```
POST /optimize-single-meal-rag
```

### 4. بهینه‌سازی پیشرفته RAG (پیشنهادی)
```
POST /optimize-single-meal-rag-advanced
```

### 5. دریافت مواد غذایی موجود
```
GET /api/ingredients
```

### 6. دریافت مواد غذایی RAG
```
GET /api/rag-ingredients
```

## 🧠 الگوریتم بهینه‌سازی

### مراحل بهینه‌سازی

1. **تحلیل مواد RAG**: استخراج مواد و محاسبه مقادیر تغذیه‌ای فعلی
2. **محاسبه کمبودها**: شناسایی تفاوت بین مقادیر فعلی و اهداف
3. **افزودن مواد تکمیلی**: انتخاب مواد مناسب برای پر کردن کمبودها
4. **بهینه‌سازی مقادیر**: استفاده از الگوریتم‌های ژنتیک برای تنظیم مقادیر
5. **اعتبارسنجی نهایی**: بررسی رسیدن به اهداف و تولید توصیه‌ها

### روش‌های بهینه‌سازی

- **الگوریتم ژنتیک (DEAP)**: بهینه‌سازی تکاملی
- **تکامل تفاضلی (SciPy)**: بهینه‌سازی با الگوریتم‌های تکاملی
- **برنامه‌ریزی خطی**: بهینه‌سازی با محدودیت‌های خطی
- **روش ترکیبی**: ترکیب چندین روش برای بهترین نتیجه

## 📊 مثال استفاده

### درخواست نمونه

```json
{
  "rag_response": {
    "suggestions": [
      {
        "mealTitle": "Persian Chicken and Rice",
        "ingredients": [
          {
            "name": "Chicken Breast",
            "amount": 150,
            "unit": "grams",
            "calories": 247.5,
            "protein": 46.5,
            "carbs": 0,
            "fat": 5.4
          }
        ]
      }
    ],
    "success": true
  },
  "target_macros": {
    "calories": 800,
    "protein": 60,
    "carbohydrates": 80,
    "fat": 30
  },
  "user_preferences": {
    "dietary_restrictions": ["halal"],
    "allergies": [],
    "preferred_cuisines": ["persian"]
  },
  "user_id": "user_123",
  "meal_type": "lunch"
}
```

### پاسخ نمونه

```json
{
  "optimization_result": {
    "success": true,
    "method": "Genetic Algorithm (DEAP)",
    "computation_time": 0.245,
    "target_achieved": true
  },
  "meal": {
    "meal_time": "lunch",
    "total_calories": 798.5,
    "total_protein": 60.2,
    "total_carbs": 79.8,
    "total_fat": 29.7,
    "items": [
      {
        "ingredient": "Chicken Breast",
        "quantity_grams": 180.5,
        "calories": 298.2,
        "protein": 56.0,
        "carbs": 0,
        "fat": 6.5
      }
    ]
  },
  "target_achievement": {
    "calories_achieved": true,
    "protein_achieved": true,
    "carbs_achieved": true,
    "fat_achieved": true
  },
  "recommendations": [
    "This meal plan has been enhanced with additional ingredients to meet your nutritional targets"
  ],
  "rag_enhancement": {
    "enhancement_method": "Mathematical optimization to meet targets",
    "original_ingredients": 1,
    "supplements_added": 2,
    "total_ingredients": 3
  }
}
```

## 🧪 تست سیستم

### اجرای تست‌ها

```bash
python test_rag_optimization.py
```

### تست دستی با cURL

```bash
curl -X POST http://localhost:5000/optimize-single-meal-rag-advanced \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## 🔍 عیب‌یابی

### مشکلات رایج

1. **خطای وابستگی‌ها**: اطمینان از نصب تمام وابستگی‌ها
2. **خطای پورت**: بررسی آزاد بودن پورت 5000
3. **خطای پایگاه داده**: بررسی وجود فایل `ingredients_database.json`

### لاگ‌ها

سیستم لاگ‌های مفصلی تولید می‌کند که در کنسول نمایش داده می‌شوند.

## 🚀 استقرار

### استقرار محلی

```bash
python backend_server.py
```

### استقرار در Render

1. اتصال repository به Render
2. تنظیم متغیرهای محیطی
3. استقرار خودکار

### استقرار در Railway

1. اتصال repository به Railway
2. تنظیم متغیرهای محیطی
3. استقرار خودکار

## 📈 عملکرد

### معیارهای عملکرد

- **زمان پردازش**: معمولاً کمتر از 1 ثانیه
- **دقت بهینه‌سازی**: ±10% از اهداف
- **مقیاس‌پذیری**: پشتیبانی از 100+ ماده غذایی
- **قابلیت اطمینان**: 99%+ موفقیت در بهینه‌سازی

### بهینه‌سازی‌ها

- استفاده از الگوریتم‌های موازی
- کش کردن نتایج
- بهینه‌سازی حافظه

## 🤝 مشارکت

### گزارش باگ

لطفاً مشکلات را در Issues repository گزارش دهید.

### درخواست ویژگی

برای درخواست ویژگی‌های جدید، از Issues استفاده کنید.

### مشارکت در کد

1. Fork repository
2. ایجاد branch جدید
3. اعمال تغییرات
4. ارسال Pull Request

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است.

## 📞 پشتیبانی

برای سوالات و پشتیبانی:
- ایجاد Issue در repository
- تماس با تیم توسعه

---

**توسعه‌دهنده**: تیم بهینه‌سازی غذایی فارسی  
**نسخه**: 1.0.0  
**تاریخ آخرین به‌روزرسانی**: 2024
