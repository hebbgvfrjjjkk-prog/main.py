import telebot
import replicate
import os

# الإعدادات
CHIP_TOKEN = "8119352317:AAEhw1uSzkKozmyMntC1WpshIln49W3uvmY"
MY_CHAT_ID = 6007579460
REPLICATE_API_TOKEN = "r8_وضع_المفتاح_هنا" # <--- لا تنسى استبدال هذا

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
bot = telebot.TeleBot(CHIP_TOKEN)

user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id != MY_CHAT_ID:
        bot.reply_to(message, "⚠️ البوت خاص بالمطور فقط.")
        return
    bot.reply_to(message, "أهلاً بك! أرسل **صورة الوجه** أولاً.")

@bot.message_handler(content_types=['photo'])
def handle_face_image(message):
    if message.chat.id != MY_CHAT_ID: return
    file_info = bot.get_file(message.photo[-1].file_id)
    file_url = f"https://api.telegram.org/file/bot{CHIP_TOKEN}/{file_info.file_path}"
    user_states[message.chat.id] = {'source_image': file_url}
    bot.reply_to(message, "✅ تم حفظ الوجه. أرسل الآن **الفيديو**.")

@bot.message_handler(content_types=['video'])
def handle_target_video(message):
    chat_id = message.chat.id
    if chat_id != MY_CHAT_ID or chat_id not in user_states: return
    
    file_info = bot.get_file(message.video.file_id)
    video_url = f"https://api.telegram.org/file/bot{CHIP_TOKEN}/{file_info.file_path}"
    bot.send_message(chat_id, "⏳ جاري المعالجة... انتظر قليلاً.")

    try:
        output = replicate.run(
            "lucataco/facefusion:97f39420-94e8-4660-8f64-4670-349f285d0e2e",
            input={
                "target_video": video_url,
                "source_image": user_states[chat_id]['source_image'],
            }
        )
        bot.send_video(chat_id, output, caption="تم الدمج بنجاح! 🔥")
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ: {str(e)}")

bot.polling()
