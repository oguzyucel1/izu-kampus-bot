import json
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HTML_PATH = "home.html"
CACHE_PATH = "onceki_etkinlikler.json"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text.strip())

def parse_events_from_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    etkinlikler = []
    for li in soup.select("li.hoverable"):
        etkinlik = {}
        baslik_div = li.select_one("div.event-baslik")
        detay_divs = li.select("div.event-detaylar > div")

        if not baslik_div or len(detay_divs) < 3:
            continue  # Beklenen yapı yoksa geç

        etkinlik["etkinlik"] = normalize_whitespace(baslik_div.text)

        tarih_div = detay_divs[0]
        try:
            gun_satiri, tarih = map(str.strip, tarih_div.text.strip().split("\n", 1))
            etkinlik["tarih"] = tarih
        except ValueError:
            etkinlik["tarih"] = "Tarih Bilinmiyor"

        saat_div = detay_divs[1]
        etkinlik["saat"] = normalize_whitespace(saat_div.text)

        ogretim_div = detay_divs[2]
        ogretim_text = normalize_whitespace(ogretim_div.text)
        etkinlik["ogretim_uyesi"] = ogretim_text.replace("(", "").replace(")", "")

        etkinlikler.append(etkinlik)
    return etkinlikler

def load_old_events():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_events_to_cache(events):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def compare_events(yeni, eski):
    eski_set = {json.dumps(e, sort_keys=True) for e in eski}
    yeni_set = {json.dumps(e, sort_keys=True) for e in yeni}
    fark = yeni_set - eski_set
    return [json.loads(e) for e in fark]

# 📄 HTML'den etkinlikleri oku
guncel_etkinlikler = parse_events_from_html(HTML_PATH)
eski_etkinlikler = load_old_events()
farkli_etkinlikler = compare_events(guncel_etkinlikler, eski_etkinlikler)

# 🧾 Bildirim gönder
if farkli_etkinlikler:
    mesaj = f"🎯 <b>Yeni Etkinlikler</b> ({datetime.now().strftime('%Y-%m-%d %H:%M')}):\n\n"
    for e in farkli_etkinlikler:
        mesaj += (
            f"📌 <b>{e['etkinlik']}</b>\n"
            f"📅 {e['tarih']}\n"
            f"🕓 {e['saat']}\n"
            f"👨‍🏫 {e['ogretim_uyesi']}\n"
            f"ℹ️ Detaylara sistemden ulaşabilirsiniz.\n\n"
        )
    print(mesaj)
    send_telegram_message(mesaj)
else:
    send_telegram_message("🔁 Yeni etkinlik bulunamadı.")

# 💾 JSON cache güncelle
save_events_to_cache(guncel_etkinlikler)
