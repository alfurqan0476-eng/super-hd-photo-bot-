import os
import time
import urllib.parse
import telebot
from google import genai

# ----------------------------------------------------
# ১. বটের টোকেন কনফিগারেশন
# ----------------------------------------------------
BOT_TOKEN = "8892102480:AAEEqzJzZAwRfYYnhsEUnMse98Hxwq87EeE"
bot = telebot.TeleBot(BOT_TOKEN)

# Gemini AI Client (কথোপকথনের জন্য)
client = genai.Client()

# সেফটি ফিল্টার (অনৈতিক শব্দ ব্লকিং)
BAD_WORDS = [
    "nude", "naked", "undress", "remove clothes", "sex", "strip", "porn",
    "কাপড় খুলি", "উলঙ্গ", "নগ্ন", "কাপড় ছাড়া", "নেংটা"
]

def is_safe_prompt(prompt_text):
    text = prompt_text.lower()
    return not any(word in text for word in BAD_WORDS)

# ----------------------------------------------------
# ২. /start কমান্ড (স্বাগতম জানানো)
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        f"হ্যালো {message.from_user.first_name}! 👋\n\n"
        "আমি আপনার নিজস্ব **AI Assistant**! 🤖✨\n\n"
        "আমার সাথে যেকোনো বিষয় নিয়ে স্বাভাবিকভাবে কথা বলতে বা প্রশ্ন করতে পারেন।\n"
        "আর যদি কোনো ছবি বানাতে চান, তবে শুধু লিখুন (যেমন: *নদীর পাড়ে ছেলে বসে আছে*)—আমি ২-৩ সেকেন্ডে ৪কে রেজুলেশনের এইচডি ছবি বানিয়ে দেব!"
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown")

# ----------------------------------------------------
# ৩. ছবি পেয়ে অ্যানালাইসিস করে মানুষের মত কথা বলা
# ----------------------------------------------------
@bot.message_handler(content_types=['photo'])
def handle_user_photo(message):
    status_msg = bot.reply_to(message, "🤔 ছবিটি দেখছি, একটু দাঁড়ান...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_path = "temp_user_photo.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        caption_prompt = message.caption if message.caption else "এই ছবিটি দেখে খুব সুন্দর ও অমায়িক বাংলায় মানুষের মত কথা বলো এবং ছবিটির মতামত দাও।"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[caption_prompt, image_path]
        )
        
        bot.reply_to(message, response.text)
        bot.delete_message(message.chat.id, status_msg.message_id)
        
        if os.path.exists(image_path):
            os.remove(image_path)
            
    except Exception as e:
        bot.edit_message_text("❌ ছবিটি বুঝতে সমস্যা হয়েছে, আবার চেষ্টা করুন!", message.chat.id, status_msg.message_id)

# ----------------------------------------------------
# ৪. চ্যাটিং ও ফটো জেনারেটর (Main Engine)
# ----------------------------------------------------
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text

    # ১. সেফটি চেক
    if not is_safe_prompt(user_text):
        bot.reply_to(message, "⚠️ **দুঃখিত!** অনৈতিক বা নীতিবহির্ভূত কোনো বিষয় সম্পূর্ণ নিষিদ্ধ।")
        return

    # ২. ইউজার ছবি বানাতে চেয়েছে কি না তা চেক করা
    image_keywords = ["বানাও", "তৈরি কর", "ছবি দাও", "আঁকো", "make image", "generate", "draw", "photo of", "picture of"]
    is_image_req = any(keyword in user_text.lower() for keyword in image_keywords)

    if is_image_req:
        status_msg = bot.reply_to(message, "⚡ **৮কে (8K) Ultra HD ছবি তৈরি করা হচ্ছে...**")
        try:
            ultra_prompt = (
                f"{user_text}, hyperrealistic masterpiece, shot on Hasselblad H6D-100c medium format camera, "
                f"8k resolution, cinematic lighting, ultra sharp focus, realistic skin texture, award winning photography"
            )
                
            encoded_prompt = urllib.parse.quote(ultra_prompt)
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1080&height=1080&model=flux-realism&seed=100&nologo=true"

            bot.send_photo(
                message.chat.id, 
                image_url, 
                caption=f"✨ **আপনার Ultra-HD ছবি রেডি!**\n📝 *প্রম্পট:* {user_text}",
                parse_mode="Markdown"
            )
            bot.delete_message(message.chat.id, status_msg.message_id)
        except Exception as e:
            bot.edit_message_text("❌ ছবি তৈরি করতে সমস্যা হয়েছে!", message.chat.id, status_msg.message_id)
    
    else:
        # ৩. মানুষের মত চ্যাট করার জন্য Gemini AI
        try:
            prompt_instruction = (
                f"তুমি একজন অত্যন্ত বুদ্ধিমান, প্রফেশনাল এবং আন্তরিক এআই অ্যাসিস্ট্যান্ট (Gemini AI-এর মতো)। "
                f"ইউজারের সাথে খুব প্রাঞ্জল, সুন্দর ও বন্ধুত্বপূর্ণ বাংলায় কথোপকথন বা চ্যাট করো: {user_text}"
            )
            chat_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_instruction
            )
            bot.reply_to(message, chat_response.text)
        except Exception as e:
            bot.reply_to(message, "আমি আপনার কথা শুনতে পাচ্ছি! বলুন, আপনাকে কীভাবে সাহায্য করতে পারি?")

# ----------------------------------------------------
# ৫. অল-টাইম এক্টিভ লুপ
# ----------------------------------------------------
print("AI Chat & Photo Bot is Active...")
while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        time.sleep(3)
