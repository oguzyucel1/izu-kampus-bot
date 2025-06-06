import json
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

OLD_JSON_PATH = "onceki_notlar_duzenli.json"
NEW_HTML_PATH = "sinav_sonuclari.html"

# .env dosyasından bot bilgilerini al
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_file_to_telegram(file_path, caption="📄 Dosya"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as file:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": file})


def send_telegram_message(message):
    """Telegram'a mesaj gönderir"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)



def parse_new_html(path):
    with open(path, "r", encoding="utf-8") as file:
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
            kod = tds[0].text.strip()
            adi = tds[1].text.strip()
            ogretmen = tds[2].text.strip()

            if i + 1 < len(rows):
                detay = rows[i + 1]
                if "gizli" in detay.get("class", []):
                    tablo = detay.select_one("table")
                    if tablo:
                        for satir in tablo.select("tbody tr"):
                            cols = satir.find_all("td")
                            if len(cols) >= 6:
                                ders_dict[kod]["Ders Adı"] = adi
                                ders_dict[kod]["Öğretim Üyesi"] = ogretmen
                                ders_dict[kod]["Sınavlar"].append({
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

    return ders_dict

def farklari_bul(yeni, eski):
    farklar = []
    for kod, bilgiler in yeni.items():
        if kod not in eski:
            for sinav in bilgiler["Sınavlar"]:
                if sinav["Not"]:
                    farklar.append((kod, bilgiler["Ders Adı"], sinav, "Yeni sınav türü"))
        else:
            eski_sinavlar = eski[kod]["Sınavlar"]
            for sinav in bilgiler["Sınavlar"]:
                eslesen = next((s for s in eski_sinavlar if s["Sınav Türü"] == sinav["Sınav Türü"]), None)
                if eslesen:
                    onceki_not = eslesen["Not"].strip().lower()
                    yeni_not = sinav["Not"].strip().lower()
                    if (onceki_not in ["", "gm"] and yeni_not not in ["", "gm"] and onceki_not != yeni_not):
                        farklar.append((kod, bilgiler["Ders Adı"], sinav, "Not girildi"))
                    elif onceki_not != yeni_not and onceki_not != "" and yeni_not != "":
                        farklar.append((kod, bilgiler["Ders Adı"], sinav, "Not değiştirildi"))
                else:
                    if sinav["Not"]:
                        farklar.append((kod, bilgiler["Ders Adı"], sinav, "Yeni sınav türü"))
    return farklar

# Eski veriyi yükle
with open(OLD_JSON_PATH, "r", encoding="utf-8") as f:
    eski_json = json.load(f)
eski_dict = {d["Ders Kodu"]: d for d in eski_json}

# Yeni veriyi çek
yeni_dict = parse_new_html(NEW_HTML_PATH)

# Farkları bul
farklar = farklari_bul(yeni_dict, eski_dict)

if farklar:
    degisim_zamani = datetime.now().strftime("%Y-%m-%d %H:%M")
    mesaj = f"🆕 Değişiklikler tespit edildi ({degisim_zamani}):\n\n"
    for kod, adi, sinav, degisiklik_turu in farklar:
        mesaj += (
            f"📘 {kod} - {adi}\n"
            f"🔄 {degisiklik_turu}: {sinav['Sınav Türü']} - Not: {sinav['Not']} | 🕒 İlan: {degisim_zamani}\n\n"
        )
    print(mesaj)
    send_telegram_message(mesaj)

    # Yeni veriyi kaydet
    yeni_kayitlar = []
    for kod, bilgiler in yeni_dict.items():
        yeni_kayitlar.append({
            "Ders Kodu": kod,
            "Ders Adı": bilgiler["Ders Adı"],
            "Öğretim Üyesi": bilgiler["Öğretim Üyesi"],
            "Sınavlar": bilgiler["Sınavlar"]
        })
    with open(OLD_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(yeni_kayitlar, f, ensure_ascii=False, indent=2)
else:
    mesaj = "🔁 Yeni not girişi veya değişiklik tespit edilmedi."
    print(mesaj)
    send_telegram_message(mesaj)
    send_file_to_telegram("sinav_sonuclari.html", "📄 Son çekilen HTML dosyası")
    send_file_to_telegram("onceki_notlar_duzenli.json", "🧾 Güncel JSON verisi")

