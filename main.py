import subprocess

# 1. Giriş yap ve HTML dosyasını al
print("\n 🔐 [1/3]  Login ve sınav sayfası çekiliyor... \n")
subprocess.run(["python", "login_script.py"])

# 2. HTML'den JSON'a dönüştür
print("\n 💾 [2/3]  HTML'den notlar ayrıştırılıyor ve kaydediliyor... \n")
subprocess.run(["python", "save_grades.py"])

# 3. Güncel notlar kontrol ediliyor
print("\n🔍 [3/3]  Değişiklik kontrolü yapılıyor... \n")
subprocess.run(["python", "check_updates.py"])
