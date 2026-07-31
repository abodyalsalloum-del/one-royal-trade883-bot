from telegram import Update
from telegram.ext import ContextTypes
from database import get_user, set_user_language
from languages import TEXTS


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("يرجى كتابة /start للتسجيل أولاً.")
        return

    lang = user['language']
    text = update.message.text
    t = TEXTS[lang]

    if text in [TEXTS['ar']['btn_profile'], TEXTS['en']['btn_profile']]:
        status_str = "✓ Active" if user['status'] == 'active' else "✗ Inactive (25$ Fee Required)"
        msg = t['profile_info'].format(
            tg_id=user['telegram_id'],
            username=user['username'],
            status=status_str,
            balance=user['balance'],
            created_date=user['created_date']
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text in [TEXTS['ar']['btn_balance'], TEXTS['en']['btn_balance']]:
        await update.message.reply_text(f"{t['btn_balance']}: **${user['balance']:.2f}**", parse_mode="Markdown")

    elif text in [TEXTS['ar']['btn_support'], TEXTS['en']['btn_support']]:
        await update.message.reply_text(t['support_msg'], parse_mode="Markdown")

    elif text in [TEXTS['ar']['btn_settings'], TEXTS['en']['btn_settings']]:
        new_lang = 'en' if lang == 'ar' else 'ar'
        set_user_language(user_id, new_lang)
        await update.message.reply_text(
            f"Switched language to {new_lang.upper()}",
            reply_markup=get_main_keyboard(new_lang)
        )
      
