"""
Seed database Y-Key dengan data dummy
Run: python seed.py
"""

import sqlite3
import hashlib
import uuid
from datetime import datetime

DB_PATH = "ykey.db"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()[:32]


def seed():
    # Connect & init
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Drop existing tables (clean slate)
    for table in ['chat_messages', 'chat_sessions', 'order_items', 'orders', 'customers', 'products', 'admin_users']:
        c.execute(f'DROP TABLE IF EXISTS {table}')

    # Create tables (same as app.py init_db)
    c.execute('''CREATE TABLE admin_users (
        id TEXT PRIMARY KEY, username TEXT UNIQUE, password TEXT, name TEXT, role TEXT, created_at TEXT
    )''')
    c.execute('''CREATE TABLE products (
        id TEXT PRIMARY KEY, name TEXT, category TEXT, price INTEGER, description TEXT, image TEXT, stock INTEGER, tags TEXT, created_at TEXT
    )''')
    c.execute('''CREATE TABLE customers (
        id TEXT PRIMARY KEY, name TEXT, whatsapp TEXT, email TEXT, address TEXT, created_at TEXT
    )''')
    c.execute('''CREATE TABLE orders (
        id TEXT PRIMARY KEY, code TEXT UNIQUE, customer_id TEXT, status TEXT, total INTEGER, note TEXT,
        payment_method TEXT, payment_ref TEXT, va_number TEXT, shipping_address TEXT, created_at TEXT
    )''')
    c.execute('''CREATE TABLE order_items (
        id TEXT PRIMARY KEY, order_id TEXT, product_id TEXT, qty INTEGER, price INTEGER, subtotal INTEGER
    )''')
    c.execute('''CREATE TABLE chat_sessions (
        id TEXT PRIMARY KEY, customer_id TEXT, wa_number TEXT, visitor_name TEXT, source TEXT, status TEXT, created_at TEXT, updated_at TEXT
    )''')
    c.execute('''CREATE TABLE chat_messages (
        id TEXT PRIMARY KEY, session_id TEXT, role TEXT, content TEXT, created_at TEXT
    )''')

    print("🌱 Seeding database...")

    # ===== ADMIN =====
    admin_id = str(uuid.uuid4())
    c.execute('INSERT INTO admin_users VALUES (?, ?, ?, ?, ?, ?)',
              (admin_id, 'admin', hash_password('admin123'), 'Admin Y-Key', 'ADMIN', datetime.now().isoformat()))
    print("✅ Admin created: admin / admin123")

    # ===== YOGURT PRODUCTS =====
    yogurts = [
        ('Yogurt Strawberry Fresh', 'YOGURT', 15000, 'Yogurt premium dengan strawberry fresh, creamy dan segar. Cocok untuk sarapan atau camilan sehat.', '🍓', 50, 'best-seller,fresh'),
        ('Yogurt Blueberry Blast', 'YOGURT', 17000, 'Yogurt blueberry dengan tekstur lembut dan rasa manis-asam yang pas. Kaya antioksidan.', '🫐', 40, 'best-seller,antioxidant'),
        ('Yogurt Mango Tropical', 'YOGURT', 16000, 'Yogurt dengan potongan mangga segar, memberikan sensasi tropical di setiap sendok.', '🥭', 35, 'tropical,fresh'),
        ('Yogurt Plain Original', 'YOGURT', 12000, 'Yogurt plain tanpa tambahan gula, cocok untuk yang suka rasa asli yogurt. Vegan friendly.', '🥛', 60, 'vegan,plain'),
        ('Yogurt Matcha Latte', 'YOGURT', 18000, 'Yogurt matcha latte premium dengan teh hijau pilihan, kombinasi unik yang menenangkan.', '🍵', 25, 'premium,matcha'),
    ]
    for name, cat, price, desc, img, stock, tags in yogurts:
        pid = f'yogurt-{name.lower().replace(" ", "-")}'
        c.execute('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (pid, name, cat, price, desc, img, stock, tags, datetime.now().isoformat()))
    print(f"✅ {len(yogurts)} yogurt products created")

    # ===== KEYCHAIN PRODUCTS =====
    keychains = [
        ('Keychain Acrylic Custom Nama', 'KEYCHAIN', 25000, 'Keychain acrylic custom dengan nama kamu. Bisa request desain, warna, dan ukuran. Foto bisa di-embed.', '🏷️', 100, 'custom,best-seller'),
        ('Keychain Resin Bunga', 'KEYCHAIN', 35000, 'Keychain resin dengan bunga asli di dalamnya. Handmade, setiap piece unik.', '🌸', 30, 'handmade,premium'),
        ('Keychain Pom-pom Lucu', 'KEYCHAIN', 20000, 'Keychain pom-pom lembut dengan berbagai warna pilihan. Cocok untuk gantungan tas.', '🧶', 80, 'cute,best-seller'),
        ('Keychain Kulit Premium', 'KEYCHAIN', 45000, 'Keychain kulit asli dengan finishing premium. Bisa emboss nama. Tahan lama dan elegan.', '👜', 20, 'premium,leather'),
        ('Keychain Karakter 3D', 'KEYCHAIN', 30000, 'Keychain karakter 3D printed dengan berbagai pilihan: hewan, anime, robot. Custom request tersedia.', '🎨', 50, '3d,custom'),
    ]
    for name, cat, price, desc, img, stock, tags in keychains:
        pid = f'keychain-{name.lower().replace(" ", "-")}'
        c.execute('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (pid, name, cat, price, desc, img, stock, tags, datetime.now().isoformat()))
    print(f"✅ {len(keychains)} keychain products created")

    # ===== DEMO CUSTOMERS =====
    demo_customers = [
        ('Dewi Lestari', '6281234567890', 'dewi@example.com', 'Jakarta Selatan'),
        ('Andi Pratama', '6281234567891', 'andi@example.com', 'Bandung'),
        ('Siti Nurhaliza', '6281234567892', 'siti@example.com', 'Surabaya'),
        ('Budi Santoso', '6281234567893', 'budi@example.com', 'Yogyakarta'),
        ('Rina Wati', '6281234567894', 'rina@example.com', 'Semarang'),
    ]
    for name, wa, email, address in demo_customers:
        cust_id = f'cust-{wa}'
        c.execute('INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)',
                  (cust_id, name, wa, email, address, datetime.now().isoformat()))
    print(f"✅ {len(demo_customers)} demo customers created")

    # ===== DEMO ORDERS =====
    demo_orders = [
        (0, [('yogurt-yogurt-strawberry-fresh', 2), ('keychain-keychain-pom-pom-lucu', 1)], 'PAID'),
        (1, [('keychain-keychain-acrylic-custom-nama', 1)], 'PENDING'),
        (2, [('yogurt-yogurt-blueberry-blast', 3), ('yogurt-yogurt-mango-tropical', 1)], 'PAID'),
        (3, [('keychain-keychain-kulit-premium', 1), ('keychain-keychain-resin-bunga', 1)], 'SHIPPED'),
        (4, [('yogurt-yogurt-matcha-latte', 2)], 'DONE'),
        (0, [('keychain-keychain-karakter-3d', 2)], 'PENDING'),
    ]

    for i, (cust_idx, items, status) in enumerate(demo_orders):
        customer = demo_customers[cust_idx]
        cust_id = f'cust-{customer[1]}'
        total = 0
        for pid, qty in items:
            p = c.execute('SELECT price FROM products WHERE id = ?', (pid,)).fetchone()
            total += p['price'] * qty

        order_id = str(uuid.uuid4())
        order_code = f'ORD-20261026-{i+1:04d}'
        va_number = f'8077{"".join([str(__import__("random").randint(0,9)) for _ in range(12)])}'

        c.execute('''INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (order_id, order_code, cust_id, status, total, f'Demo order {i+1}',
                   'MIDTRANS_VA', f'MID-SIM-{order_code}', va_number, customer[3], datetime.now().isoformat()))

        for pid, qty in items:
            p = c.execute('SELECT price FROM products WHERE id = ?', (pid,)).fetchone()
            item_id = str(uuid.uuid4())
            c.execute('INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)',
                      (item_id, order_id, pid, qty, p['price'], p['price'] * qty))

    print(f"✅ {len(demo_orders)} demo orders created")

    conn.commit()
    conn.close()

    print("\n🎉 Seeding complete!")
    print("👤 Admin login: admin / admin123")
    print(f"📂 Database: {DB_PATH}")


if __name__ == '__main__':
    seed()