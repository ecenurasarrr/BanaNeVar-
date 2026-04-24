# BanaNeVar - Mersin Etkinlik Asistanı 🚀

BanaNeVar, Mersin'deki etkinlikleri takip etmenizi, bilet almanızı ve yapay zeka (Gemini AI) desteğiyle size özel etkinlik önerileri almanızı sağlayan modern bir web uygulamasıdır.

## ✨ Özellikler

- **🤖 AI Asistanı**: Google Gemini API kullanarak modunuza ve tercihinize göre akıllı etkinlik önerileri sunar.
- **📅 Etkinlik Takibi**: Müzik, Tiyatro, Gezi, Gastronomi ve Sinema kategorilerinde güncel etkinlikleri listeler.
- **🎫 Biletleme Sistemi**: QR kod destekli bilet oluşturma ve satın alma simülasyonu.
- **💳 Ödeme Ekranı**: Güvenli görünümlü, iki aşamalı modern ödeme arayüzü.
- **🔐 Kullanıcı Sistemi**: Kayıt olma, giriş yapma ve kişisel bilet geçmişini görüntüleme.
- **🎨 Glassmorphism UI**: Modern, şık ve kullanıcı dostu arayüz tasarımı.

## 🛠️ Teknolojiler

- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript (Vanilla)
- **AI**: Google Gemini Pro (google-genai)
- **Diğer**: QR Code Generator, Python-Dotenv

## 🚀 Kurulum

1. Bu depoyu klonlayın:
   ```bash
   git clone https://github.com/ecenurasarrr/BanaNeVar-.git
   cd BanaNeVar-
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. `.env` dosyasını oluşturun ve Gemini API anahtarınızı ekleyin:
   ```env
   GEMINI_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key
   ```

4. Uygulamayı çalıştırın:
   ```bash
   python app.py
   ```

Uygulama `http://127.0.0.1:5001` adresinde çalışacaktır.

## 📝 Lisans

Bu proje MIT lisansı ile lisanslanmıştır.
