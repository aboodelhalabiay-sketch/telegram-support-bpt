from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)


TOKEN = "8941141926:AAFRGwDqPt9CvNmki0VJ9sCAWh1qhoLJhlo"

# ايدي جروب الدعم
SUPPORT_GROUP_ID = -1004296196413
message_users = {}
# تخزين المستخدمين اللي بيكتبوا للدعم
users_waiting = {}
active_users = {}


# رسالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "📩 تواصل مع الدعم",
                callback_data="contact_support"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 أهلاً بيك في ميد فيرس\n"
        "يقدر يساعدك إزاي؟ 👀",
        reply_markup=reply_markup
    )


# عند الضغط على زر الدعم
async def contact_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    users_waiting[user.id] = True

    await query.message.reply_text(
        "✍️ اكتب رسالتك وسيتم إرسالها لفريق الدعم."
    )


# استقبال رسالة المستخدم
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # لو المستخدم بدأ محادثة دعم
    if user.id in users_waiting or user.id in active_users:

        text = update.message.text

        message = (
            "📩 رسالة جديدة من المستخدم\n\n"
            f"👤 الاسم: {user.full_name}\n"
            f"🔹 Username: @{user.username if user.username else 'لا يوجد'}\n"
            f"🆔 User ID: {user.id}\n\n"
            f"💬 الرسالة:\n{text}"
        )

        sent = await context.bot.send_message(
            chat_id=SUPPORT_GROUP_ID,
            text=message
        )

        # ربط رسالة الجروب بالمستخدم
        message_users[sent.message_id] = user.id

        # حفظ المستخدم كمحادثة نشطة
        active_users[user.id] = True

        await update.message.reply_text(
            "✅ تم إرسال رسالتك للدعم، يمكنك متابعة المحادثة هنا."
        )

        # إزالة الانتظار بعد أول رسالة فقط
        if user.id in users_waiting:
            del users_waiting[user.id]
    # استقبال رد الأدمن من الجروب وإرساله للمستخدم
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # لازم تكون الرسالة رد على رسالة في الجروب
    if not update.message.reply_to_message:
        return

    # التأكد أن الرسالة من جروب الدعم
    if update.message.chat.id != SUPPORT_GROUP_ID:
        return

    replied_message_id = update.message.reply_to_message.message_id

    # جلب رقم المستخدم المرتبط بالرسالة
    user_id = message_users.get(replied_message_id)

    if not user_id:
        await update.message.reply_text(
            "❌ لم يتم العثور على المستخدم."
        )
        return

    reply_text = (
        "📩 رد من فريق الدعم:\n\n"
        f"{update.message.text}"
    )

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=reply_text
        )

        await update.message.reply_text(
            "✅ تم إرسال الرد للمستخدم."
        )

    except Exception:
        await update.message.reply_text(
            "❌ حصل خطأ أثناء إرسال الرد."
        )


# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(
            contact_support,
            pattern="contact_support"
        )
    )

    # ردود الأدمن من جروب الدعم (لازم يكون قبل user_message)
    app.add_handler(
        MessageHandler(
            filters.Chat(SUPPORT_GROUP_ID) & filters.TEXT,
            admin_reply
        )
    )

    # رسائل المستخدمين
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            user_message
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()