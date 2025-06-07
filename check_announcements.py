import json
import re
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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
JSON_PATH = "onceki_duyurular.json"

def run():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Güncel duyuruları HTML'den topla
    yeni_duyurular = []
    for a in soup.select("a.accordion-toggle"):
        baslik = normalize(a.contents[0])
        tarih_span = a.find("span")
        tarih = normalize(tarih_span.get_text()) if tarih_span else ""
        yeni_duyurular.append({"baslik": baslik, "tarih": tarih})

    # İlk defa çalışıyorsa: sadece JSON'a kaydet, bildirim atma
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            onceki_duyurular = json.load(f)
    except FileNotFoundError:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(yeni_duyurular, f, ensure_ascii=False, indent=2)
        print("🟡 İlk çalıştırma: JSON oluşturuldu, bildirim gönderilmedi.")
        return

    # Karşılaştırma
    eski_set = set((d["baslik"], d["tarih"]) for d in onceki_duyurular)
    yeni_set = set((d["baslik"], d["tarih"]) for d in yeni_duyurular)
    farklar = yeni_set - eski_set

    if farklar:
        for baslik, tarih in farklar:
            mesaj = (
                "*📢 Yeni Duyuru:*\n"
                f"📝 {baslik}\n"
                f"📅 {tarih}\n"
                "🔗 Detaylara sistemden ulaşabilirsiniz."
            )
            # Markdown V2 kullanmak istiyorsan parse_mode ekle
            send_telegram_message(mesaj)
    else:
        send_telegram_message("📢 Yeni duyuru bulunamadı.")

    # En sonunda güncel duyuruları kaydet
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(yeni_duyurular, f, ensure_ascii=False, indent=2)

    print(f"✅ Karşılaştırma tamamlandı, {JSON_PATH} güncellendi.")

if __name__ == "__main__":
    run()
