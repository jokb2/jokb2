from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import requests
import re
import random
import string
import threading
import time
import os
import json

TOKEN = "7976738230:AAHMz5rc5_iNEbl71pS-4xphLJsv3HDdWAM"  # حط توكنك هنا

ASK_URL = 1
ASK_CHECK_URL = 2
ASK_NEWS = 3
ADDING_NEWS = 4  # لحفظ عدة رسائل للخبر

user_ids = set()
news_file = "news_data.json"

def register_user(update):
    user_id = update.effective_user.id
    user_ids.add(user_id)

def start(update, context):
    register_user(update)
    update.message.reply_text("""Welcome, I Amoory's boy
I can do:
1)Link Shortener 🛠
2)Link Safety Checker
3)Password Generator
4)Show Random cyber News
مطوري هو :@sanme_1 😎
I think you will love me 😊
    """)

def test(update, context):
    register_user(update)
    update.message.reply_text("✅ هذا اختبار")

def num(update, context):
    register_user(update)
    count = len(user_ids)
    update.message.reply_text(f"👤 عدد مستخدمي البوت حتى الآن: {count}")

# === Link Shortener ===
def creat_start(update, context):
    register_user(update)
    update.message.reply_text("📎 أرسل الرابط الذي تريد اختصاره:")
    return ASK_URL

def is_valid_url(url):
    regex = re.compile(r'^(?:http|ftp)s?://\S+$', re.IGNORECASE)
    return re.match(regex, url) is not None

def shorten_url(long_url):
    if not long_url.startswith(('http://', 'https://')):
        long_url = 'http://' + long_url
    if not is_valid_url(long_url):
        return None
    try:
        res = requests.get("http://tinyurl.com/api-create.php", params={"url": long_url}, timeout=10)
        if res.status_code == 200:
            short = res.text.strip()
            if short.startswith('http://'):
                short = short.replace('http://', 'https://', 1)
            return short if short.startswith('https://') else None
    except:
        return None

def receive_url(update, context):
    register_user(update)
    url = update.message.text
    short = shorten_url(url)
    if short:
        update.message.reply_text(f"🔗 رابطك المختصر:\n{short}")
    else:
        update.message.reply_text("❌ حصل خطأ في اختصار الرابط.")
    return ConversationHandler.END

# === Link Checker ===
def check_start(update, context):
    register_user(update)
    update.message.reply_text(" أرسل الرابط اللي تريد فحصه:")
    return ASK_CHECK_URL

def analyze_link_safety(url):
    suspicious = ['login', 'verify', 'update', 'secure', 'account', 'free', 'gift', 'bank', 'password','malicious']
    score = sum(word in url.lower() for word in suspicious)
    if "@" in url or url.count('.') > 4:
        score += 1
    if score >= 2:
        return False, "الرابط ذا مشبوه | وانا ك Amoory's boy انصحك لا تدخل عليه ترا ممكن يكون رابط احتيال"
    else:
        return True, "✅ الرابط آمن."

def receive_check_url(update, context):
    register_user(update)
    url = update.message.text.strip()
    if not is_valid_url(url):
        update.message.reply_text("❌ الرابط غير صالح. تأكد أنه يبدأ بـ http أو https.")
        return ConversationHandler.END
    _, verdict = analyze_link_safety(url)
    update.message.reply_text(verdict)
    return ConversationHandler.END

# === Password Generator ===
def generate_password(length=12):
    if length < 6: length = 6
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(random.choice(chars) for _ in range(length))

def delete_message_later(bot, chat_id, msg_id, delay=20):
    time.sleep(delay)
    try: bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except: pass

def password_command(update, context):
    register_user(update)
    try:
        length = int(context.args[0]) if context.args else 12
    except:
        length = 12
    password = generate_password(length)
    msg = update.message.reply_text(
        f"اقل عدد احرف لكلمة المرور هي ست احرف\nكلمة السر العشوائية:\n`{password}`\n\n⚠️ سوف يتم حذف هذه الرسالة خلال 20 ثانية",
        parse_mode='Markdown'
    )
    threading.Thread(target=delete_message_later, args=(context.bot, update.message.chat_id, msg.message_id, 20)).start()

