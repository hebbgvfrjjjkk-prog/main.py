import telebot
import replicate
import os

# --- الإعدادات المدمجة ---
CHIP_TOKEN = "8119352317:AAEhw1uSzkKozmyMntC1WpshIln49W3uvmY"
MY_CHAT_ID = 6007579460

# ⚠️ يجب عليك وضع مفتاح Replicate الخاص بك هنا لكي يعمل تحويل الوجوه
REPLICATE_API_TOKEN = "ضع_هنا_مفتاح_REPLICATE_الخاص_بك" 

# إعداد البوت والبيئة
bot = telebot.TeleBot(CHIP_TOKEN)
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # التحقق من أن المستخدم هو صاحب الأيدي المسموح له فقط
    if message.chat.id != MY_CHAT_ID:
        bot.reply_to(message, "⚠️ عذراً، هذا البوت مخصص للمطور فقط.")
        return
    bot.reply_to(message, "أهلاً بك يا مطور! أرسل الآن **صورة الوجه** (Source Image) التي تريد تركيبها.")

@bot.message_handler(content_types=['photo'])
def handle_face_image(message):
    if message.chat.id != MY_CHAT_ID: 
        return
        
    file_info = bot.get_file(message.photo[-1].file_id)
    file_url = f"https://api.telegram.org/file/bot{CHIP_TOKEN}/{file_info.file_path}"
    
    user_states[message.chat.id] = {'source_image': file_url}
    bot.reply_to(message, "✅ تم استلام صورة الوجه بنجاح.\nالآن أرسل **مقطع الفيديو** (Target Video) المراد العمل عليه.")

@bot.message_handler(content_types=['video'])
def handle_target_video(message):
    chat_id = message.chat.id
    if chat_id != MY_CHAT_ID: 
        return
        
    if chat_id not in user_states:
        bot.reply_to(message, "❌ من فضلك أرسل صورة الوجه أولاً قبل إرسال الفيديو.")
        return
    
    file_info = bot.get_file(message.video.file_id)
    video_url = f"https://api.telegram.org/file/bot{CHIP_TOKEN}/{file_info.file_path}"
    
    bot.send_message(chat_id, "⏳ جاري المعالجة بواسطة الذكاء الاصطناعي... قد يستغرق الأمر دقيقة.")

    try:
        # استدعاء نموذج FaceFusion عبر Replicate
        output = replicate.run(
            "lucataco/facefusion:97f39420-94e8-4660-8f64-4670-349f285d0e2e",
            input={
                "target_video": video_url,
                "source_image": user_states[chat_id]['source_image'],
                "face_detector_model": "retinaface",
                "face_swapper_model": "inswapper_128",
                "face_enhancer_model": "gfpgan_1.4"
            }
        )
        
        if output:
            bot.send_video(chat_id, output, caption="تم دمج الوجه بنجاح! 🔥")
        else:
            bot.send_message(chat_id, "❌ حدث خطأ أثناء المعالجة، لم يتم إنتاج فيديو.")
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ فني:\n{str(e)}")

# تشغيل البوت
print("البوت يعمل الآن...")
bot.polling()
