import os
import json
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

# ENV değişkenlerini yükle
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HTML_PATH = "home.html"
JSON_PATH = "onceki_etkinlikler.json"

# Telegram mesaj gönderici
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# Boşlukları normalize et
def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text.strip())

# HTML'den etkinlikleri çek
with open(HTML_PATH, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

etkinlik_listesi = []
li_etiketleri = soup.select("ul.feeds li.hoverable")

for li in li_etiketleri:
    saat_baslik_ogretmen_tag = li.select_one("div.content-col2 span[style*='color: #717171']")
    tarih_tag = li.select_one("div.date")

    if not saat_baslik_ogretmen_tag or not tarih_tag:
        continue

    ham_text = normalize_whitespace(saat_baslik_ogretmen_tag.get_text())
    tarih_text = normalize_whitespace(tarih_tag.get_text(separator="|"))

    match = re.match(r"(.*?)\s*\|\s*(.*?)\s*\((.*?)\)", ham_text)
    if not match:
        continue

    saat = match.group(1).strip()
    etkinlik_adi = match.group(2).strip()
    ogr_uyesi = match.group(3).strip()

    tarih_split = tarih_text.split("|")
    etkinlik_tarihi = tarih_split[1].strip() if len(tarih_split) > 1 else "Tarih yok"

    kimlik = f"{etkinlik_adi} | {saat} | {ogr_uyesi} | {etkinlik_tarihi}"
    etkinlik_listesi.append(kimlik)

# JSON var mı kontrol et
ilk_calisma = not os.path.exists(JSON_PATH)

# İlk çalıştırmadaysa JSON'u sadece kaydet
if ilk_calisma:
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(etkinlik_listesi, f, ensure_ascii=False, indent=2)
    print("🆕 İlk çalıştırma, etkinlikler kaydedildi ama Telegram mesajı atılmadı.")
else:
    # Eski kayıtları yükle
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        onceki_kayitlar = json.load(f)

    # Farkları bul
    yeni_etkinlikler = [
        k for k in etkinlik_listesi
        if normalize_whitespace(k) not in [normalize_whitespace(e) for e in onceki_kayitlar]
    ]

    # Bildirim gönder
    if yeni_etkinlikler:
        for k in yeni_etkinlikler:
            try:
                etkinlik_adi, saat, ogr_uyesi, etkinlik_tarihi = [par.strip() for par in k.split("|")]
            except ValueError:
                continue

            mesaj = (
                f"📢 Yeni etkinlik: {etkinlik_adi}\n"
                f"🕒 Tarih: {etkinlik_tarihi} | {saat}\n"
                f"👤 Öğretim Üyesi: {ogr_uyesi}\n"
                f"📌 Detaylara sistemden ulaşabilirsiniz."
            )
            send_telegram_message(mesaj)
    else:
        send_telegram_message("🔔 Yeni etkinlik bulunamadı.")

    # JSON'u güncelle
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(etkinlik_listesi, f, ensure_ascii=False, indent=2)
