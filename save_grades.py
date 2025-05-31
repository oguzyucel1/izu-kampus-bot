from bs4 import BeautifulSoup
import json
from collections import defaultdict

# HTML dosya yolu
HTML_PATH = "sinav_sonuclari.html"
JSON_PATH = "onceki_notlar_duzenli.json"

# HTML dosyasını oku
with open(HTML_PATH, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

rows = soup.select("table tbody tr")
ders_dict = defaultdict(lambda: {
    "Ders Adı": "",
    "Öğretim Üyesi": "",
    "Sınavlar": []
})

i = 0
while i < len(rows):
    tr = rows[i]
    if "gizli" not in tr.get("class", []):
        tds = tr.find_all("td")
        if len(tds) < 6:
            i += 1
            continue
        ders_kodu = tds[0].text.strip()
        ders_adi = tds[1].text.strip()
        ogretmen = tds[2].text.strip()

        if i + 1 < len(rows):
            detay_tr = rows[i + 1]
            if "gizli" in detay_tr.get("class", []):
                detay_tablosu = detay_tr.select_one("table")
                if detay_tablosu:
                    for satir in detay_tablosu.select("tbody tr"):
                        cols = satir.find_all("td")
                        if len(cols) >= 6:
                            ders_dict[ders_kodu]["Ders Adı"] = ders_adi
                            ders_dict[ders_kodu]["Öğretim Üyesi"] = ogretmen
                            ders_dict[ders_kodu]["Sınavlar"].append({
                                "Sınav Türü": cols[0].text.strip(),
                                "Not": cols[1].text.strip(),
                                "Ortalama": cols[2].text.strip(),
                                "Yüzde Dilimi": cols[3].text.strip(),
                                "Sınav Tarihi": cols[4].text.strip(),
                                "İlan Tarihi": cols[5].text.strip()
                            })
        i += 2
    else:
        i += 1

# Sözlükten listeye çevir
duzenlenmis_dersler = []
for kod, bilgiler in ders_dict.items():
    duzenlenmis_dersler.append({
        "Ders Kodu": kod,
        "Ders Adı": bilgiler["Ders Adı"],
        "Öğretim Üyesi": bilgiler["Öğretim Üyesi"],
        "Sınavlar": bilgiler["Sınavlar"]
    })

# JSON dosyasına yaz
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(duzenlenmis_dersler, f, ensure_ascii=False, indent=2)

print(f"✅ Kaydedildi: {JSON_PATH}")
