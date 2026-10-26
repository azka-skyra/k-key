"""
Y-Key Chatbot - Rules-based AI (tanpa LLM eksternal)
Keyword matching + product context
"""

# Knowledge base produk Y-Key
PRODUCTS = [
    {"name": "Yogurt Strawberry Fresh", "category": "YOGURT", "price": 15000, "desc": "creamy, segar, cocok buat sarapan", "tags": ["best-seller", "fresh", "sarapan"]},
    {"name": "Yogurt Blueberry Blast", "category": "YOGURT", "price": 17000, "desc": "manis-asam, antioksidan", "tags": ["best-seller", "antioxidant"]},
    {"name": "Yogurt Mango Tropical", "category": "YOGURT", "price": 16000, "desc": "potongan mangga segar, tropical", "tags": ["tropical", "fresh", "sarapan"]},
    {"name": "Yogurt Plain Original", "category": "YOGURT", "price": 12000, "desc": "plain, vegan friendly, tanpa gula tambahan", "tags": ["vegan", "plain", "sehat"]},
    {"name": "Yogurt Matcha Latte", "category": "YOGURT", "price": 18000, "desc": "matcha premium, teh hijau", "tags": ["premium", "matcha"]},
    {"name": "Keychain Acrylic Custom Nama", "category": "KEYCHAIN", "price": 25000, "desc": "custom nama, bisa foto", "tags": ["custom", "best-seller"]},
    {"name": "Keychain Resin Bunga", "category": "KEYCHAIN", "price": 35000, "desc": "bunga asli di resin, handmade", "tags": ["handmade", "premium"]},
    {"name": "Keychain Pom-pom Lucu", "category": "KEYCHAIN", "price": 20000, "desc": "pom-pom lembut, banyak warna", "tags": ["cute", "best-seller"]},
    {"name": "Keychain Kulit Premium", "category": "KEYCHAIN", "price": 45000, "desc": "kulit asli, emboss nama, elegan", "tags": ["premium", "leather"]},
    {"name": "Keychain Karakter 3D", "category": "KEYCHAIN", "price": 30000, "desc": "3D printed, hewan/anime/robot", "tags": ["3d", "custom"]},
]


