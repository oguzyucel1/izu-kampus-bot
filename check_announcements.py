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
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

def parse_announcements():
    with open(HTML_PATH, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    duyurular = []
    for panel in soup.select("div.panel.panel-default"):
        baslik_tag = panel.select_one("a.accordion-toggle")
        if not baslik_tag:
            continue

        # Span içindeki tarihi al
        span = baslik_tag.select_one("span.pull-right")
        tarih = normalize(span.text) if span else ""

        # Span'ı sil, kalan duyuru metni başlık
        if span:
            span.extract()
        duyuru_metni = normalize(baslik_tag.text)

        duyurular.append({"baslik": duyuru_metni, "tarih": tarih})

    return duyurular


# ✔ Yeni duyuruları al ve normalize et
duyurular_yeni = [normalize(d) for d in parse_announcements()]

# JSON yoksa boş oluştur
if not os.path.exists(JSON_PATH):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

# Önceki duyuruları yükle ve normalize et
with open(JSON_PATH, "r", encoding="utf-8") as f:
    duyurular_eski = [normalize(d) for d in json.load(f)]

# Farkları bul
yeni_duyurular = [d for d in duyurular_yeni if d not in duyurular_eski]

# Mesaj gönder
if yeni_duyurular:
    mesaj = "*📢📢 Yeni Duyurular 📢📢*\n\n"

    for duyuru in yeni_duyurular:
        ad = duyuru["baslik"]
        tarih = duyuru["tarih"]

        mesaj += (
            f"📌 Duyuru: {ad}\n"
            f"🗓️ Tarih: {tarih}\n"
            f"📄 Detaylar için sisteme giriş yapabilirsiniz.\n\n"
        )

    send_telegram_message(mesaj)
else:
    send_telegram_message("🔁 Yeni duyuru bulunamadı.")


# Güncel duyuruları JSON'a yaz
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(duyurular_yeni, f, ensure_ascii=False, indent=2)
