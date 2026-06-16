# 🚂 Telegram Bot — Railway Deploy Qo'llanmasi

## 📁 Fayl tuzilmasi
```
railway_bot/
├── bot.py            ← Asosiy bot kodi
├── requirements.txt  ← Kutubxonalar
├── Procfile          ← Railway ishga tushirish buyrug'i
├── railway.json      ← Railway konfiguratsiyasi
├── .gitignore        ← Git uchun e'tiborsiz fayllar
└── README.md         ← Shu qo'llanma
```

---

## 🚀 DEPLOY QADAMLARI

### 1️⃣ GitHub Repozitory yaratish
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/SIZNING_USERNAME/bot.git
git push -u origin main
```

### 2️⃣ Railway.app ga kirish
1. https://railway.app saytiga boring
2. **"Login with GitHub"** tugmasini bosing
3. **"New Project"** → **"Deploy from GitHub repo"** tanlang
4. O'zingizning reponi tanlang

### 3️⃣ Environment Variables (Muhit o'zgaruvchilari) o'rnatish
Railway dashboard → **Variables** bo'limiga kiring va quyidagilarni qo'shing:

| Variable    | Qiymat                          |
|-------------|----------------------------------|
| BOT_TOKEN   | 8872082735:AAGmtLEWkwZ...       |
| WEBHOOK_URL | (4-qadamdan keyin to'ldirasiz)  |

### 4️⃣ Railway URL olish
Deploy bo'lgandan keyin:
- **Settings** → **Networking** → **Generate Domain** tugmasini bosing
- URL ko'rinishi: `https://sizning-bot.up.railway.app`

### 5️⃣ WEBHOOK_URL ni o'rnatish
Variables ga qayting va WEBHOOK_URL ga Railway URL ni kiriting:
```
WEBHOOK_URL = https://sizning-bot.up.railway.app
```
Saqlang — bot avtomatik qayta ishga tushadi ✅

---

## 🔧 Lokalda sinash (ixtiyoriy)
```bash
pip install -r requirements.txt
python bot.py
# WEBHOOK_URL bo'lmasa polling rejimida ishlaydi
```

---

## ⚠️ Muhim eslatmalar
- **TOKEN ni hech kimga bermang!**
- Railway bepul plani: oyiga 500 soat
- Agar bot to'xtasa: Railway → **Deployments** → **Redeploy**
