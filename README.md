# Meal Optimization System - سیستم بهینه‌سازی وعده‌های غذایی

## English Description
Advanced meal optimization system using cutting-edge mathematical optimization techniques including:
- Linear Programming (PuLP)
- Genetic Algorithms (DEAP)
- Machine Learning (Scikit-learn)
- Multi-objective optimization
- Nutritional constraint satisfaction

## توضیحات فارسی
سیستم پیشرفته بهینه‌سازی وعده‌های غذایی با استفاده از تکنیک‌های بهینه‌سازی ریاضی پیشرفته شامل:
- برنامه‌ریزی خطی (PuLP)
- الگوریتم‌های ژنتیک (DEAP)
- یادگیری ماشین (Scikit-learn)
- بهینه‌سازی چندهدفه
- برآورده‌سازی محدودیت‌های تغذیه‌ای

## Features / ویژگی‌ها
- 6 meal times: Breakfast, Morning Snack, Lunch, Afternoon Snack, Evening Snack, Dinner
- 6 وعده: صبحانه، میان‌وعده صبح، ناهار، میان‌وعده عصر، میان‌وعده شب، شام
- API integration with main website / اتصال API با وب‌سایت اصلی
- Advanced optimization algorithms / الگوریتم‌های بهینه‌سازی پیشرفته
- Personalized ingredient recommendations / توصیه‌های شخصی‌سازی شده مواد غذایی

## Installation / نصب
```bash
pip install -r requirements.txt
```

## Usage / استفاده
```bash
python main.py
```

## API Endpoints / نقاط پایانی API
- `POST /optimize-meal` - Optimize meal with given ingredients
- `GET /health` - Health check
- `POST /add-ingredients` - Add new ingredients to database

