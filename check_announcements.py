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

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text.strip())

# Güncel HTML'den duyuruları oku
with open(HTML_PATH, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

duyurular = []
for a in soup.select(".panel-title a.accordion-toggle"):
    baslik = normalize_whitespace(a.contents[0])
    tarih = normalize_whitespace(a.find("span").text)
    duyurular.append({"baslik": baslik, "tarih": tarih})

# Önceki JSON varsa oku, yoksa boş liste
if os.path.exists(JSON_PATH):
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        onceki_duyurular = json.load(f)
else:
    onceki_duyurular = []

# Karşılaştırma
yeni_duyurular = [d for d in duyurular if d not in onceki_duyurular]

if yeni_duyurular:
    mesaj = "🆕 *Yeni Duyurular:*\n\n"
    for duyuru in yeni_duyurular:
        mesaj += f"📌 {duyuru['baslik']}\n📅 {duyuru['tarih']}\n📎 Detaylara sistemden ulaşabilirsiniz.\n\n"
    send_telegram_message(mesaj)
else:
    send_telegram_message("📭 Yeni duyuru bulunamadı.")

# Güncel duyuruları JSON'a yaz (cache için)
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(duyurular, f, ensure_ascii=False, indent=2)
