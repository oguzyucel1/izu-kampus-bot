import os
import json
import re
from bs4 import BeautifulSoup

# Sabit yollar
HTML_PATH = "home.html"
ANN_JSON = "onceki_duyurular.json"
EVT_JSON = "onceki_etkinlikler.json"

def temizle_metin(metin):
    return re.sub(r'\s+', ' ', metin).strip()

# HTML oku
with open(HTML_PATH, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# --- DUYURULAR ---
duyurular = []
duyuru_divleri = soup.select("div.panel.panel-default")
for panel in duyuru_divleri:
    title_tag = panel.select_one("h3.panel-title a")
    if title_tag:
        tarih_tag = title_tag.select_one("span.pull-right")
        tarih = temizle_metin(tarih_tag.get_text()) if tarih_tag else ""
        for span in title_tag.select("span"):
            span.extract()
        baslik = temizle_metin(title_tag.get_text())
        kimlik = f"{baslik} | {tarih}"
        duyurular.append(kimlik)

# Duyuruları JSON'a yaz
os.makedirs(os.path.dirname(ANN_JSON), exist_ok=True)
with open(ANN_JSON, "w", encoding="utf-8") as f:
    json.dump(duyurular, f, ensure_ascii=False, indent=2)
print(f"✅ Duyurular kaydedildi: {ANN_JSON}")
if not duyurular:
    print("⚠️ Hiç duyuru bulunamadı.")

# --- ETKİNLİKLER ---
etkinlikler = []
etkinlik_lileri = soup.select("ul.feeds.clearfix > li.hoverable")
for li in etkinlik_lileri:
    desc = li.select_one("div.desc")
    date = li.select_one("div.date")
    if desc and date:
        satirlar = [temizle_metin(x) for x in desc.stripped_strings]
        zaman_baslik_hoca = ' | '.join(satirlar)
        tarih = temizle_metin(date.get_text().splitlines()[-1])
        kimlik = f"{zaman_baslik_hoca} | {tarih}"
        etkinlikler.append(kimlik)

# Etkinlikleri JSON'a yaz
os.makedirs(os.path.dirname(EVT_JSON), exist_ok=True)
with open(EVT_JSON, "w", encoding="utf-8") as f:
    json.dump(etkinlikler, f, ensure_ascii=False, indent=2)
print(f"✅ Etkinlikler kaydedildi: {EVT_JSON}")
if not etkinlikler:
    print("⚠️ Hiç etkinlik bulunamadı.")
