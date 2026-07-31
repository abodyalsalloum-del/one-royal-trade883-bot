from telegram import Update
from telegram.ext import ContextTypes
from database import get_user, set_user_language
from languages import TEXTS
from keyboards import get_main_keyboard

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("يرجى كتابة /start أولاً أو التسجيل.")
        return

    lang = user['language']
    text = update.message.text
    t = TEXTS[lang]

    if text in [TEXTS['ar']['btn_profile'], TEXTS['en']['btn_profile']]:
        status_str = "✔️ Active" if user['status'] == 'active' else "Inactive"
        msg = t['profile_info'].format(
            tg_id=user['telegram_id'],
            username=user['username'],
            status=status_str,
            balance=user['balance'],
            created_date=user['created_date']
        )
        await update.message.reply_text(msg, parse_mode="HTML")

    elif text in [TEXTS['ar']['btn_settings'], TEXTS['en']['btn_settings']]:
        new_lang = 'en' if lang == 'ar' else 'ar'
        set_user_language(user_id, new_lang)
        await update.message.reply_text(
            f"Switched language to {new_lang.upper()}",
            reply_markup=get_main_keyboard(new_lang)
        )
        
