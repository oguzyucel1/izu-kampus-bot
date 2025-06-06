import os
import json
import re
import sys
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

# ENV
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HTML_PATH = "home.html"
JSON_PATH = "onceki_duyurular.json"

# 🧼 Metin temizleyici
def temizle_metin(metin):
    return re.sub(r'\s+', ' ', metin).strip()

def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        response = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Telegram mesaj hatası: {e}")
        sys.exit(1)

try:
    # Sayfayı oku
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
except Exception as e:
    print(f"❌ HTML dosyası okunamadı: {e}")
    sys.exit(1)

duyurular = []
try:
    duyuru_divleri = soup.select("div.panel.panel-default")
    for panel in duyuru_divleri:
        title_tag = panel.select_one("h3.panel-title a")
        if title_tag:
            tarih_tag = title_tag.select_one("span.pull-right")
            tarih = temizle_metin(tarih_tag.get_text()) if tarih_tag else ""
            for span in title_tag.select("span"):
                span.extract()
            baslik = temizle_metin(title_tag.get_text())
            duyuru_kimligi = f"{baslik} | {tarih}"
            duyurular.append(duyuru_kimligi)
except Exception as e:
    print(f"❌ Duyuru ayrıştırma hatası: {e}")
    sys.exit(1)

# Eski duyuruları yükle
try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        onceki_duyurular = json.load(f)
except FileNotFoundError:
    onceki_duyurular = []
except Exception as e:
    print(f"❌ JSON okuma hatası: {e}")
    sys.exit(1)

# Normalize ederek karşılaştır
try:
    yeni_duyurular = [
        d for d in duyurular
        if temizle_metin(d) not in [temizle_metin(e) for e in onceki_duyurular]
    ]
except Exception as e:
    print(f"❌ Karşılaştırma hatası: {e}")
    sys.exit(1)

# Bildirim gönder
try:
    if yeni_duyurular:
        for duyuru in yeni_duyurular:
            try:
                baslik, tarih = duyuru.split("|")
            except ValueError:
                baslik, tarih = duyuru, "Tarih yok"
            mesaj = f"📢 Yeni duyuru: {baslik.strip()}\n📅 Tarih: {tarih.strip()}\n📌 Detaylara sistemden ulaşabilirsiniz."
            send_telegram_message(mesaj)
    else:
        print("✅ Yeni duyuru yok.")
except Exception as e:
    print(f"❌ Bildirim gönderme hatası: {e}")
    sys.exit(1)

# Güncelleme
try:
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(duyurular, f, ensure_ascii=False, indent=2)
except Exception as e:
    print(f"❌ JSON yazma hatası: {e}")
    sys.exit(1)

# Başarılı tamamlandı
print("✅ check_announcements.py başarıyla tamamlandı.")
sys.exit(0)
