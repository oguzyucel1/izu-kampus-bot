import subprocess

# 1. Giriş yap ve HTML dosyasını al
print("🔐 1. Login ve sınav sayfası çekiliyor...")
subprocess.run(["python", "login_script.py"])

# 2. HTML'den JSON'a dönüştür
print("💾 2. HTML'den notlar ayrıştırılıyor ve kaydediliyor...")
subprocess.run(["python", "save_grades.py"])

# 3. Güncel notlar kontrol ediliyor
print("🔍 3. Değişiklik kontrolü yapılıyor...")
subprocess.run(["python", "check_updates.py"])
