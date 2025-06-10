import os
import json
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ENV
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HTML_PATH = "home.html"
CACHE_DIR = ".cache"
JSON_PATH = os.path.join(CACHE_DIR, "onceki_duyurular.json")

# Telegram mesajı gönder
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

# Boşluk normalize
def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

# HTML'den duyuruları çek
def parse_announcements():
    with open(HTML_PATH, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    duyurular = []
    for panel in soup.select("div.panel.panel-default"):
        baslik_tag = panel.select_one("a.accordion-toggle")
        if not baslik_tag:
            continue

        # Tarihi <span> içinden al
        span = baslik_tag.select_one("span.pull-right")
        tarih = normalize(span.text) if span else ""

        # Tarihi içeren span'ı sil
        if span:
            span.extract()

        # Geriye kalan metin: başlık
        baslik = normalize(baslik_tag.text)
        duyurular.append({
            "baslik": baslik,
            "tarih": tarih
        })

    return duyurular

# ✔ Ana akış
duyurular_yeni = parse_announcements()

# JSON yoksa boş oluştur
if not os.path.exists(JSON_PATH):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

# Öncekileri yükle
with open(JSON_PATH, "r", encoding="utf-8") as f:
    duyurular_eski = json.load(f)

# Farkları bul (dict olarak karşılaştır)
yeni_duyurular = [d for d in duyurular_yeni if d not in duyurular_eski]

# Mesaj oluştur
if yeni_duyurular:
    mesaj = "*📢 Yeni Duyurular*\n\n"
    for d in yeni_duyurular:
        mesaj += (
            f"📌 Duyuru: {d['baslik']}\n"
            f"🗓️ Tarih: {d['tarih']}\n"
            f"📄 Detaylar için sisteme giriş yapabilirsiniz.\n\n"
        )
    send_telegram_message(mesaj)
else:
    send_telegram_message("🔁 Yeni duyuru bulunamadı.")

# Güncel cache'i yaz
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(duyurular_yeni, f, ensure_ascii=False, indent=2)

print("✅ Duyurular güncellendi ve cache'e yazıldı.")
