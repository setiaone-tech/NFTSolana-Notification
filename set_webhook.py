import requests

#Token API Telegram BOT
TOKEN = ""
#Your Website for Webhhook
WEBHOOK_URL = "{url}/webhook"

requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
