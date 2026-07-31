from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID, REGISTRATION_FEE
from database import (
    get_transaction, update_transaction_status,
    get_user, update_user_status, update_user_balance, get_all_users
)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = get_all_users()
    msg = f"**لوحة التحكم والإدارة**\nإجمالي المستخدمين: {len(users)}\n\nالأوامر المتاحة:\nعرض قائمة المستخدمين: /users"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = get_all_users()
    text = "**قائمة المستخدمين:**\n"
    for u in users:
        text += f"ID: {u[0]} | @{u[1]} | الرصيد: ${u[2]} | الحالة: {u[3]}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def admin_deposit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("غير مسموح", show_alert=True)
        return
    await query.answer()

    data = query.data
    if data.startswith("adm_app_dep_"):
        tx_id = int(data.replace("adm_app_dep_", ""))
        tx = get_transaction(tx_id)
        if tx and tx['status'] == 'pending':
            update_transaction_status(tx_id, 'approved')
            user = get_user(tx['telegram_id'])
            deposit_amount = tx['amount']

            if user['status'] == 'inactive':
                update_user_status(user['telegram_id'], 'active')
                credit_amount = max(0.0, deposit_amount - REGISTRATION_FEE)
                update_user_balance(user['telegram_id'], credit_amount)
                await context.bot.send_message(
                    chat_id=user['telegram_id'],
                    text=f"تم قبول الإيداع وتفعيل حسابك بنجاح!\nمبلغ الإيداع: ${deposit_amount}\nرسوم التفعيل المقتطعة: ${REGISTRATION_FEE}\nالمضاف لرصيدك: ${credit_amount}"
                )
            else:
                update_user_balance(user['telegram_id'], deposit_amount)
                await context.bot.send_message(
                    chat_id=user['telegram_id'],
                    text=f"تم قبول إيداعك بقيمة ${deposit_amount} بنجاح!"
                )
            await query.edit_message_text(f"تم قبول الطلب #{tx_id} بنجاح.")

    elif data.startswith("adm_rej_dep_"):
        tx_id = int(data.replace("adm_rej_dep_", ""))
        tx = get_transaction(tx_id)
        if tx and tx['status'] == 'pending':
            update_transaction_status(tx_id, 'rejected')
            await context.bot.send_message(
                chat_id=tx['telegram_id'],
                text=f"تم رفض طلب الإيداع #{tx_id}."
            )
            await query.edit_message_text(f"تم رفض الطلب #{tx_id}.")
          
