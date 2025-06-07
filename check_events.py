import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re

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

def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

# Etkinlikleri HTML'den çek
def parse_events():
    with open(HTML_PATH, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    etkinlikler = {}
    for li in soup.select("li.hoverable[onclick^='EtkinlikDetayi']"):
        onclick = li.get("onclick", "")
        etkinlik_id = onclick.split("(")[-1].split(")")[0].strip()

        span = li.select_one(".desc span")
        date_div = li.select_one(".date")

        if not span or not date_div:
            continue

        full_text = normalize(span.get_text())
        name_tag = span.select_one("i")
        isim = normalize(name_tag.get_text(" ", strip=True)) if name_tag else ""
        if isim:
            full_text = full_text.replace(name_tag.get_text(), "")  # İsmi çıkar

        # Ayır: Saat - Ad
        if "|" in full_text:
            saat, ad = map(str.strip, full_text.split("|", 1))
        else:
            saat, ad = "", full_text

        # Tarih sadece alt satır
        tarih_raw = date_div.get_text("\n", strip=True).split("\n")
        tarih = tarih_raw[1] if len(tarih_raw) > 1 else ""

        # Formatla: Ad - Tarih - Saat - İsim
        sonuc = f"{ad} - {tarih} - {saat}"
        if isim:
            sonuc += f" - {isim}"

        etkinlikler[etkinlik_id] = sonuc

    return etkinlikler

# ✔ Ana akış
guncel = parse_events()

# Cache kontrol
if not os.path.exists(JSON_PATH):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    onceki = json.load(f)

# Farkları bul
yeni_eklenen = {eid: val for eid, val in guncel.items() if eid not in onceki}

# Bildirim
if yeni_eklenen:
    mesaj = "📆 Yeni Etkinlikler:\n\n" + "\n".join(f"• {val}" for val in yeni_eklenen.values())
    send_telegram_message(mesaj)
else:
    send_telegram_message("🔁 Yeni etkinlik bulunamadı.")

# Cache'e güncel veriyi yaz
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(guncel, f, ensure_ascii=False, indent=2)

print("✅ Etkinlikler güncellendi ve cache'e yazıldı.")
