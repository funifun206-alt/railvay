import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
from database import Database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
STORAGE_CHANNEL_ID = os.getenv("STORAGE_CHANNEL_ID", "")  # e.g. -1001234567890
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

db = Database()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username or user.first_name)

    keyboard = [
        [InlineKeyboardButton("📁 Mening Shaxsiy Fayllarim", callback_data="my_files")],
        [InlineKeyboardButton("➕ Fayl Qo'shish Yo'riqnomasi", callback_data="how_to_add")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Salom {user.first_name}!\n"
        f"Botga yuborgan fayllaringiz <b>faqat siz uchun alohida</b> saqlanadi.\n\n"
        f"Fayllaringizni ko'rish uchun quyidagi tugmani bosing 👇",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    # Detect file type
    file_obj = None
    file_name = "Fayl"
    file_type = "document"

    if message.document:
        file_obj = message.document
        file_name = file_obj.file_name or "Hujjat"
        file_type = "document"
    elif message.photo:
        file_obj = message.photo[-1]
        file_name = "Rasm"
        file_type = "photo"
    elif message.video:
        file_obj = message.video
        file_name = file_obj.file_name or "Video"
        file_type = "video"
    elif message.audio:
        file_obj = message.audio
        file_name = file_obj.file_name or "Audio"
        file_type = "audio"
    elif message.voice:
        file_obj = message.voice
        file_name = "Ovozli xabar"
        file_type = "voice"
    else:
        await message.reply_text("❌ Bu fayl turi qo'llab-quvvatlanmaydi.")
        return

    # Forward to storage channel
    try:
        forwarded = await message.forward(chat_id=STORAGE_CHANNEL_ID)
        msg_id = forwarded.message_id

        # Save to DB
        db.save_file(
            user_id=user.id,
            message_id=msg_id,
            file_name=file_name,
            file_type=file_type,
            channel_id=STORAGE_CHANNEL_ID
        )

        await message.reply_text(
            f"✅ <b>{file_name}</b> muvaffaqiyatli saqlandi!\n"
            f"📁 Fayllaringizni ko'rish uchun /files buyrug'ini yuboring.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"File save error: {e}")
        await message.reply_text(
            "❌ Faylni saqlashda xatolik yuz berdi. Bot kanalga admin sifatida qo'shilganmi?"
        )


async def my_files_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    files = db.get_user_files(user.id)

    if not files:
        await update.message.reply_text(
            "📭 Sizda hali hech qanday fayl yo'q.\n\n"
            "Fayl yuborish uchun istalgan hujjat, rasm, video yoki audio yuboring!"
        )
        return

    await show_files_list(update, context, files, user.id, page=0)


async def show_files_list(update, context, files, user_id, page=0):
    per_page = 5
    total = len(files)
    start = page * per_page
    end = min(start + per_page, total)
    page_files = files[start:end]

    text = f"📁 <b>Sizning fayllaringiz</b> ({total} ta):\n\n"
    keyboard = []

    for i, f in enumerate(page_files, start=start + 1):
        emoji = get_file_emoji(f['file_type'])
        text += f"{i}. {emoji} {f['file_name']}\n"
        keyboard.append([
            InlineKeyboardButton(
                f"{emoji} {f['file_name'][:30]}",
                callback_data=f"get_file_{f['id']}"
            )
        ])

    # Pagination
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page_{page-1}"))
    if end < total:
        nav.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"page_{page+1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("🗑 Faylni o'chirish", callback_data="delete_mode")])
    keyboard.append([InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")


def get_file_emoji(file_type):
    emojis = {
        "document": "📄",
        "photo": "🖼",
        "video": "🎬",
        "audio": "🎵",
        "voice": "🎤",
    }
    return emojis.get(file_type, "📎")


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if data == "my_files":
        files = db.get_user_files(user.id)
        if not files:
            keyboard = [[InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]]
            await query.edit_message_text(
                "📭 Sizda hali hech qanday fayl yo'q.\n\n"
                "Fayl yuborish uchun istalgan hujjat, rasm, video yoki audio yuboring!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        await show_files_list(update, context, files, user.id, page=0)

    elif data == "how_to_add":
        keyboard = [[InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]]
        await query.edit_message_text(
            "📖 <b>Fayl qo'shish yo'riqnomasi:</b>\n\n"
            "1️⃣ Botga istalgan fayl yuboring\n"
            "2️⃣ Hujjat, rasm, video, audio qabul qilinadi\n"
            "3️⃣ Fayl avtomatik saqlanadi\n"
            "4️⃣ /files buyrug'i orqali ko'ring\n\n"
            "✅ Fayllaringiz <b>faqat siz</b> ko'ra olasiz!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    elif data.startswith("page_"):
        page = int(data.split("_")[1])
        files = db.get_user_files(user.id)
        await show_files_list(update, context, files, user.id, page=page)

    elif data.startswith("get_file_"):
        file_id = int(data.split("_")[2])
        file_info = db.get_file_by_id(file_id, user.id)
        if file_info:
            try:
                await context.bot.copy_message(
                    chat_id=user.id,
                    from_chat_id=file_info['channel_id'],
                    message_id=file_info['message_id']
                )
            except Exception as e:
                logger.error(f"Copy error: {e}")
                await query.message.reply_text("❌ Faylni yuklashda xatolik.")
        else:
            await query.message.reply_text("❌ Fayl topilmadi.")

    elif data == "delete_mode":
        files = db.get_user_files(user.id)
        if not files:
            await query.edit_message_text("📭 O'chirish uchun fayl yo'q.")
            return

        keyboard = []
        for f in files[:10]:
            emoji = get_file_emoji(f['file_type'])
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑 {emoji} {f['file_name'][:25]}",
                    callback_data=f"del_{f['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="my_files")])
        await query.edit_message_text(
            "🗑 <b>O'chirmoqchi bo'lgan faylni tanlang:</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    elif data.startswith("del_"):
        file_id = int(data.split("_")[1])
        success = db.delete_file(file_id, user.id)
        if success:
            await query.answer("✅ Fayl o'chirildi!", show_alert=True)
        else:
            await query.answer("❌ Xatolik yuz berdi.", show_alert=True)
        # Refresh files list
        files = db.get_user_files(user.id)
        if files:
            await show_files_list(update, context, files, user.id, page=0)
        else:
            keyboard = [[InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]]
            await query.edit_message_text(
                "📭 Barcha fayllar o'chirildi.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif data == "home":
        keyboard = [
            [InlineKeyboardButton("📁 Mening Shaxsiy Fayllarim", callback_data="my_files")],
            [InlineKeyboardButton("➕ Fayl Qo'shish Yo'riqnomasi", callback_data="how_to_add")],
        ]
        await query.edit_message_text(
            f"Salom {user.first_name}!\n"
            f"Botga yuborgan fayllaringiz <b>faqat siz uchun alohida</b> saqlanadi.\n\n"
            f"Fayllaringizni ko'rish uchun quyidagi tugmani bosing 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )


# ========== ADMIN COMMANDS ==========

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q.")
        return

    stats = db.get_stats()
    keyboard = [
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Xabar yuborish", callback_data="admin_broadcast")],
    ]
    await update.message.reply_text(
        f"🔧 <b>Admin Panel</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['users']}</b>\n"
        f"📁 Jami fayllar: <b>{stats['files']}</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    if not is_admin(user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    await query.answer()
    data = query.data

    if data == "admin_stats":
        stats = db.get_stats()
        await query.edit_message_text(
            f"📊 <b>Bot Statistikasi</b>\n\n"
            f"👥 Foydalanuvchilar: <b>{stats['users']}</b>\n"
            f"📁 Saqlangan fayllar: <b>{stats['files']}</b>\n"
            f"📅 Bugungi yangi foydalanuvchilar: <b>{stats['today_users']}</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")]])
        )

    elif data == "admin_users":
        users = db.get_all_users()
        text = f"👥 <b>Foydalanuvchilar ro'yxati</b> ({len(users)} ta):\n\n"
        for u in users[:20]:
            text += f"• {u['username']} (ID: {u['user_id']}) - {u['file_count']} fayl\n"
        if len(users) > 20:
            text += f"\n...va yana {len(users)-20} ta"
        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")]])
        )

    elif data == "admin_broadcast":
        context.user_data['broadcast_mode'] = True
        await query.edit_message_text(
            "📢 Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:\n\n"
            "(Bekor qilish uchun /cancel)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Bekor qilish", callback_data="admin_back")]])
        )

    elif data == "admin_back":
        stats = db.get_stats()
        keyboard = [
            [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton("📢 Xabar yuborish", callback_data="admin_broadcast")],
        ]
        await query.edit_message_text(
            f"🔧 <b>Admin Panel</b>\n\n"
            f"👥 Jami foydalanuvchilar: <b>{stats['users']}</b>\n"
            f"📁 Jami fayllar: <b>{stats['files']}</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )


async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        return
    if not context.user_data.get('broadcast_mode'):
        return

    context.user_data['broadcast_mode'] = False
    message = update.message
    users = db.get_all_users()

    sent = 0
    failed = 0
    for u in users:
        try:
            await context.bot.copy_message(
                chat_id=u['user_id'],
                from_chat_id=message.chat_id,
                message_id=message.message_id
            )
            sent += 1
        except Exception:
            failed += 1

    await message.reply_text(
        f"📢 <b>Xabar yuborildi!</b>\n\n"
        f"✅ Muvaffaqiyatli: {sent}\n"
        f"❌ Xatolik: {failed}",
        parse_mode="HTML"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Bekor qilindi.")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN muhit o'zgaruvchisi o'rnatilmagan!")
    if not STORAGE_CHANNEL_ID:
        raise ValueError("STORAGE_CHANNEL_ID muhit o'zgaruvchisi o'rnatilmagan!")

    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("files", my_files_command))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("cancel", cancel))

    # Callbacks
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Files
    app.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.VIDEO |
        filters.AUDIO | filters.VOICE,
        handle_file
    ))

    # Broadcast text
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_broadcast
    ))

    logger.info("Bot ishga tushdi...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
