import os
import time
import logging
import telebot

# ============================================================
# SOZLAMALAR
# ============================================================
TOKEN = os.environ.get("BOT_TOKEN", "8872082735:AAGmtLEWkwZqi0CfS_1k4zO-MZXq1Ubg-8Y")

# Admin IDlarni Railway Variables ga kiriting:
# ADMIN_IDS = 123456789,987654321
ADMIN_IDS_ENV = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS = set(int(x.strip()) for x in ADMIN_IDS_ENV.split(",") if x.strip().isdigit())

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

# ============================================================
# BOT
# ============================================================
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ============================================================
# YORDAMCHI
# ============================================================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def admin_only(func):
    def wrapper(message):
        if not is_admin(message.from_user.id):
            bot.send_message(message.chat.id, "Sizda ruxsat yoq.")
            return
        return func(message)
    return wrapper

# ============================================================
# HANDLERLAR
# ============================================================

@bot.message_handler(commands=["start"])
def cmd_start(message):
    name = message.from_user.first_name or "Foydalanuvchi"
    user_id = message.from_user.id
    status = "Admin" if is_admin(user_id) else "Foydalanuvchi"

    text = (
        f"Salom, <b>{name}</b>\n\n"
        f"ID: <code>{user_id}</code>\n"
        f"Holat: {status}\n\n"
        "/myid — ID ni bilish\n"
        "/help — Yordam\n"
    )

    if is_admin(user_id):
        text += (
            "\n<b>Admin buyruqlari:</b>\n"
            "/adminlar — Adminlar royxati\n"
            "/status — Bot holati\n"
        )

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["myid"])
def cmd_myid(message):
    uid = message.from_user.id
    bot.send_message(
        message.chat.id,
        f"Sizning Telegram ID: <code>{uid}</code>\n\n"
        "Shu IDni Railway da ADMIN_IDS ga kiriting."
    )


@bot.message_handler(commands=["help"])
def cmd_help(message):
    bot.send_message(
        message.chat.id,
        "<b>Yordam</b>\n\n"
        "Bot ishlayapti\n"
        "/myid — ID ingizni bilish\n"
        "/start — Asosiy menyu"
    )


@bot.message_handler(commands=["status"])
@admin_only
def cmd_status(message):
    admin_list = ", ".join(str(a) for a in ADMIN_IDS) if ADMIN_IDS else "Yoq"
    bot.send_message(
        message.chat.id,
        f"<b>Bot ishlayapti</b>\n\n"
        f"Adminlar: <code>{admin_list}</code>\n"
        f"Rejim: Polling (webhook yoq)\n"
        f"Auto-restart: Yoqilgan"
    )


@bot.message_handler(commands=["adminlar"])
@admin_only
def cmd_adminlar(message):
    if not ADMIN_IDS:
        bot.send_message(
            message.chat.id,
            "Hech qanday admin yoq.\n"
            "Railway > Variables > ADMIN_IDS ga ID kiriting."
        )
        return
    text = "<b>Adminlar royxati:</b>\n\n"
    for aid in ADMIN_IDS:
        text += f"<code>{aid}</code>\n"
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(message.chat.id, message.text)


# ============================================================
# ISHGA TUSHIRISH — to'xtamasdan ishlaydi, xato bo'lsa qayta
# ============================================================
def main():
    try:
        bot.remove_webhook()
        log.info("Webhook tozalandi")
    except Exception as e:
        log.warning(f"Webhook tozalashda xato: {e}")

    log.info(f"Bot ishga tushdi | Adminlar: {ADMIN_IDS if ADMIN_IDS else 'Hali kiritilmagan'}")

    while True:
        try:
            log.info("Polling boshlandi...")
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            log.error(f"Xato: {e}")
            log.info("5 soniyadan keyin qayta urinadi...")
            time.sleep(5)


if __name__ == "__main__":
    main()
