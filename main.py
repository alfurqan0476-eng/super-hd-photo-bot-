import os
import time
import urllib.parse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import google.generativeai as genai

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN এনভায়রনমেন্ট ভ্যারিয়েবল পাওয়া যায়নি!")

bot = telebot.TeleBot(BOT_TOKEN)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

BAD_WORDS = ["nude", "naked", "sex", "porn", "কাপড় খুলি", "উলঙ্গ", "নগ্ন"]

def is_safe_prompt(prompt_text):
    text = prompt_text.lower()
    return not any(word in text for word in BAD_WORDS)

def get_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🤖 AI Chat")
    btn2 = KeyboardButton("📸 DSLR HD Enhance")
    btn3 = KeyboardButton("🎨 16K Masterpiece Image")
    btn4 = KeyboardButton("ℹ️ How to Use")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"হ্যালো {message.from_user.first_name}! 👋\n\n"
        "আমি আপনার **16K Ultra-HD DSLR AI Assistant**! 🤖✨\n"
        "নিচের স্থায়ী মেনু থেকে যেকোনো অপশন সিলেক্ট করুন অথবা সরাসরি চ্যাট করুন!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# ছবি পাঠালে সাথে সাথে 16K DSLR মাস্টারপিস ইমেজ তৈরি করে দেবে
@bot.message_handler(content_types=['photo'])
def handle_user_photo(message):
    status_msg = bot.reply_to(message, "✨ **Phase One 150MP ক্যামেরা লুকে 16K Ultra-HD ছবি তৈরি হচ্ছে...**", reply_markup=get_main_keyboard())
    try:
        ultra_16k_prompt = (
            "A professional 16k resolution portrait, shot on Phase One IQ4 150MP medium format camera, "
            "ultra-sharp focus, cinematic raytraced lighting, hyper-photorealistic skin texture, DSLR bokeh"
        )
        encoded_prompt = urllib.parse.quote(ultra_16k_prompt)
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1280&height=1280&model=flux-realism&seed=999&nologo=true"

        bot.send_photo(
            message.chat.id, 
            image_url, 
            caption="🌟 **আপনার কাঙ্ক্ষিত 16K Medium Format DSLR ছবি প্রস্তুত!**",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        bot.delete_message(message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ ছবি তৈরি করতে সমস্যা হয়েছে!", message.chat.id, status_msg.message_id)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text

    if not is_safe_prompt(user_text):
        bot.reply_to(message, "⚠️ **দুঃখিত!** অনৈতিক বিষয় সম্পূর্ণ নিষিদ্ধ।", reply_markup=get_main_keyboard())
        return

    if user_text == "🤖 AI Chat":
        bot.reply_to(message, "💬 **AI চ্যাট সক্রিয়!** যা খুশি লিখে পাঠান, আমি উত্তর দিচ্ছি।", reply_markup=get_main_keyboard())
        return
    elif user_text == "📸 DSLR HD Enhance":
        bot.reply_to(message, "📸 আপনার যেকোনো ছবি পাঠান—আমি সেটিকে তৎক্ষণাৎ 16K Medium Format DSLR লুকে রূপান্তর করে দেব।", reply_markup=get_main_keyboard())
        return
    elif user_text == "🎨 16K Masterpiece Image":
        bot.reply_to(message, "🎨 আপনি কীসের ছবি দেখতে চান তা লিখে পাঠান (যেমন: *'A handsome boy, 16k DSLR'*), আমি ছবি বানিয়ে দেব!", reply_markup=get_main_keyboard())
        return
    elif user_text == "ℹ️ How to Use":
        help_text = (
            "📖 **বট ব্যবহারের গাইডলাইন:**\n\n"
            "১. **AI Chat:** যেকোনো প্রশ্ন করুন।\n"
            "২. **DSLR HD Enhance:** ছবি পাঠিয়ে 16K ডিএসএলআর রূপান্তর করুন।\n"
            "৩. **16K Masterpiece Image:** যেকোনো বিষয় লিখে ছবি তৈরি করুন।"
        )
        bot.reply_to(message, help_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return

    image_keywords = ["বানাও", "তৈরি কর", "ছবি দাও", "আঁকো", "make image", "generate", "draw", "photo of", "picture of"]
    is_image_req = any(keyword in user_text.lower() for keyword in image_keywords)

    if is_image_req or user_text:
        status_msg = bot.reply_to(message, "✨ **১৬কে (16K) Ultra-HD DSLR ছবি তৈরি হচ্ছে...**", reply_markup=get_main_keyboard())
        try:
            ultra_16k_prompt = (
                f"{user_text}, 16k resolution, shot on Phase One IQ4 150MP medium format camera, "
                f"ultra-sharp focus, cinematic raytraced lighting, hyper-photorealistic skin texture"
            )
            encoded_prompt = urllib.parse.quote(ultra_16k_prompt)
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1280&height=1280&model=flux-realism&seed=999&nologo=true"

            bot.send_photo(
                message.chat.id, 
                image_url, 
                caption=f"🌟 **আপনার কাঙ্ক্ষিত 16K Ultra-HD ছবি প্রস্তুত!**\n📝 *বিষয়:* {user_text}",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
            bot.delete_message(message.chat.id, status_msg.message_id)
        except Exception as e:
            bot.edit_message_text("❌ ছবি তৈরি করতে সমস্যা হয়েছে!", message.chat.id, status_msg.message_id)

print("16K DSLR Bot is Active...")
while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        time.sleep(3)
