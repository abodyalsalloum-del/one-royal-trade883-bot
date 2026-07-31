import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

REGISTRATION_FEE = 25.0

PAYMENT_METHODS = {
    "USDT (TRC20)": "يرجى التواصل مع الأدمن للحصول على عنوان المحفظة",
    "Wish Money": "يرجى التواصل مع الأدمن للحصول على بيانات التحويل",
    "ShamCash": "يرجى التواصل مع الأدمن للحصول على بيانات التحويل",
    "تحويل مباشر": "يرجى التواصل مع الأدمن للتنسيق"
}
