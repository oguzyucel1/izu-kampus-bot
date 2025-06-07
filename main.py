import subprocess

print("🔐 [1/7] Login ve sınav sayfası çekiliyor...")
subprocess.run(["python", "login_script.py"], check=True)

print("💾 [2/7] HTML'den notlar ayrıştırılıyor ve kaydediliyor...")
subprocess.run(["python", "save_grades.py"], check=True)

print("🔍 [3/7] Notlarda değişiklik kontrolü yapılıyor...")
subprocess.run(["python", "check_grades.py"], check=True)

print("📢 [6/7] Yeni duyurular kontrol ediliyor...")
subprocess.run(["python", "check_announcements.py"], check=True)

print("📆 [7/7] Yeni etkinlikler kontrol ediliyor...")
subprocess.run(["python", "check_events.py"], check=True)
