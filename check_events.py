import os
import json
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
HTML_PATH = "home.html"
CACHE_DIR = ".cache"
JSON_PATH = os.path.join(CACHE_DIR, "onceki_etkinlikler.json")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

def send_file(path, caption="📄 Dosya"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(path, "rb") as f:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": f})

def parse_events():
    with open(HTML_PATH, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    etkinlikler = []
    for li in soup.select("ul.events li"):
        etkinlik = re.sub(r"\s+", " ", li.get_text().strip())
        etkinlikler.append(etkinlik)
    return etkinlikler

# Etkinlik verisini al
guncel = parse_events()

# Cache kontrol
if not os.path.exists(JSON_PATH):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    onceki = json.load(f)

farklar = [e for e in guncel if e not in onceki]

if farklar:
    mesaj = "📆 Yeni Etkinlikler:\n\n" + "\n".join(f"• {e}" for e in farklar)
    send_telegram_message(mesaj)
else:
    send_telegram_message("🔁 Yeni etkinlik bulunamadı.")


