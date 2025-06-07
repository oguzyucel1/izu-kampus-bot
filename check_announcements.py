import json
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

# Yollar
HTML_PATH = "home.html"
JSON_PATH = "onceki_duyurular.json"

# .env'den bilgileri al
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Telegram fonksiyonları
def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def send_file(file_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": f})

# HTML'den duyuruları çıkar
def parse_announcements(html_path):
    with open(html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    duyurular = []
    for panel in soup.select(".panel.panel-default"):
        title_tag = panel.select_one(".panel-title a")
        if not title_tag: continue
        title = title_tag.get_text(strip=True)
        date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", title_tag.text)
        tarih = date_match.group(0) if date_match else "Tarih Yok"
        duyurular.append({"baslik": title, "tarih": tarih})
    return duyurular

# Eski veriyi oku
def load_previous_data():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Yeni duyuruları karşılaştır
def find_new_announcements(guncel, onceki):
    onceki_set = {(d["baslik"], d["tarih"]) for d in onceki}
    return [d for d in guncel if (d["baslik"], d["tarih"]) not in onceki_set]

# === ANA İŞLEM ===
guncel_duyurular = parse_announcements(HTML_PATH)
onceki_duyurular = load_previous_data()
yeni_duyurular = find_new_announcements(guncel_duyurular, onceki_duyurular)

# Bildirim gönder
if yeni_duyurular:
    mesaj = f"📢 <b>Yeni Duyurular ({datetime.now().strftime('%d.%m.%Y %H:%M')})</b>\n\n"
    for d in yeni_duyurular:
        mesaj += f"📌 {d['baslik']}\n📅 {d['tarih']}\n🔗 Detaylara sistemden ulaşabilirsiniz\n\n"
    print("[+] Yeni duyurular bulundu, mesaj gönderildi.")
    send_message(mesaj)
else:
    send_message("🔁 Yeni duyuru bulunamadı.")
    print("[=] Yeni duyuru yok.")

# Her durumda güncel veriyi kaydet
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(guncel_duyurular, f, ensure_ascii=False, indent=2)
print(f"[✓] JSON güncellendi: {JSON_PATH}")
