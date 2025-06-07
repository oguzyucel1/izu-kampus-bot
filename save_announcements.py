# save_announcements.py
from bs4 import BeautifulSoup
import json
import re

HTML_PATH = "home.html"
JSON_PATH = "onceki_duyurular.json"

def normalize(text):
    return re.sub(r"\s+", " ", text.strip())

def run():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    duyurular = []
    for a in soup.select("a.accordion-toggle"):
        baslik = normalize(a.contents[0])
        tarih_span = a.find("span")
        tarih = normalize(tarih_span.get_text()) if tarih_span else ""
        duyurular.append({"baslik": baslik, "tarih": tarih})

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(duyurular, f, ensure_ascii=False, indent=2)
