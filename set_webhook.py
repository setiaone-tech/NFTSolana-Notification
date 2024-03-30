import requests

TOKEN = "5553337166:AAF1y4oHltscYMjSyr6UlQ5BpxjmxNpza9o"  # Ganti dengan token bot Anda
WEBHOOK_URL = "https://calamity94.masuk.id/webhook"

requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")