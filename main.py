import subprocess

print("🔐 [1/4] Login ve sınav sayfası çekiliyor...")
subprocess.run(["python", "login_script.py"], check=True)

print("💾 [2/4] Notlar kaydediliyor ve karşılaştırılıyor...")
subprocess.run(["python", "check_grades.py"], check=True)

print("📣 [3/4] Duyurular kontrol ediliyor...")
subprocess.run(["python", "check_announcements.py"], check=True)

print("📆 [4/4] Etkinlikler kontrol ediliyor...")
subprocess.run(["python", "check_events.py"], check=True)

print("📤 [5/5] Cache dosyaları Telegram'a gönderiliyor...")
subprocess.run(["python", "cache.py"], check=True)


