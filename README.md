![Header](https://github.com/user-attachments/assets/a5158019-26d8-4778-a34e-c63c24811c38)



## 🏫 IZÜ Kampüs Bilgi Sistemi Not Takip Botu

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

### 📌 Hakkında

Bu Python uygulaması, İstanbul Sabahattin Zaim Üniversitesi'nin **Kampüs Bilgi Sistemi**'ne otomatik olarak giriş yapar ve **“Sınav Sonuçları”** sayfasında not değişikliği olup olmadığını kontrol eder.  
Herhangi bir ders için **yeni not girildiğinde**, **Telegram üzerinden otomatik bildirim gönderir.**

---

### 🧠 Kullanılan Teknolojiler

| Amaç | Kütüphane |
|------|-----------|
| 🧭 Web tarayıcısını otomatik kontrol | `selenium` |
| 🔍 HTML içinden veri ayıklama | `beautifulsoup4` |
| 📬 Telegram botuyla mesaj gönderimi | `requests` |
| 🌐 Ortam değişkeni yönetimi (.env) | `python-dotenv` |
| 🌐 Basit web sunucu (Webhook, opsiyonel) | `Flask` |

---

### ⚙️ Nasıl Çalışır?

1. Öğrencinin e-posta ve şifresiyle sisteme giriş yapılır  
2. “Sınav Sonuçları” sayfası tarayıcıdan alınır  
3. HTML içinden dersler ve notlar ayrıştırılır  
4. Daha önceki notlar ile karşılaştırılır  
5. Yeni bir not girildiyse, Telegram’a mesaj gönderilir:

```text
📘 BIM430 - Derin Öğrenme
🔄 Yeni Not: Final 1 - 92
🕒 İlan Tarihi: 01.06.2025 14:36
```
### 🚀 Kurulum (Kısaca)

```bash
pip install -r requirements.txt
python main.py
```
### 🌐 .env Dosyasında

```bash
KULLANICI_ADI=... Üniversite E-Postası
SIFRE=... KBS Şifreniz
BOT_TOKEN=... Telegram Bot Tokeni ( ileride public olarak sağlanacaktır!)
CHAT_ID=... Kişisel Telegram Bot Chat ID ( kişisel kullanım entegresi ile birlikte gelecektir.)
```
---
### ⏱️ Zamanlama Sistemi

Şu anda GitHub Actions üzerinden main.py dosyası her 10 dakikada bir çalışacak şekilde ayarlanmıştır.
(Free plan nedeniyle gecikmeler yaşanabilir.)

---

### 📈 Yakında Eklenecekler

☁️ Web sunucuya taşınarak daha stabil çalışacak yapı

👥 Çoklu kullanıcı desteği: Her öğrenci kendi bilgilerinden giriş yapacak

🔐 Daha gelişmiş veri gizliliği ve güvenlik

🗃️ Veritabanı desteğiyle geçmiş notların takibi

---

# 🧑‍💻 Geliştirici

Mehmet Oğuz Yücel

📫 E-mail : oguzyucell.oy@gmail.com



# ⭐️ Repo'ya yıldız bırakmayı unutma :)




