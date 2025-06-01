import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# .env'den kullanıcı bilgilerini al
load_dotenv()
KULLANICI_ADI = os.getenv("KULLANICI_ADI")
SIFRE = os.getenv("SIFRE")

# Tarayıcı ayarları (Render'da headless mod gerekiyor)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# 1. Login sayfasına git
driver.get("https://kampus.izu.edu.tr/login")

# 2. Giriş yap
try:
    driver.find_element(By.ID, "user_name").send_keys(KULLANICI_ADI)
    sifre_input = driver.find_element(By.ID, "user_pas")
    sifre_input.send_keys(SIFRE)
    sifre_input.send_keys(Keys.RETURN)
except Exception as e:
    print(f"❌ Giriş inputları bulunamadı: {e}")
    driver.quit()
    exit()

# 3. Login sonrası kontrol
time.sleep(5)
if "login" in driver.current_url.lower():
    print("❌ Giriş başarısız. Login sayfasında kaldı.")
    driver.quit()
    exit()
else:
    print(f"✅ Giriş başarılı! Şu anda bu sayfadasın: {driver.current_url}")

# ✅ "Sınav Sonuçları" sayfasına doğrudan JavaScript ile yönlen
try:
    js_code = """History.navigateToPath(decodeURIComponent('%2F%2Fkampus.izu.edu.tr%3A443%2FOgr%2FOgrDersSinav'), decodeURIComponent('Sınav Sonuçları'));"""
    driver.execute_script(js_code)
    print("✅ JavaScript ile sınav sayfasına yönlendirildi.")
    time.sleep(5)
except Exception as e:
    print(f"❌ JavaScript yönlendirmesi başarısız: {e}")
    driver.quit()
    exit()

# ✅ Sayfa tamamen yüklendi mi kontrol et
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table-striped')]"))
    )
    print("✅ Notlar tablosu yüklendi.")
except:
    print("❌ Notlar tablosu bulunamadı.")
    with open("sinav_sonuclari.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("⚠️ HTML yine de kaydedildi.")
    driver.quit()
    exit()

# ✅ HTML'i kaydet
with open("sinav_sonuclari.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)
print("📄 Sayfa HTML olarak kaydedildi.")

driver.quit()
driver.quit()
