import os
import json
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime
import requests
from dotenv import load_dotenv

# ENV yükle
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Dosya yolları
HTML_PATH = "sinav_sonuclari.html"
CACHE_DIR = ".cache"
JSON_PATH = os.path.join(CACHE_DIR, "onceki_notlar_duzenli.json")

def send_cache_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > 3900:
            send_telegram_message("📁 JSON içeriği çok büyük, dosya olarak gönderiliyor.")
            send_file_to_telegram(file_path, caption="📦 Cache JSON içeriği")
        else:
            send_telegram_message(f"🧾 Cache içeriği:\n\n{content}")
    else:
        send_telegram_message("❌ Cache dosyası bulunamadı.")


# Telegram fonksiyonları
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def send_file_to_telegram(file_path, caption="📄 Dosya"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as file:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": file})

# HTML'den notları çek
def parse_html(path):
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
            kod, adi, ogretmen = tds[0].text.strip(), tds[1].text.strip(), tds[2].text.strip()

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

# Farkları karşılaştır
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

# ✔ Ana akış
yeni_dict = parse_html(HTML_PATH)

# Önceki json cache'de yoksa boş başlat
if not os.path.exists(JSON_PATH):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# Önceki JSON'u yükle
with open(JSON_PATH, "r", encoding="utf-8") as f:
    eski_json = json.load(f)
eski_dict = {d["Ders Kodu"]: d for d in eski_json}

# Farkları bul
farklar = farklari_bul(yeni_dict, eski_dict)

if farklar:
    mesaj = f"🆕 Not değişiklikleri ({datetime.now().strftime('%Y-%m-%d %H:%M')}):\n\n"
    for kod, adi, sinav, degisiklik in farklar:
        mesaj += (
            f"📘 {kod} - {adi}\n"
            f"🔄 {degisiklik}: {sinav['Sınav Türü']} - Not: {sinav['Not']}\n\n"
        )
    print(mesaj)
    send_telegram_message(mesaj)
else:
    mesaj = "🔁 Yeni not girişi veya değişiklik tespit edilmedi."
    print(mesaj)
    send_telegram_message(mesaj)

# Yeni JSON'u cache’e yaz
duzenlenmis = []
for kod, bilgiler in yeni_dict.items():
    duzenlenmis.append({
        "Ders Kodu": kod,
        "Ders Adı": bilgiler["Ders Adı"],
        "Öğretim Üyesi": bilgiler["Öğretim Üyesi"],
        "Sınavlar": bilgiler["Sınavlar"]
    })
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(duzenlenmis, f, ensure_ascii=False, indent=2)

print("✅ Güncellenmiş JSON cache'e yazıldı.")

send_cache_content(JSON_PATH)

