from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard(lang='ar'):
    if lang == 'en':
        keyboard = [
            [KeyboardButton("👤 Profile"), KeyboardButton("💰 Balance")],
            [KeyboardButton("🛠 Support"), KeyboardButton("⚙️ Settings")]
        ]
    else:
        keyboard = [
            [KeyboardButton("👤 الملف الشخصي"), KeyboardButton("💰 الرصيد")],
            [KeyboardButton("🛠 الدعم"), KeyboardButton("⚙️ الإعدادات")]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
  
