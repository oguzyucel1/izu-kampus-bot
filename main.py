import subprocess
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_file_to_telegram(file_path, caption="📄 Dosya"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as file:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": file})

print("🔐 [1/3] Login ve sınav sayfası çekiliyor...")
subprocess.run(["python", "login_script.py"], check=True)

# Her durumda HTML gönder
html_path = "sinav_sonuclari.html"
if os.path.exists(html_path):
    send_file_to_telegram(html_path, "📄 Güncel sınav sayfası HTML içeriği")

print("💾 [2/3] HTML'den notlar ayrıştırılıyor ve kaydediliyor...")
subprocess.run(["python", "save_grades.py"], check=True)

print("🔍 [3/3] Değişiklik kontrolü yapılıyor...")
subprocess.run(["python", "check_updates.py"], check=True)
