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
JSON_PATH = os.path.join(CACHE_DIR, "onceki_duyurular.json")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

# ✅ Yeni: HTML'den duyuruları doğru şekilde çek
def parse_announcements():
    with open(HTML_PATH, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    duyurular = []
    for panel in soup.select("div.panel.panel-default"):
        baslik_tag = panel.select_one("a.accordion-toggle")
        if baslik_tag:
            duyuru_metni = normalize(baslik_tag.text)
            duyurular.append(duyuru_metni)
    return duyurular

# ✔ Ana akış
duyurular_yeni = parse_announcements()

# JSON yoksa boş oluştur
if not os.path.exists(JSON_PATH):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

# Eski JSON'u oku
with open(JSON_PATH, "r", encoding="utf-8") as f:
    duyurular_eski = json.load(f)

# Farklıları bul
yeni_duyurular = [d for d in duyurular_yeni if d not in duyurular_eski]

# Telegram’a gönder ve JSON’u güncelle
if yeni_duyurular:
    mesaj = "📢 Yeni Duyurular:\n\n" + "\n".join(f"• {d}" for d in yeni_duyurular)
    send_telegram_message(mesaj)
else:
    send_telegram_message("🔁 Yeni duyuru bulunamadı.")

# Cache’e yaz
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(duyurular_yeni, f, ensure_ascii=False, indent=2)
