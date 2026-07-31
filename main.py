import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from database import init_db
from handlers.start import start_handler
from handlers.users import handle_menu_options
from handlers.deposit import deposit_handler
from handlers.withdraw import withdraw_handler
from handlers.admin import admin_panel, list_users, admin_deposit_callback

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(start_handler)
    app.add_handler(deposit_handler)
    app.add_handler(withdraw_handler)
    app.add_handler(CommandHandler('admin', admin_panel))
    app.add_handler(CommandHandler('users', list_users))
    app.add_handler(CallbackQueryHandler(admin_deposit_callback, pattern='^adm_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_options))

    print("Bot started successfully...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
