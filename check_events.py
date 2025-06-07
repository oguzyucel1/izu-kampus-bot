import os
import json
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

# Telegram'a mesaj gönder
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

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
                baslik = baslik_span.get_text(strip=True)
                tarih = tarih_div.get_text(strip=True).replace("\n", " ")
                etkinlik = f"{tarih} | {baslik}"
                etkinlikler.append(etkinlik)
        except Exception as e:
            print("Etkinlik parse hatası:", e)

    return etkinlikler

# ✔ Ana akış
guncel_etkinlikler = parse_events()

# Cache yoksa oluştur
if not os.path.exists(JSON_PATH):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

# Önceki etkinlikleri yükle
with open(JSON_PATH, "r", encoding="utf-8") as f:
    onceki_etkinlikler = json.load(f)

# Farkları karşılaştır
farklar = [e for e in guncel_etkinlikler if e not in onceki_etkinlikler]

if farklar:
    mesaj = "📆 Yeni Etkinlikler:\n\n" + "\n".join(f"• {e}" for e in farklar)
    send_telegram_message(mesaj)
else:
    send_telegram_message("🔁 Yeni etkinlik bulunamadı.")

# Güncel etkinlikleri JSON cache'e yaz
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(guncel_etkinlikler, f, ensure_ascii=False, indent=2)

print("✅ Etkinlikler güncellendi ve cache'e yazıldı.")