def get_reply(message, products_from_db=None):
    """
    Generate chatbot reply based on user message.
    Pure Python rules-based, no API call needed.
    """
    msg = message.lower().strip()
    products = products_from_db or PRODUCTS

    # ===== GREETING =====
    if any(w in msg for w in ['halo', 'hai', 'hello', 'hi', 'pagi', 'siang', 'sore', 'malam']):
        return ("Halo! 👋 Selamat datang di Y-Key! Aku Y-Key Bot, asisten AI kamu buat "
                "milih yogurt fresh atau keychain custom. Kamu lagi cari produk untuk "
                "siapa / acara apa nih? 😊🍓🏷️")

    # ===== CARA PESAN =====
    if any(w in msg for w in ['cara pesan', 'cara order', 'gimana pesan', 'cara beli', 'checkout', 'pemesanan']):
        return ("Mantap! 🎉 Cara pesannya gampang:\n\n"
                "1️⃣ Klik tombol **Pesan** di card produk buat bayar via Virtual Account otomatis\n"
                "2️⃣ Atau klik tombol WhatsApp (hijau) di bawah web buat pesan custom/manual\n\n"
                "Kalau bingung milih produk, ceritain dulu selera kamu, aku bantu rekomendasiin! 😊")

    # ===== HARGA =====
    if any(w in msg for w in ['harga', 'berapa', 'biaya', 'price', 'cost', 'murah', 'mahal']):
        yogurt_min = min(p['price'] for p in products if p['category'] == 'YOGURT')
        keychain_min = min(p['price'] for p in products if p['category'] == 'KEYCHAIN')
        keychain_max = max(p['price'] for p in products if p['category'] == 'KEYCHAIN')
        return (f"Harga produk kita:\n\n"
                f"🍓 **Yogurt**: mulai Rp{yogurt_min:,} (Plain Original)\n"
                f"🏷️ **Keychain**: mulai Rp{keychain_min:,} (Pom-pom) - Rp{keychain_max:,} (Kulit Premium)\n\n"
                f"Budget kamu berapa? Biar aku rekomendasiin yang pas! 😊")

    # ===== REKOMENDASI YOGURT BUAT SARAPAN =====
    if 'sarapan' in msg and ('yogurt' in msg or 'yoghurt' in msg or 'pagi' in msg or 'sehat' in msg):
        recs = [p for p in products if p['category'] == 'YOGURT' and p['price'] <= 18000][:3]
        reply = "Buat sarapan, ini rekomendasi yogurt kita yang creamy & menyegarkan:\n\n"
        for p in recs:
            reply += f"🍓 **{p['name']}** - Rp{p['price']:,}\n   {p['desc']}\n\n"
        reply += "Mau yang mana? Atau bilang aja budget kamu, aku bantu pilihkan yang pas! 😊"
        return reply

    # ===== REKOMENDASI DENGAN BUDGET =====
    import re
    budget_match = re.search(r'(\d+)[\s]*(rb|ribu|k|k)', msg)
    if budget_match and ('yogurt' in msg or 'keychain' in msg or 'rekomendasi' in msg or 'mau' in msg):
        budget = int(budget_match.group(1)) * 1000
        category = 'YOGURT' if 'yogurt' in msg or 'yoghurt' in msg else ('KEYCHAIN' if 'keychain' in msg else None)

        if category:
            recs = [p for p in products if p['category'] == category and p['price'] <= budget][:3]
            if recs:
                reply = f"Buat budget Rp{budget:,} nih, ini rekomendasi {category.lower()} yang cocok:\n\n"
                for p in recs:
                    reply += f"{'🍓' if category == 'YOGURT' else '🏷️'} **{p['name']}** - Rp{p['price']:,}\n   {p['desc']}\n\n"
                reply += "Kamu bisa klik tombol **Pesan** di card produk buat bayar via VA otomatis, atau chat WhatsApp buat custom! 😊"
                return reply

    # ===== REKOMENDASI KEYCHAIN HADIAH =====
    if 'hadiah' in msg or 'ultah' in msg or 'kado' in msg or 'gift' in msg:
        return ("Buat hadiah, aku rekomendasiin nih 🎁:\n\n"
                "🌸 **Keychain Resin Bunga** (Rp35.000) - bunga asli di resin, handmade, unik\n"
                "👜 **Keychain Kulit Premium** (Rp45.000) - kulit asli, bisa emboss nama\n"
                "🏷️ **Keychain Acrylic Custom Nama** (Rp25.000) - bisa custom foto\n\n"
                "Buat hadiah ultah, aku suggest Resin Bunga atau Kulit Premium — keliatan premium! "
                "Mau yang mana? 😊")

    # ===== KEYCHAIN CUSTOM =====
    if 'custom' in msg and 'keychain' in msg:
        return ("Keychain custom kita ada beberapa pilihan 🎨:\n\n"
                "🏷️ **Acrylic Custom Nama** - Rp25.000 (bisa foto, nama, desain bebas)\n"
                "🎨 **Karakter 3D** - Rp30.000 (hewan, anime, robot)\n"
                "👜 **Kulit Premium** - Rp45.000 (bisa emboss nama)\n\n"
                "Ceritain mau custom kayak gimana, nanti aku bantu pilihkan yang cocok! 😊")

    # ===== BEST SELLER =====
    if 'best seller' in msg or 'bestseller' in msg or 'terlaris' in msg or 'populer' in msg:
        return ("Best seller kita nih 🔥:\n\n"
                "🍓 **Yogurt Strawberry Fresh** - Rp15.000 (creamy, cocok buat sarapan)\n"
                "🫐 **Yogurt Blueberry Blast** - Rp17.000 (kaya antioksidan)\n"
                "🏷️ **Keychain Acrylic Custom Nama** - Rp25.000 (custom sesuka hati)\n"
                "🧶 **Keychain Pom-pom Lucu** - Rp20.000 (lucu buat gantungan tas)\n\n"
                "Mau coba yang mana? 😊")

    # ===== VEGAN / SEHAT =====
    if 'vegan' in msg or 'sehat' in msg or 'diet' in msg or 'gula' in msg:
        return ("Buat kamu yang peduli kesehatan, ini rekomendasi 💪:\n\n"
                "🥛 **Yogurt Plain Original** - Rp12.000 (tanpa gula tambahan, vegan friendly)\n"
                "🫐 **Yogurt Blueberry Blast** - Rp17.000 (kaya antioksidan)\n\n"
                "Cocok buat sarapan sehat atau camilan diet. Mau coba? 😊")

    # ===== PERTANYAAN STOK =====
    if 'stok' in msg or 'ready' in msg or 'tersedia' in msg:
        return ("Semua produk kita ready stok kok! 📦\n\n"
                "Stok paling update:\n"
                "🍓 Yogurt: 25-60 pcs per varian\n"
                "🏷️ Keychain: 20-100 pcs per desain\n\n"
                "Tapi kalau mau keychain custom desain sendiri, butuh waktu proses 3-5 hari ya. "
                "Mau pesan yang mana? 😊")

    # ===== PENGIRIMAN =====
    if 'kirim' in msg or 'ongkir' in msg or 'delivery' in msg or 'pengiriman' in msg:
        return ("Info pengiriman 📦:\n\n"
                "📍 Jakarta: 1-2 hari (flat Rp15.000)\n"
                "📍 Jabodetabek: 2-3 hari\n"
                "📍 Luar kota: 3-7 hari (sesuai JNE/JNT)\n\n"
                "Untuk yogurt, kita pakai packaging khusus dengan ice pack biar tetap fresh. "
                "Mau pesan? 😊")

    # ===== PEMBAYARAN =====
    if 'bayar' in msg or 'pembayaran' in msg or 'payment' in msg or 'va' in msg or 'transfer' in msg:
        return ("Cara pembayaran 💳:\n\n"
                "1️⃣ **Virtual Account BCA (otomatis)** - klik tombol Pesan di card produk, langsung dapet no VA\n"
                "2️⃣ **Transfer manual** - lewat WhatsApp, konfirmasi sama admin\n"
                "3️⃣ **COD** - untuk area Jakarta (konfirmasi dulu ya)\n\n"
                "Pembayaran VA otomatis dikonfirmasi 1-5 menit setelah transfer. Praktis! 😊")

    # ===== CONTACT / KONTAK =====
    if 'kontak' in msg or 'contact' in msg or 'wa' in msg or 'whatsapp' in msg or 'telepon' in msg:
        return ("Hubungi kami 📞:\n\n"
                "💬 WhatsApp: +62 812-3456-7890\n"
                "📧 Email: halo@y-key.id\n"
                "📷 Instagram: @y.key.id\n"
                "📍 Lokasi: Jakarta, Indonesia\n"
                "🕐 Jam: Senin-Sabtu, 09.00-21.00 WIB\n\n"
                "Atau klik tombol WhatsApp (hijau) di bawah web buat langsung chat admin! 😊")

    # ===== CAPTURE NAMA / WA =====
    if any(w in msg for w in ['nama saya', 'namaku', 'aku ', 'saya ']):
        return ("Mantap, salam kenal! 😊 Data kamu udah aku catat ya. "
                "Kalau mau pesan, tinggal klik tombol Pesan di produk yang kamu suka, "
                "atau chat WhatsApp admin buat custom. Ada yang mau aku bantu pilih? 🍓")

    # ===== DEFAULT REPLY =====
    return ("Hai! Aku Y-Key Bot 🤖 Aku bisa bantu kamu soal:\n\n"
            "🍓 **Yogurt** - 5 varian rasa (Strawberry, Blueberry, Mango, Plain, Matcha)\n"
            "🏷️ **Keychain** - 5 jenis (Acrylic, Resin, Pom-pom, Kulit, 3D)\n\n"
            "Tanya aja: 'rekomendasi yogurt buat sarapan', 'harga keychain', atau 'cara pesan'. "
            "Kamu lagi cari produk untuk siapa/acara apa nih? 😊")


if __name__ == '__main__':
    # Test chatbot
    print("🤖 Test Y-Key Chatbot")
    print("=" * 40)
    test_messages = [
        "halo",
        "mau rekomendasi yogurt buat sarapan budget 20rb",
        "harga keychain berapa?",
        "cara pesan gimana?",
        "mau keychain buat hadiah ultah",
    ]
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        print(f"🤖 Bot: {get_reply(msg)}")