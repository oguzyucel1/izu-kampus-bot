import json
import re
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN veya CHAT_ID eksik")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
        if resp.status_code != 200:
            print(f"Telegram mesajı gönderilemedi: {resp.text}")
    except Exception as e:
        print(f"Telegram hatası: {e}")

def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

HTML_PATH = "home.html"
JSON_PATH = "onceki_etkinlikler.json"

def run():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    yeni_etkinlikler = []
    for li in soup.select("li.hoverable"):
        try:
            span = li.select_one("div.desc > span")

            # Etkinlik adı ve saat | kısmını ayır
            etkinlik_raw = span.contents[0]
            saat, ad = etkinlik_raw.split("|", 1)
            saat = normalize(saat)
            etkinlik_adi = normalize(ad)

            # <i> içinden öğretim üyesini al, parantezleri temizle
            ogretim_uyesi_raw = span.find("i").get_text()
            ogretim_uyesi = normalize(ogretim_uyesi_raw.strip("()"))

            # Tarihi al
            tarih_raw = li.select_one("div.date").get_text(separator="\n").strip().split("\n")[-1]
            tarih = normalize(tarih_raw)

            yeni_etkinlikler.append({
                "etkinlik": etkinlik_adi,
                "saat": saat,
                "tarih": tarih,
                "ogretim_uyesi": ogretim_uyesi
            })
        except Exception as e:
            print("❌ Etkinlik ayrıştırma hatası:", e)
            continue

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            onceki_etkinlikler = json.load(f)
    except FileNotFoundError:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(yeni_etkinlikler, f, ensure_ascii=False, indent=2)
        return

    eski_set = set((e["etkinlik"], e["tarih"]) for e in onceki_etkinlikler)
    yeni_set = set((e["etkinlik"], e["tarih"]) for e in yeni_etkinlikler)
    farklar = yeni_set - eski_set

    if farklar:
        for etkinlik, tarih in farklar:
            detay = next(
                (e for e in yeni_etkinlikler if e["etkinlik"] == etkinlik and e["tarih"] == tarih),
                None
            )
            if detay:
                mesaj = (
                    "📅  Yeni Etkinlik:\n"
                    f"📝 Etkinlik Adı: {detay['etkinlik']}\n"
                    f"⏱️ Tarih ve Saat: {detay['tarih']} | {detay['saat']}\n"
                    f"👤 Öğretim Görevlisi: {detay['ogretim_uyesi']}\n"
                    "🔗 Detaylara sistemden ulaşabilirsiniz."
                )
                send_telegram_message(mesaj)
    else:
        send_telegram_message("📅 Yeni etkinlik bulunamadı.")

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(yeni_etkinlikler, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run()
