import os
import time
import urllib.parse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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
# ১. কনফিগারেশন
# ----------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

BAD_WORDS = ["nude", "naked", "sex", "porn", "কাপড় খুলি", "উলঙ্গ", "নগ্ন"]

def is_safe_prompt(prompt_text):
    text = prompt_text.lower()
    return not any(word in text for word in BAD_WORDS)

# ----------------------------------------------------
# ২. /start কমান্ড ও বোতাম
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=2)
    
    btn1 = InlineKeyboardButton("🤖 AI Chat", callback_data="ai_chat")
    btn2 = InlineKeyboardButton("📸 DSLR HD Enhance", callback_data="enhance")
    btn3 = InlineKeyboardButton("🎨 16K Masterpiece Image", callback_data="img_gen")
    btn4 = InlineKeyboardButton("ℹ️ How to Use", callback_data="help")
    
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4)
    
    welcome_text = (
        f"হ্যালো {message.from_user.first_name}! 👋\n\n"
        "আমি আপনার **16K Ultra-HD DSLR AI Assistant**! 🤖✨\n"
        "আমার সাথে গল্প করতে পারেন, ছবি পাঠিয়ে প্রফেশনাল রিপোর্ট নিতে পারেন অথবা নতুন ১৬কে (16K) ছবি বানাতে পারেন!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "ai_chat":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💬 **AI চ্যাট সক্রিয়!** যা খুশি লিখে পাঠান, উত্তর দেব।")
        
    elif call.data == "enhance":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📸 আপনার ছবিটি পাঠান—আমি এটিকে একদম নিখুঁত 16K Medium Format DSLR লুক ও ডিটেইলসে বিশ্লেষণ করে দেব।")
    
    elif call.data == "img_gen":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🎨 কীসের ছবি দেখতে চান তা লিখে পাঠান (যেমন: *'A boy in pink jersey, 16k DSLR style'*), ছবি বানিয়ে দেব!")
        
    elif call.data == "help":
        bot.answer_callback_query(call.id)
        help_text = (
            "📖 **বট ব্যবহারের গাইডলাইন:**\n\n"
            "১. **🤖 AI Chat:** যেকোনো প্রশ্ন করুন বা কথা বলুন।\n"
            "২. **📸 DSLR HD Enhance:** আপনার ছবি প্রসেস করে ডিএসএলআর মান বজায় রাখার পরামর্শ পেতে ছবি পাঠান।\n"
            "৩. **🎨 Image Gen:** যেকোনো বিষয় লিখে সাথে 'ছবি বানাও' বলুন।"
        )
        bot.send_message(call.message.chat.id, help_text, parse_mode="Markdown")

# ----------------------------------------------------
# ৩. ছবি অ্যানালাইসিস (Fixing Error)
# ----------------------------------------------------
@bot.message_handler(content_types=['photo'])
def handle_user_photo(message):
    status_msg = bot.reply_to(message, "⚙️ 16K রেজোলিউশন ও Medium Format ফটোগ্রাফি মানদণ্ডে ছবি প্রসেস হচ্ছে...")
    image_path = f"photo_{message.chat.id}.jpg"
    
    try:
        # ছবি সেভ করা
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Gemini AI-তে ছবি আপলোড
        sample_file = genai.upload_file(path=image_path)
        
        dslr_prompt = (
            "Analyze this photo like a world-class professional photographer. "
            "Describe in beautiful, friendly, and natural Bangla language how to refine this image to a 16K ultra-HD, "
            "Phase One 150MP DSLR camera quality with sharp focus, depth blur, and professional lighting."
        )
        
        response = model.generate_content([sample_file, dslr_prompt])
        
        bot.reply_to(message, f"✨ **16K DSLR Masterclass Analysis:**\n\n{response.text}")
        bot.delete_message(message.chat.id, status_msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ সমস্যা হয়েছে: {str(e)}", message.chat.id, status_msg.message_id)
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

# ----------------------------------------------------
# ৪. চ্যাটিং ও 16K ফটো জেনারেটর
# ----------------------------------------------------
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text

    if not is_safe_prompt(user_text):
        bot.reply_to(message, "⚠️ **দুঃখিত!** অনৈতিক কোনো বিষয় অনুমতিপ্রাপ্ত নয়।")
        return

    image_keywords = ["বানাও", "তৈরি কর", "ছবি দাও", "আঁকো", "make image", "generate", "draw", "photo of", "picture of"]
    is_image_req = any(keyword in user_text.lower() for keyword in image_keywords)

    if is_image_req:
        status_msg = bot.reply_to(message, "✨ **১৬কে (16K) Ultra-HD DSLR ছবি তৈরি হচ্ছে...**")
        try:
            ultra_16k_prompt = (
                f"{user_text}, 16k resolution, shot on Phase One IQ4 150MP medium format camera, "
                f"ultra-sharp focus, cinematic lighting, hyper-photorealistic skin texture, masterwork"
            )
            encoded_prompt = urllib.parse.quote(ultra_16k_prompt)
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1280&height=1280&model=flux-realism&seed=999&nologo=true"

            bot.send_photo(
                message.chat.id, 
                image_url, 
                caption=f"🌟 **আপনার কাঙ্ক্ষিত 16K Ultra-HD ছবি প্রস্তুত!**\n📝 *বিষয়:* {user_text}",
                parse_mode="Markdown"
            )
            bot.delete_message(message.chat.id, status_msg.message_id)
        except Exception as e:
            bot.edit_message_text("❌ ছবি তৈরি করতে সমস্যা হয়েছে!", message.chat.id, status_msg.message_id)
    else:
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            response = model.generate_content(f"ইউজারের সাথে অমায়িক প্রফেশনাল বাংলায় কথা বলো: {user_text}")
            bot.reply_to(message, response.text)
        except Exception as e:
            bot.reply_to(message, "বলুন, আপনাকে কীভাবে সাহায্য করতে পারি?")

# ----------------------------------------------------
# ৫. পলিস লুপ
# ----------------------------------------------------
print("16K DSLR Bot is Active...")
while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        time.sleep(3)
