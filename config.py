import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

REGISTRATION_FEE = 25.0

PAYMENT_METHODS = {
    "USDT TRC20": "YourUsdtTrc20WalletAddressHere...",
    "ShamCash": "Account #12345678",
    "Wish Money": "+961XXXXXXXX",
    "Western Union": "Name: John Doe, Country: Lebanon",
    "Office Transfer": "Contact Admin @support_username"
}
