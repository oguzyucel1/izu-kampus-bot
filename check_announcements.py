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

def send_file(file_path, caption="📄 Dosya"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": f})

def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

# HTML'den duyuruları çek
def parse_announcements():
    with open(HTML_PATH, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    duyurular = []
    for li in soup.select("ul.announcements li"):
        baslik = normalize(li.get_text())
        duyurular.append(baslik)
    return duyurular

# Ana akış
duyurular_yeni = parse_announcements()

# Cache kontrol
if not os.path.exists(JSON_PATH):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    duyurular_eski = json.load(f)

# Farkları bul
yeni_duyurular = [d for d in duyurular_yeni if d not in duyurular_eski]

if yeni_duyurular:
    mesaj = "📢 Yeni Duyurular:\n\n" + "\n".join(f"• {d}" for d in yeni_duyurular)
    send_telegram_message(mesaj)
else:
    send_telegram_message("🔁 Yeni duyuru bulunamadı.")

# Güncelle ve cache gönder
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(duyurular_yeni, f, ensure_ascii=False, indent=2)
send_file(JSON_PATH, "🧾 Güncel duyurular (cache)")
