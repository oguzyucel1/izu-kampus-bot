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
JSON_PATH = "onceki_etkinlikler.json"

def run():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # HTML'den etkinlik verilerini çıkar
    yeni_etkinlikler = []
    for li in soup.select("li.hoverable"):
        try:
            span = li.select_one("div.desc > span")
            raw_text = normalize(span.contents[0])
            saat, etkinlik_adi = raw_text.split("|", 1)
            saat = normalize(saat)
            etkinlik_adi = normalize(etkinlik_adi)
            ogretim_uyesi = normalize(span.find("i").get_text().strip("()"))
            tarih_raw = li.select_one("div.date").get_text(separator="\n").strip().split("\n")[-1]
            tarih = normalize(tarih_raw)

            yeni_etkinlikler.append({
                "etkinlik": etkinlik_adi,
                "saat": saat,
                "tarih": tarih,
                "ogretim_uyesi": ogretim_uyesi
            })
        except Exception:
            continue

    # JSON dosyası yoksa ilk defa çalışıyordur
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            onceki_etkinlikler = json.load(f)
    except FileNotFoundError:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(yeni_etkinlikler, f, ensure_ascii=False, indent=2)
        print("🟡 İlk çalıştırma: JSON oluşturuldu, bildirim gönderilmedi.")
        return

    # Karşılaştırma
    eski_set = set((e["etkinlik"], e["saat"], e["tarih"], e["ogretim_uyesi"]) for e in onceki_etkinlikler)
    yeni_set = set((e["etkinlik"], e["saat"], e["tarih"], e["ogretim_uyesi"]) for e in yeni_etkinlikler)
    farklar = yeni_set - eski_set

    if farklar:
        for etkinlik, saat, tarih, hoca in farklar:
            mesaj = (
                "*🎉 Yeni Etkinlik:*\n"
                f"📝 {etkinlik}\n"
                f"⏰ {tarih} | {saat}\n"
                f"👤 {hoca}\n"
                "🔗 Detaylara sistemden ulaşabilirsiniz."
            )
            send_telegram_message(mesaj)
    else:
        send_telegram_message("🎉 Yeni etkinlik bulunamadı.")

    # En son JSON'u güncelle
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(yeni_etkinlikler, f, ensure_ascii=False, indent=2)

    print(f"✅ Karşılaştırma tamamlandı, {JSON_PATH} güncellendi.")

if __name__ == "__main__":
    run()
