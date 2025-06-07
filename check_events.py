import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ENV yükle
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

# Etkinlikleri çek
def parse_events():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    etkinlikler = {}
    for li in soup.select("li.hoverable[onclick^='EtkinlikDetayi']"):
        onclick = li.get("onclick", "")
        etkinlik_id = onclick.split("(")[-1].split(")")[0].strip()

        baslik_tag = li.select_one(".desc span")
        saat_tarih = li.select_one(".date")
        if etkinlik_id and baslik_tag and saat_tarih:
            ad = baslik_tag.get_text(strip=True)
            saat = saat_tarih.get_text(strip=True).replace("\n", " ")
            etkinlikler[etkinlik_id] = f"{ad} - {saat}"
    return etkinlikler

# ✔ Ana akış
guncel = parse_events()

# Cache kontrolü
if not os.path.exists(JSON_PATH):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    onceki = json.load(f)

# Farklı etkinlik ID'lerini bul
yeni_eklenenler = {eid: val for eid, val in guncel.items() if eid not in onceki}

# Bildirim
if yeni_eklenenler:
    mesaj = "📆 Yeni Etkinlikler:\n\n" + "\n".join(f"• {val}" for val in yeni_eklenenler.values())
    send_telegram_message(mesaj)
else:
    send_telegram_message("🔁 Yeni etkinlik bulunamadı.")

# Güncel etkinlikleri cache'e yaz
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(guncel, f, ensure_ascii=False, indent=2)

print("✅ Etkinlikler güncellendi ve cache'e yazıldı.")
