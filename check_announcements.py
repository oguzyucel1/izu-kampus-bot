import os
import json
import re
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
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# Sayfayı oku
with open(HTML_PATH, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

duyurular = []
duyuru_divleri = soup.select("div.panel.panel-default")

for panel in duyuru_divleri:
    title_tag = panel.select_one("h3.panel-title a")
    if title_tag:
        tarih_tag = title_tag.select_one("span.pull-right")
        tarih = temizle_metin(tarih_tag.get_text()) if tarih_tag else ""

        for span in title_tag.select("span"):
            span.extract()

        baslik = temizle_metin(title_tag.get_text())
        duyuru_kimligi = f"{baslik} | {tarih}" if tarih else baslik
        duyurular.append(duyuru_kimligi)

# Eski duyuruları yükle
try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        onceki_duyurular = json.load(f)
except FileNotFoundError:
    onceki_duyurular = []

# Normalize ederek karşılaştır
yeni_duyurular = [
    d for d in duyurular
    if temizle_metin(d) not in [temizle_metin(e) for e in onceki_duyurular]
]

# Bildirim gönder
if yeni_duyurular:
    for duyuru in yeni_duyurular:
        try:
            baslik, tarih = duyuru.split("|", 1)
        except ValueError:
            baslik, tarih = duyuru, "Tarih yok"

        mesaj = f"📢 Yeni duyuru: {baslik.strip()}\n📅 Tarih: {tarih.strip()}\n📌 Detaylara sistemden ulaşabilirsiniz."
        send_telegram_message(mesaj)
else:
    print("✅ Yeni duyuru yok.")

# Güncelleme
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(duyurular, f, ensure_ascii=False, indent=2)