# === Cyber News System ===
def load_news():
    if not os.path.exists(news_file):
        return []
    with open(news_file, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_news(news_list):
    with open(news_file, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

def addnews_start(update, context):
    register_user(update)
    context.user_data['news_messages'] = []
    update.message.reply_text("📝 أرسل لي رسائل الخبر واحد واحد. ارسل /done لما تخلص.")
    return ADDING_NEWS

def receive_news_message(update, context):
    register_user(update)
    msg = update.message
    entry = {}
    if msg.text:
        entry['type'] = 'text'
        entry['content'] = msg.text
    elif msg.photo:
        photo_file = msg.photo[-1].file_id
        entry['type'] = 'photo'
        entry['content'] = photo_file
        if msg.caption:
            entry['caption'] = msg.caption
    else:
        update.message.reply_text("❌ نوع الرسالة غير مدعوم، أرسل نص أو صورة فقط.")
        return ADDING_NEWS

    context.user_data['news_messages'].append(entry)
    update.message.reply_text(f"✅ استلمت جزء من الخبر، أرسل المزيد أو /done للانتهاء.")
    return ADDING_NEWS

def addnews_done(update, context):
    register_user(update)
    news_messages = context.user_data.get('news_messages', [])
    if not news_messages:
        update.message.reply_text("❌ ما أرسلت أي جزء من الخبر.")
        return ConversationHandler.END
    news_list = load_news()
    news_list.append(news_messages)
    save_news(news_list)
    update.message.reply_text(f"✅ تم حفظ الخبر بنجاح. يمكنك إضافة أخبار أخرى بأي وقت.")
    return ConversationHandler.END

def getnews(update, context):
    register_user(update)
    news_list = load_news()
    if not news_list:
        update.message.reply_text("❌ لا يوجد أخبار محفوظة.")
        return
    chosen_news = random.choice(news_list)
    for part in chosen_news:
        if part['type'] == 'text':
            update.message.reply_text(part['content'])
        elif part['type'] == 'photo':
            caption = part.get('caption', None)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=part['content'], caption=caption)

def hop(update, context):
    register_user(update)
    if os.path.exists(news_file):
        os.remove(news_file)
        update.message.reply_text("🗑️ تم حذف جميع الأخبار بنجاح.")
    else:
        update.message.reply_text("ℹ️ لا يوجد أخبار محفوظة أصلاً.")

def cancel(update, context):
    update.message.reply_text("🚫 تم إلغاء العملية.")
    return ConversationHandler.END

from telegram.ext import Filters

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("test", test))
dp.add_handler(CommandHandler("num", num))
dp.add_handler(CommandHandler("pass", password_command))
dp.add_handler(CommandHandler("getnews", getnews))
dp.add_handler(CommandHandler("hop", hop))

dp.add_handler(ConversationHandler(
    entry_points=[CommandHandler("creat", creat_start)],
    states={ASK_URL: [MessageHandler(Filters.text & ~Filters.command, receive_url)]},
    fallbacks=[CommandHandler("cancel", cancel)]
))

dp.add_handler(ConversationHandler(
    entry_points=[CommandHandler("check", check_start)],
    states={ASK_CHECK_URL: [MessageHandler(Filters.text & ~Filters.command, receive_check_url)]},
    fallbacks=[CommandHandler("cancel", cancel)]
))

dp.add_handler(ConversationHandler(
    entry_points=[CommandHandler("addnews", addnews_start)],
    states={
        ADDING_NEWS: [
            MessageHandler(Filters.text & ~Filters.command, receive_news_message),
            MessageHandler(Filters.photo, receive_news_message)
        ],
    },
    fallbacks=[CommandHandler("done", addnews_done), CommandHandler("cancel", cancel)]
))

updater.start_polling()
print("✅ البوت يعمل الآن")
updater.idle()
