import subprocess

print("🔐 [1/3] Login ve sınav sayfası çekiliyor...")
subprocess.run(["python", "login_script.py"], check=True)

print("💾 [2/3] HTML'den notlar ayrıştırılıyor ve kaydediliyor...")
subprocess.run(["python", "save_grades.py"], check=True)

print("🔍 [3/3] Değişiklik kontrolü yapılıyor...")
subprocess.run(["python", "check_updates.py"], check=True)
