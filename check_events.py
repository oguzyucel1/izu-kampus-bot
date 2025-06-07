import os
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import requests

# ENV yükle
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HTML_PATH = "home.html"
JSON_PATH = "onceki_etkinlikler.json"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

def parse_events_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    etkinlikler = []
    for li in soup.select("ul.feeds > li.hoverable"):
        etkinlik_span = li.select_one(".desc span")
        tarih_div = li.select_one(".date")
        if etkinlik_span and tarih_div:
            etkinlik_text = normalize(etkinlik_span.text)
            saat_kisim = etkinlik_text.split("|")[0].strip()
            ad_kisim = etkinlik_text.split("|")[1].split("(")[0].strip()
            ogretmen_kisim = etkinlik_text.split("(")[-1].split(")")[0].strip() if "(" in etkinlik_text else ""
            gun_satiri, tarih = map(str.strip, tarih_div.text.split("\n"))
            etkinlikler.append({
                "etkinlik": ad_kisim,
                "saat": saat_kisim,
                "tarih": tarih,
                "ogretim_uyesi": ogretmen_kisim
            })
    return etkinlikler

def load_previous_events(json_path):
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_current_events(json_path, events):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def etkinlik_farki_yazdir(yeni_liste, eski_liste):
    eski_set = {json.dumps(e, sort_keys=True) for e in eski_liste}
    farklar = [json.loads(e) for e in {json.dumps(e, sort_keys=True) for e in yeni_liste} - eski_set]
    return farklar

# 1. Parse et
guncel_etkinlikler = parse_events_from_html(HTML_PATH)

# 2. Önceki JSON'dan oku
onceki_etkinlikler = load_previous_events(JSON_PATH)

# 3. Farkları karşılaştır
farkli_etkinlikler = etkinlik_farki_yazdir(guncel_etkinlikler, onceki_etkinlikler)

# 4. Bildirim gönder
if farkli_etkinlikler:
    for e in farkli_etkinlikler:
        mesaj = (
            f"*📢 Yeni Etkinlik*\n"
            f"🎓 *Etkinlik Adı:* {e['etkinlik']}\n"
            f"⏰ *Saat:* {e['saat']}\n"
            f"📅 *Tarih:* {e['tarih']}\n"
            f"👤 *Öğretim Üyesi:* {e['ogretim_uyesi']}\n"
            f"🔗 Detaylara sistemden ulaşabilirsiniz."
        )
        send_telegram_message(mesaj)
else:
    send_telegram_message("📭 Yeni etkinlik bulunamadı.")

# 5. JSON'u güncelle
save_current_events(JSON_PATH, guncel_etkinlikler)
