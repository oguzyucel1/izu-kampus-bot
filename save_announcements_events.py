from bs4 import BeautifulSoup
import json
import re

HTML_PATH = "home.html"
DUYURU_JSON_PATH = "onceki_duyurular.json"
ETKINLIK_JSON_PATH = "onceki_etkinlikler.json"

def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

def save_announcements():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    duyurular = []
    for panel in soup.select(".panel.panel-default"):
        baslik_el = panel.select_one("a.accordion-toggle")
        tarih_el = panel.select_one("span.pull-right")
        if baslik_el and tarih_el:
            baslik = normalize(baslik_el.text.replace(tarih_el.text, ""))
            tarih = normalize(tarih_el.text)
            duyurular.append({"baslik": baslik, "tarih": tarih})

    return duyurular

def save_events():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    etkinlikler = []
    for li in soup.select("li.hoverable"):
        span = li.select_one(".desc span")
        i_tag = li.select_one(".desc i")
        date_div = li.select_one(".date")

        if span and i_tag and date_div:
            raw_text = span.text.strip()
            saat, etkinlik_adi = raw_text.split("|", 1) if "|" in raw_text else ("", raw_text)
            saat = normalize(saat)
            etkinlik_adi = normalize(etkinlik_adi.split("(")[0])  # Parantez ayıklama
            ogretim_uyesi = normalize(i_tag.text.replace("(", "").replace(")", ""))
            tarih = normalize(date_div.get_text(strip=True).split("\n")[-1])

            etkinlikler.append({
                "etkinlik": etkinlik_adi,
                "saat": saat,
                "tarih": tarih,
                "ogretim_uyesi": ogretim_uyesi
            })

    return etkinlikler

# Bellekte verileri al
duyurular = save_announcements()
etkinlikler = save_events()

# JSON'a yaz
with open(DUYURU_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(duyurular, f, ensure_ascii=False, indent=2)

with open(ETKINLIK_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(etkinlikler, f, ensure_ascii=False, indent=2)

print("✅ Güncel duyurular ve etkinlikler kaydedildi.")
