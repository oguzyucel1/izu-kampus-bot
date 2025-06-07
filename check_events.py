import json
from bs4 import BeautifulSoup
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

# Yol tanımları
HTML_PATH = "home.html"
JSON_PATH = "onceki_etkinlikler.json"

# .env dosyasından bot bilgilerini al
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Telegram mesaj fonksiyonları
def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

def send_file(file_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": f})

# HTML'den etkinlikleri ayrıştır
def parse_events(html_path):
    with open(html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    etkinlikler = []
    for li in soup.select("li.hoverable"):
        try:
            detay_span = li.select_one(".content-col2 .desc span")
            date_div = li.select_one(".col2 .date")
            if detay_span and date_div:
                saat_ve_ad = detay_span.text.strip().split("|")
                etkinlik = saat_ve_ad[1].strip() if len(saat_ve_ad) > 1 else "Etkinlik Bilgisi Yok"
                saat = saat_ve_ad[0].strip() if len(saat_ve_ad) > 1 else ""
                ogretim_uyesi = detay_span.find("i").text.strip("()") if detay_span.find("i") else ""
                tarih_satiri = date_div.text.strip().split("\n")
                tarih = tarih_satiri[1].strip() if len(tarih_satiri) > 1 else ""
                etkinlikler.append({
                    "etkinlik": etkinlik,
                    "saat": saat,
                    "tarih": tarih,
                    "ogretim_uyesi": ogretim_uyesi
                })
        except Exception as e:
            print(f"[!] Hata: {e}")
    return etkinlikler

# Önceki verileri oku
def load_previous_data():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Farkları bul
def find_new_events(guncel, onceki):
    onceki_set = {(e["etkinlik"], e["saat"], e["tarih"], e["ogretim_uyesi"]) for e in onceki}
    return [e for e in guncel if (e["etkinlik"], e["saat"], e["tarih"], e["ogretim_uyesi"]) not in onceki_set]

# === ANA AKIŞ ===
guncel_etkinlikler = parse_events(HTML_PATH)
onceki_etkinlikler = load_previous_data()
yeni_etkinlikler = find_new_events(guncel_etkinlikler, onceki_etkinlikler)

if yeni_etkinlikler:
    mesaj = f"<b>📣 Yeni Etkinlikler ({datetime.now().strftime('%d.%m.%Y %H:%M')})</b>\n\n"
    for e in yeni_etkinlikler:
        mesaj += (
            f"🔸 <b>{e['etkinlik']}</b>\n"
            f"⏰ {e['saat']}\n"
            f"📅 {e['tarih']}\n"
            f"👤 {e['ogretim_uyesi']}\n"
            f"📎 Detaylara sistemden ulaşabilirsiniz\n\n"
        )
    send_message(mesaj)
    print("[+] Yeni etkinlikler bulundu, mesaj gönderildi.")
else:
    send_message("🔁 Yeni etkinlik bulunamadı.")
    print("[=] Yeni etkinlik yok.")

# Her durumda güncel veriyi kaydet
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(guncel_etkinlikler, f, ensure_ascii=False, indent=2)
print(f"[✓] JSON güncellendi: {JSON_PATH}")
