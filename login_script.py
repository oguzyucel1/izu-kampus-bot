import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
KULLANICI_ADI = os.getenv("KULLANICI_ADI")
SIFRE = os.getenv("SIFRE")

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Sunucuda çalıştığın için gerekli
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

driver.get("https://kampus.izu.edu.tr/login")

# Giriş yap
try:
    driver.find_element(By.ID, "user_name").send_keys(KULLANICI_ADI)
    sifre_input = driver.find_element(By.ID, "user_pas")
    sifre_input.send_keys(SIFRE)
    sifre_input.send_keys(Keys.RETURN)
except:
    print("❌ Giriş inputları bulunamadı.")
    driver.quit()
    exit()

# Sayfa yönlendirmesini bekle
time.sleep(5)
if "login" in driver.current_url.lower():
    print("❌ Giriş başarısız. Login sayfasında kaldı.")
    driver.quit()
    exit()
else:
    print(f"✅ Giriş başarılı! Şu anda bu sayfadasın: {driver.current_url}")

# Menüye tıkla
try:
    sinav_link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sınav Sonuçları')]"))
    )
    sinav_link.click()
    print("✅ 'Sınav Sonuçları' bağlantısına tıklandı.")
except Exception as e:
    print(f"❌ Bağlantıya tıklanamadı: {e}")
    driver.quit()
    exit()

# Sayfa yüklenmesini bekle
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table-striped')]"))
    )
    print("✅ Notlar tablosu yüklendi.")
except:
    print("❌ Notlar tablosu bulunamadı.")
    with open("sinav_sonuclari.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("⚠️ Yine de HTML kaydedildi.")
    driver.quit()
    exit()

# HTML kaydet
with open("sinav_sonuclari.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)
print("📄 Sayfa HTML olarak kaydedildi.")

driver.quit()
