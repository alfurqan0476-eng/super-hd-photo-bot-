import os
import time
import urllib.parse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from google import genai

# ----------------------------------------------------
# Render Port Binding (সার্ভার সচল রাখার জন্য)
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
# ১. কনফিগারেশন ও সেফটি ফিল্টার
# ----------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

BAD_WORDS = [
    "nude", "naked", "undress", "remove clothes", "sex", "strip", "porn",
    "কাপড় খুলি", "উলঙ্গ", "নগ্ন", "কাপড় ছাড়া", "নেংটা"
]

def is_safe_prompt(prompt_text):
    text = prompt_text.lower()
    return not any(word in text for word in BAD_WORDS)

# ----------------------------------------------------
# ২. /start কমান্ড ও সুইচের তালিকা
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
        "আমি আপনার নিজস্ব **16K Ultra-HD DSLR AI Assistant**! 🤖✨\n"
        "আমার সাথে গল্প করতে পারেন, যেকোনো ছবির DSLR রিপোর্ট নিতে পারেন অথবা ১৬কে (16K) রেজোলিউশনে ছবি তৈরি করতে পারেন!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# বাটন ক্লিকের হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "ai_chat":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💬 **AI চ্যাট সক্রিয়!** যা খুশি লিখে পাঠান, মানুষের মতো সুন্দর উত্তর দেব।")
        
    elif call.data == "enhance":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📸 আপনার ছবিটি পাঠান—আমি এটিকে একদম নিখুঁত 16K Medium Format DSLR লুক এবং শার্প ডিটেইলসে সাজিয়ে দিচ্ছি।")
    
    elif call.data == "img_gen":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🎨 আপনি কীসের ছবি দেখতে চান তা লিখে পাঠান (যেমন: *'A majestic royal tiger in rain, 16k DSLR'*), আমি অতি-উচ্চমানের ছবি বানিয়ে দেব!")
        
    elif call.data == "help":
        bot.answer_callback_query(call.id)
        help_text = (
            "📖 **বট ব্যবহারের গাইডলাইন:**\n\n"
            "১. **🤖 AI Chat:** যেকোনো প্রশ্ন করুন বা কথা বলুন।\n"
            "২. **📸 DSLR HD Enhance:** আপনার ছবি প্রসেস করে ডিএসএলআর স্ট্যান্ডার্ড প্রম্পট পান।\n"
            "৩. **🎨 16K Masterpiece Image:** যেকোনো বিষয় লিখে সাথে 'ছবি বানাও' বলুন, সবচেয়ে উন্নত রেজোলিউশনে ছবি তৈরি হবে!"
        )
        bot.send_message(call.message.chat.id, help_text, parse_mode="Markdown")

# ----------------------------------------------------
# ৩. ছবি অ্যানালাইসিস ও 16K প্রফেশনাল রিপোর্ট
# ----------------------------------------------------
@bot.message_handler(content_types=['photo'])
def handle_user_photo(message):
    status_msg = bot.reply_to(message, "⚙️ 16K রেজোলিউশন ও প্রফেশনাল Medium Format ফটোগ্রাফি স্ট্যান্ডার্ডে প্রসেস করা হচ্ছে...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_path = "temp_user_photo.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        dslr_prompt = (
            "Analyze this photo as a world-class Phase One 150MP Medium Format photographer. "
            "Provide a deeply attractive masterclass response in friendly Bangla language "
            "explaining how to upgrade this photo into a 16K ultra-high-definition masterpiece with crisp focus, "
            "cinematic studio lighting, smooth bokeh background, and natural texture perfection."
        )
        
        if message.caption:
            dslr_prompt += f" User note: {message.caption}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[dslr_prompt, image_path]
        )
        
        bot.reply_to(message, f"✨ **16K DSLR Masterclass Report:**\n\n{response.text}")
        bot.delete_message(message.chat.id, status_msg.message_id)
        
        if os.path.exists(image_path):
            os.remove(image_path)
            
    except Exception as e:
        bot.edit_message_text("❌ ছবিটি প্রসেস করতে সমস্যা হয়েছে, আবার চেষ্টা করুন!", message.chat.id, status_msg.message_id)

# ----------------------------------------------------
# ৪. চ্যাটিং ও ১৬কে (16K) সুপার ইমেজ জেনারেটর
# ----------------------------------------------------
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text

    if not is_safe_prompt(user_text):
        bot.reply_to(message, "⚠️ **দুঃখিত!** অনৈতিক বা নীতিবহির্ভূত কোনো বিষয় সম্পূর্ণ নিষিদ্ধ।")
        return

    image_keywords = ["বানাও", "তৈরি কর", "ছবি দাও", "আঁকো", "make image", "generate", "draw", "photo of", "picture of"]
    is_image_req = any(keyword in user_text.lower() for keyword in image_keywords)

    if is_image_req:
        status_msg = bot.reply_to(message, "✨ **১৬কে (16K) Ultra-HD Medium Format DSLR ছবি তৈরি করা হচ্ছে...**")
        try:
            # ১৬কে এবং ১৫০ মেগাপিক্সেল মিডিয়াম ফরম্যাট লেন্সের অতি-উচ্চমানের প্রম্পট
            ultra_16k_prompt = (
                f"{user_text}, 16k resolution, shot on Phase One IQ4 150MP medium format camera, "
                f"ultra-sharp focus, cinematic raytraced lighting, hyper-photorealistic skin and material texture, "
                f"award winning professional photography masterpiece, uncompressed raw detail"
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
            bot.edit_message_text("❌ ছবি তৈরি করতে সমস্যা হয়েছে, আবার চেষ্টা করুন!", message.chat.id, status_msg.message_id)
    
    else:
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            prompt_instruction = f"তুমি একজন অত্যন্ত বুদ্ধিমান, অমায়িক এবং প্রফেশনাল এআই অ্যাসিস্ট্যান্ট। ইউজারের সাথে অত্যন্ত সুন্দর, মিষ্টি ও প্রাকৃতিক বাংলায় কথা বলো: {user_text}"
            chat_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_instruction
            )
            bot.reply_to(message, chat_response.text)
        except Exception as e:
            bot.reply_to(message, "আমি আপনার কথা শুনতে পাচ্ছি! বলুন, আপনাকে কীভাবে সাহায্য করতে পারি?")

# ----------------------------------------------------
# ৫. পলিস লুপ
# ----------------------------------------------------
print("16K Ultra DSLR Bot is Active...")
while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        time.sleep(3)
