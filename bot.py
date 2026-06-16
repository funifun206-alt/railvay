import os
import telebot
from flask import Flask, request

# Token va muhit o'zgaruvchilari
TOKEN = os.environ.get("BOT_TOKEN", "8872082735:AAGmtLEWkwZqi0CfS_1k4zO-MZXq1Ubg-8Y")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # Railway URL

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ========================
# Bot handlerlar
# ========================

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom 👋 Bot ishlayapti!")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(message.chat.id, message.text)

# ========================
# Webhook endpoint
# ========================

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot ishlayapti! ✅", 200

# ========================
# Ishga tushirish
# ========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    if WEBHOOK_URL:
        # Railway muhiti — Webhook rejimi
        bot.remove_webhook()
        bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
        print(f"✅ Webhook o'rnatildi: {WEBHOOK_URL}/{TOKEN}")
        app.run(host="0.0.0.0", port=port)
    else:
        # Local muhit — Polling rejimi
        print("🔄 Polling rejimida ishlamoqda...")
        bot.remove_webhook()
        bot.polling(none_stop=True)
