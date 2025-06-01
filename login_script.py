import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ortam değişkenlerini yükle
load_dotenv()
KULLANICI_ADI = os.getenv("KULLANICI_ADI")
SIFRE = os.getenv("SIFRE")

# Tarayıcı ayarları
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Render'da headless gerekli
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Kampüs giriş sayfasına git
driver.get("https://kampus.izu.edu.tr/login")

# Giriş formunu doldur
try:
    driver.find_element(By.ID, "user_name").send_keys(KULLANICI_ADI)
    sifre_input = driver.find_element(By.ID, "user_pas")
    sifre_input.send_keys(SIFRE)
    sifre_input.send_keys(Keys.RETURN)
except:
    print("❌ Giriş inputları bulunamadı.")
    driver.quit()
    exit()

# Giriş sonrası yönlendirmeyi bekle
time.sleep(5)
if "login" in driver.current_url.lower():
    print("❌ Giriş başarısız. Login sayfasında kaldı.")
    driver.quit()
    exit()
else:
    print(f"✅ Giriş başarılı! Şu anda bu sayfadasın: {driver.current_url}")

# JavaScript ile Sınav Sonuçları sayfasına git
try:
    js_code = """History.navigateToPath(decodeURIComponent('%2F%2Fkampus.izu.edu.tr%3A443%2FOgr%2FOgrDersSinav'), decodeURIComponent('Sınav Sonuçları'));"""
    driver.execute_script(js_code)
    print("✅ JavaScript ile sınav sayfasına yönlendirildi.")

    # Sınav tablosunun yüklenmesini bekle
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table-striped')]"))
    )
    print("✅ Notlar tablosu yüklendi.")
except:
    print("❌ Notlar tablosu bulunamadı.")
    # Yine de sayfa kaydedilsin
    with open("sinav_sonuclari.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("⚠️ HTML yine de kaydedildi.")
    driver.quit()
    exit()

# Sayfa HTML'sini kaydet
with open("sinav_sonuclari.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)
print("📄 Sayfa HTML olarak kaydedildi.")

driver.quit()
