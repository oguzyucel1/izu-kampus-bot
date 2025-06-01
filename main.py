import subprocess
import requests
import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_file_to_telegram(file_path, caption="📄 Dosya"):
    """Telegram'a dosya gönder"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": file})
            print(f"📤 Telegram'a gönderildi: {caption}")
    else:
        print(f"⚠️ Dosya bulunamadı: {file_path}")

# 1. Adım: Giriş yap ve HTML'yi çek
print("🔐 [1/3] Login ve sınav sayfası çekiliyor...")
subprocess.run(["python", "login_script.py"], check=True)

# 1.1: Çekilen HTML dosyasını gönder
send_file_to_telegram("sinav_sonuclari.html", "📄 Güncel sınav sayfası (HTML)")

# 2. Adım: HTML'den JSON'a dönüştür
print("💾 [2/3] HTML'den notlar ayrıştırılıyor ve kaydediliyor...")
subprocess.run(["python", "save_grades.py"], check=True)

# 2.1: JSON dosyasını gönder
send_file_to_telegram("onceki_notlar_duzenli.json", "🧾 JSON Not Verisi")

# 3. Adım: Değişiklik kontrolü ve Telegram mesajı
print("🔍 [3/3] Değişiklik kontrolü yapılıyor...")
subprocess.run(["python", "check_updates.py"], check=True)
