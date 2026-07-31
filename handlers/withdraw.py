from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database import get_user, add_transaction
from languages import TEXTS
from config import ADMIN_ID

WITH_AMOUNT, WITH_DETAILS = range(2)

async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user:
        return ConversationHandler.END
    lang = user['language']
    if user['status'] != 'active':
        await update.message.reply_text(TEXTS[lang]['account_inactive_warning'], parse_mode="Markdown")
        return ConversationHandler.END
    
    await update.message.reply_text(TEXTS[lang]['withdraw_amount'])
    return WITH_AMOUNT

async def withdraw_amount_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    lang = user['language']
    try:
        amount = float(update.message.text.strip())
        if amount <= 0 or amount > user['balance']:
            await update.message.reply_text(TEXTS[lang]['insufficient_balance'])
            return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Invalid amount.")
        return WITH_AMOUNT

    context.user_data['with_amount'] = amount
    await update.message.reply_text(TEXTS[lang]['withdraw_method'])
    return WITH_DETAILS

async def withdraw_details_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    lang = user['language']
    details = update.message.text.strip()
    amount = context.user_data['with_amount']

    tx_id = add_transaction(user['telegram_id'], 'withdraw', amount, details)
    await update.message.reply_text(TEXTS[lang]['withdraw_sent'])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"**طلب سحب جديد #{tx_id}**\n"
             f"User: @{user['username']} ({user['telegram_id']})\n"
             f"Amount: ${amount}\n"
             f"Details: {details}",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

withdraw_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(r'^(ATM السحب|ATM Withdraw)$'), withdraw_start)
    ],
    states={
        WITH_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_amount_step)],
        WITH_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_details_step)]
    },
    fallbacks=[]
)
