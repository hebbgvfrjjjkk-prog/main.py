import telebot
import os

# ضع التوكن الخاص بك هنا بين العلامتين
API_TOKEN = '8119352317:AAEhw1uSzkKozmyMntC1WpshIln49W3uvmY'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أنا بوت التزييف العميق، أرسل لي صورة لأبدأ العمل.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "وصلت رسالتك، سأقوم بمعالجتها قريباً.")

# تشغيل البوت
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
