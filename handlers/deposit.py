from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from database import get_user, add_transaction
from languages import TEXTS
from config import PAYMENT_METHODS, ADMIN_ID

DEP_METHOD, DEP_AMOUNT = range(2)

async def deposit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user:
        return ConversationHandler.END
    lang = user['language']
    keyboard = []
    for method in PAYMENT_METHODS.keys():
        keyboard.append([InlineKeyboardButton(method, callback_data=f"dep_{method}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(TEXTS[lang]['deposit_select'], reply_markup=reply_markup)
    return DEP_METHOD

async def deposit_method_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = query.data.replace("dep_", "")
    context.user_data['dep_method'] = method
    user = get_user(update.effective_user.id)
    lang = user['language']
    details = PAYMENT_METHODS.get(method, "")
    await query.edit_message_text(
        f"**{method}**\nDetails:\n`{details}`\n\n" + TEXTS[lang]['deposit_amount'], 
        parse_mode="Markdown"
    )
    return DEP_AMOUNT

async def deposit_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    lang = user['language']
    try:
        amount = float(update.message.text.strip())
        if amount <= 0:
            raise ValueError()
    except ValueError:
        await update.message.reply_text("Invalid amount. Enter a valid number.")
        return DEP_AMOUNT

    method = context.user_data['dep_method']
    tx_id = add_transaction(user['telegram_id'], 'deposit', amount, method)
    await update.message.reply_text(TEXTS[lang]['deposit_sent'].format(amount=amount))

    admin_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("قبول (Approve)", callback_data=f"adm_app_dep_{tx_id}"),
            InlineKeyboardButton("رفض (Reject)", callback_data=f"adm_rej_dep_{tx_id}")
        ]
    ])
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"**طلب إيداع جديد #{tx_id}**\n"
             f"User: @{user['username']} ({user['telegram_id']})\n"
             f"Amount: ${amount}\n"
             f"Method: {method}\n"
             f"Account Status: {user['status']}",
        reply_markup=admin_kb,
        parse_mode="Markdown"
    )
    return ConversationHandler.END

deposit_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(r'^(الإيداع|Deposit)$'), deposit_start)
    ],
    states={
        DEP_METHOD: [CallbackQueryHandler(deposit_method_selected, pattern='^dep_')],
        DEP_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deposit_amount_received)]
    },
    fallbacks=[]
  )
