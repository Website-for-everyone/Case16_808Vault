import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8217851677:AAHN34TMuC1P4e6SppuazFN8BIiLHa_RyIc")
TELEGRAM_OWNER_ID = int(os.getenv("TELEGRAM_OWNER_ID", "1387913438"))
TELEGRAM_OWNER_USERNAME = os.getenv("TELEGRAM_OWNER_USERNAME", "@Idrisov_prod")
API_PORT = int(os.getenv("API_PORT", "8016"))
