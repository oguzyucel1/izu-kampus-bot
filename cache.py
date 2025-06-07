import os
from dotenv import load_dotenv
import requests

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_file_to_telegram(file_path, caption="📄 Cache Durumu"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as file:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": file})

def cache_durumunu_gonder():
    cache_dosyalar = [
        "onceki_notlar_duzenli.json",
        "onceki_duyurular.json",
        "onceki_etkinlikler.json"
    ]
    
    icerik = ""
    for dosya in cache_dosyalar:
        if os.path.exists(dosya):
            with open(dosya, "r", encoding="utf-8") as f:
                icerik += f"\n🗂️ {dosya}\n" + "-"*40 + "\n" + f.read() + "\n\n"
        else:
            icerik += f"\n❌ {dosya} bulunamadı!\n"

    # Geçici .txt dosyası olarak kaydet
    with open("cache_durum.txt", "w", encoding="utf-8") as f:
        f.write(icerik)

    # Telegram'a gönder
    send_file_to_telegram("cache_durum.txt", "🧠 Cache Durumu")
