import subprocess
import zipfile
import os 
import requests

def send_file_to_telegram(file_path, caption="📄 Dosya"):
    url = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendDocument"
    with open(file_path, "rb") as f:
        requests.post(url, data={"chat_id": os.getenv("CHAT_ID"), "caption": caption}, files={"document": f})

def zip_and_send_cache():
    zip_name = "cache_dosyasi.zip"
    with zipfile.ZipFile(zip_name, "w") as zipf:
        for root, dirs, files in os.walk(".cache"):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, ".cache")
                zipf.write(full_path, arcname)
    send_file_to_telegram(zip_name, "🗂 Tüm cache dosyaları ZIP halinde")

def zip_and_send_cache():
    zip_name = "cache_dosyasi.zip"
    with zipfile.ZipFile(zip_name, "w") as zipf:
        for root, dirs, files in os.walk(".cache"):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, ".cache")
                zipf.write(full_path, arcname)
    send_file_to_telegram(zip_name, "🗂 Tüm cache dosyaları zip")

print("🔐 [1/4] Login ve sınav sayfası çekiliyor...")
subprocess.run(["python", "login_script.py"], check=True)

print("💾 [2/4] Notlar kaydediliyor ve karşılaştırılıyor...")
subprocess.run(["python", "check_grades.py"], check=True)

print("📣 [3/4] Duyurular kontrol ediliyor...")
subprocess.run(["python", "check_announcements.py"], check=True)

print("📆 [4/4] Etkinlikler kontrol ediliyor...")
subprocess.run(["python", "check_events.py"], check=True)

zip_and_send_cache()




