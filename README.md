# 📦 Storage Bot — Railway Deployment

Foydalanuvchilar fayllarini alohida saqlash uchun Telegram boti.

---

## 🚀 Railway ga Deploy qilish

### 1-qadam: Telegram sozlamalari

#### Bot yaratish:
1. [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` yuboring
3. Bot nomini kiriting (masalan: `MyStorageBot`)
4. Username kiriting (masalan: `my_storage_bot`)
5. **BOT TOKEN** ni saqlang

#### Storage Kanal yaratish:
1. Telegram da yangi **kanal** yarating (Private bo'lishi mumkin)
2. Botni kanalga **Admin** sifatida qo'shing (Post yuborish huquqi kerak)
3. Kanal ID sini olish uchun:
   - Kanalga istalgan xabar yuboring
   - [@username_to_id_bot](https://t.me/username_to_id_bot) ga forward qiling
   - Kanal ID si ko'rinadi (odatda `-100` bilan boshlanadi)

#### Admin ID olish:
1. [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring
2. Sizning Telegram ID ingiz ko'rinadi

---

### 2-qadam: Railway Deploy

1. [railway.app](https://railway.app) ga kiring
2. **New Project** → **Deploy from GitHub repo** tanlang
3. Bu papkani GitHub ga yuklang va u reponi tanlang
4. **Variables** bo'limiga o'ting va quyidagilarni kiriting:

```
BOT_TOKEN=your_bot_token_here
STORAGE_CHANNEL_ID=-1001234567890
ADMIN_IDS=your_telegram_id
```

5. **Deploy** tugmasini bosing ✅

---

## 📋 Bot Buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni ishga tushirish |
| `/files` | Fayllarimni ko'rish |
| `/admin` | Admin panel (faqat adminlar uchun) |
| `/cancel` | Amalni bekor qilish |

---

## 🔧 Admin Panel imkoniyatlari

- 👥 **Foydalanuvchilar ro'yxati** — kim qancha fayl saqlagan
- 📊 **Statistika** — jami foydalanuvchilar va fayllar soni
- 📢 **Xabar yuborish** — barcha foydalanuvchilarga broadcast

---

## 📁 Qo'llab-quvvatlanadigan fayl turlari

- 📄 Hujjatlar (PDF, Word, Excel, va h.k.)
- 🖼 Rasmlar
- 🎬 Videolar
- 🎵 Audio fayllar
- 🎤 Ovozli xabarlar

---

## ⚙️ Loyiha tuzilmasi

```
storage_bot/
├── bot.py          # Asosiy bot kodi
├── database.py     # SQLite ma'lumotlar bazasi
├── requirements.txt
├── Procfile        # Railway uchun
├── railway.toml    # Railway konfiguratsiya
└── .env.example    # Muhit o'zgaruvchilari namunasi
```

---

## 🔒 Xavfsizlik

- Har bir foydalanuvchi **faqat o'z fayllarini** ko'ra oladi
- Fayllar storage kanalda saqlanadi, foydalanuvchi kanal ID sini bilmaydi
- Admin panel faqat ruxsat etilgan ID larga ko'rinadi
