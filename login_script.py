import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
 
# .env dosyasını yükle
load_dotenv()
KULLANICI_ADI = os.getenv("KULLANICI_ADI")
SIFRE = os.getenv("SIFRE")
 
# Tarayıcıyı başlat
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--headless")  # Localde çalıştırmak için bu satırı devre dışı bırakın
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
 
# 1. Giriş Sayfasına Git
driver.get("https://kampus.izu.edu.tr/login")
 
# 2. Kullanıcı adı ve şifre gir
driver.find_element(By.ID, "user_name").send_keys(KULLANICI_ADI)
sifre_input = driver.find_element(By.ID, "user_pas")
sifre_input.send_keys(SIFRE)
sifre_input.send_keys(Keys.RETURN)
 
# 3. Giriş sonrası yönlendirme kontrolü
time.sleep(5)

if "login" in driver.current_url.lower():
    print("❌ Giriş başarısız. Login sayfasında kaldı.")
    driver.quit()
    exit()

else:
    print(f"✅ Giriş başarılı! Şu anda bu sayfadasın: {driver.current_url}")
    with open("home.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("📄 Ana sayfa kaydedildi: home.html")
 
# 4. Menüde "Sınav Sonuçları" linkini bul ve tıkla


MAX_ATTEMPTS = 3
success = False

for attempt in range(1, MAX_ATTEMPTS + 1):
    try:
        print(f"🔍 'Sınav Sonuçları' bağlantısı aranıyor... Deneme {attempt}")

        # Önce DOM’da elementin varlığını bekle
        link = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//a[@menuilsemno='2055']"))
        )

        # Sonra JavaScript ile native tıklama
        driver.execute_script("arguments[0].click();", link)

        print("✅ 'Sınav Sonuçları' bağlantısına tıklandı.")
        success = True
        break

    except Exception as e:
        print(f"⚠️ Tıklama başarısız: {e}")
        time.sleep(2)

if not success:
    print("❌ Bağlantıya tıklanamadı. İşlem iptal edildi.")
    driver.quit()
    exit()

# 5. Sayfanın yüklenmesini bekle
try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table-striped')]"))
    )
    print("✅ Notlar tablosu yüklendi.")
except:
    print("❌ Notlar tablosu bulunamadı.")
    driver.quit()
    exit()

# 6. Sayfanın HTML içeriğini kaydet
with open("sinav_sonuclari.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)
print("📄 Sınav sonuçları sayfası kaydedildi: sinav_sonuclari.html")
