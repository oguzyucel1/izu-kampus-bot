# save_events.py
from bs4 import BeautifulSoup
import json
import re

HTML_PATH = "home.html"
JSON_PATH = "onceki_etkinlikler.json"

def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

def run():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    etkinlikler = []
    for li in soup.select("li.hoverable"):
        try:
            span = li.select_one("div.desc > span")
            etkinlik_ad_saat = normalize(span.get_text())

            ogretim_uyesi = normalize(span.find_next("i").get_text())

            tarih_raw = li.select_one("div.date").get_text(separator="\n").strip().split("\n")[-1]
            tarih = normalize(tarih_raw)

            etkinlikler.append({
                "etkinlik": etkinlik_ad_saat,
                "ogretim_uyesi": ogretim_uyesi,
                "tarih": tarih
            })
        except Exception:
            continue

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(etkinlikler, f, ensure_ascii=False, indent=2)
