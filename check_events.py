import os
import json
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ENV değişkenlerini yükle
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Dosya yolları
HTML_PATH = "home.html"
CACHE_DIR = ".cache"
JSON_PATH = os.path.join(CACHE_DIR, "onceki_etkinlikler.json")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

# Etkinlikleri HTML'den çek
def parse_events():
    with open(HTML_PATH, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    etkinlikler = []
    for li in soup.select("ul.feeds li.hoverable"):
        try:
            baslik_span = li.select_one(".desc span")
            tarih_div = li.select_one(".date")
            if baslik_span and tarih_div:
                baslik = normalize(baslik_span.get_text())
                tarih = normalize(tarih_div.get_text().replace("\n", " "))
                etkinlik = f"{tarih} | {baslik}"
                etkinlikler.append(etkinlik)
        except Exception as e:
            print("Etkinlik parse hatası:", e)

    return etkinlikler

# ✔ Ana akış
guncel_etkinlikler = [normalize(e) for e in parse_events()]

# Eğer JSON dosyası yoksa oluştur
if not os.path.exists(JSON_PATH):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

# Önceki etkinlikleri yükle ve normalize et
with open(JSON_PATH, "r", encoding="utf-8") as f:
    onceki_etkinlikler = [normalize(e) for e in json.load(f)]

# Farkları bul
farklar = [e for e in guncel_etkinlikler if e not in onceki_etkinlikler]

# Bildirim gönder
if farklar:
    mesaj = "📆 Yeni Etkinlikler:\n\n" + "\n".join(f"• {e}" for e in farklar)
    send_telegram_message(mesaj)
else:
    send_telegram_message("🔁 Yeni etkinlik bulunamadı.")

# Güncel verileri JSON olarak kaydet
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(guncel_etkinlikler, f, ensure_ascii=False, indent=2)

print("✅ Etkinlikler güncellendi ve cache'e yazıldı.")
