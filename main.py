import os
import time
import urllib.parse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import google.generativeai as genai

# ----------------------------------------------------
# Render Port Binding
# ----------------------------------------------------
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

# ----------------------------------------------------
# ১. কনফিগারেশন (নতুন টোকেন সরাসরি যুক্ত করা হলো)
# ----------------------------------------------------
BOT_TOKEN = "8833020885:AAGYVPU7VepcGsrfC-m6xelTafeIvxrdYHM"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

BAD_WORDS = ["nude", "naked", "sex", "porn", "কাপড় খুলি", "উলঙ্গ", "নগ্ন"]

def is_safe_prompt(prompt_text):
    text = prompt_text.lower()
    return not any(word in text for word in BAD_WORDS)

# ----------------------------------------------------
# স্থায়ী মেনু কিবোর্ড (সবসময় নিচে ফিক্সড থাকবে)
# ----------------------------------------------------
def get_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🤖 AI Chat")
    btn2 = KeyboardButton("📸 DSLR HD Enhance")
    btn3 = KeyboardButton("🎨 16K Masterpiece Image")
    btn4 = KeyboardButton("ℹ️ How to Use")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# ----------------------------------------------------
# ২. /start কমান্ড
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"হ্যালো {message.from_user.first_name}! 👋\n\n"
        "আমি আপনার **16K Ultra-HD DSLR AI Assistant**! 🤖✨\n"
        "নিচের স্থায়ী মেনু থেকে যেকোনো অপশন সিলেক্ট করুন অথবা সরাসরি চ্যাট করুন!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# ----------------------------------------------------
# ৩. ছবি অ্যানালাইসিস
# ----------------------------------------------------
@bot.message_handler(content_types=['photo'])
def handle_user_photo(message):
    status_msg = bot.reply_to(message, "⚙️ 16K রেজোলিউশন ও Medium Format প্রফেশনাল ফটোগ্রাফি মানদণ্ডে প্রসেস করা হচ্ছে...", reply_markup=get_main_keyboard())
    image_path = f"photo_{message.chat.id}.jpg"
    
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        if GEMINI_API_KEY:
            sample_file = genai.upload_file(path=image_path)
            dslr_prompt = (
                "Analyze this photo like a professional Phase One 150MP DSLR photographer. "
                "Describe in natural, friendly Bangla language how to refine this image to a 16K Ultra-HD masterpiece with sharp focus, smooth bokeh, and professional lighting."
            )
            response = model.generate_content([sample_file, dslr_prompt])
            bot.reply_to(message, f"✨ **16K DSLR Masterclass Report:**\n\n{response.text}", reply_markup=get_main_keyboard())
        else:
            bot.reply_to(message, "⚠️ API Key কনফিগার করা নেই!", reply_markup=get_main_keyboard())

        bot.delete_message(message.chat.id, status_msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ সমস্যা হয়েছে: {str(e)}", message.chat.id, status_msg.message_id)
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

# ----------------------------------------------------
# ৪. বাটন ক্লিক এবং চ্যাটিং হ্যান্ডলার
# ----------------------------------------------------
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text

    if not is_safe_prompt(user_text):
        bot.reply_to(message, "⚠️ **দুঃখিত!** অনৈতিক বিষয় সম্পূর্ণ নিষিদ্ধ।", reply_markup=get_main_keyboard())
        return

    # মেনু বাটনের কমান্ড হ্যান্ডলিং
    if user_text == "🤖 AI Chat":
        bot.reply_to(message, "💬 **AI চ্যাট সক্রিয়!** যা খুশি লিখে পাঠান, আমি উত্তর দিচ্ছি।", reply_markup=get_main_keyboard())
        return
    elif user_text == "📸 DSLR HD Enhance":
        bot.reply_to(message, "📸 আপনার প্রফেশনাল ছবিটি পাঠান—আমি এটিকে 16K Medium Format DSLR লুকে বিশ্লেষণ করে দেব।", reply_markup=get_main_keyboard())
        return
    elif user_text == "🎨 16K Masterpiece Image":
        bot.reply_to(message, "🎨 আপনি কীসের ছবি দেখতে চান তা লিখে পাঠান (যেমন: *'A handsome boy, 16k DSLR'*), আমি ছবি বানিয়ে দেব!", reply_markup=get_main_keyboard())
        return
    elif user_text == "ℹ️ How to Use":
        help_text = (
            "📖 **বট ব্যবহারের গাইডলাইন:**\n\n"
            "১. **AI Chat:** যেকোনো প্রশ্ন করুন।\n"
            "২. **DSLR HD Enhance:** ছবি পাঠিয়ে ডিএসএলআর পরামর্শ নিন।\n"
            "৩. **16K Masterpiece Image:** যেকোনো বিষয় লিখে ছবি তৈরি করুন।"
        )
        bot.reply_to(message, help_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return

    image_keywords = ["বানাও", "তৈরি কর", "ছবি দাও", "আঁকো", "make image", "generate", "draw", "photo of", "picture of"]
    is_image_req = any(keyword in user_text.lower() for keyword in image_keywords)

    if is_image_req:
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
    else:
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            if GEMINI_API_KEY:
                response = model.generate_content(f"ইউজারের সাথে অমায়িক প্রফেশনাল বাংলায় কথা বলো: {user_text}")
                bot.reply_to(message, response.text, reply_markup=get_main_keyword())
            else:
                bot.reply_to(message, "আপনার বার্তাটি পেয়েছি!", reply_markup=get_main_keyboard())
        except Exception as e:
            bot.reply_to(message, "বলুন, আপনাকে কীভাবে সাহায্য করতে পারি?", reply_markup=get_main_keyboard())

# ----------------------------------------------------
# ৫. পলিস লুপ
# ----------------------------------------------------
print("16K DSLR Bot is Active...")
while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        time.sleep(3)
