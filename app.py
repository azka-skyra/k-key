"""
Y-Key Web Server - Pure Python (no npm, no frameworks)
SEMUA HALAMAN WAJIB LOGIN (kecuali /login itu sendiri)
"""

import http.server
import socketserver
import sqlite3
import json
import os
import re
import hashlib
import secrets
import uuid
import random
from urllib.parse import urlparse, parse_qs
from http.cookies import SimpleCookie
from datetime import datetime

# ===== KONFIGURASI =====
PORT = 8000
DB_PATH = "ykey.db"
SESSIONS = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

BRAND = {
    "name": "Y-Key",
    "tagline": "Yogurt Fresh & Keychain Custom",
    "whatsapp": "6281234567890",
    "whatsappDisplay": "+62 812-3456-7890",
    "email": "halo@y-key.id",
    "instagram": "@y.key.id",
    "address": "Jakarta, Indonesia",
    "hours": "Senin-Sabtu, 09.00-21.00 WIB",
}


# ===== DATABASE =====
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS admin_users (
        id TEXT PRIMARY KEY, username TEXT UNIQUE, password TEXT, name TEXT, role TEXT, created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY, name TEXT, category TEXT, price INTEGER, description TEXT, image TEXT, stock INTEGER, tags TEXT, created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id TEXT PRIMARY KEY, name TEXT, whatsapp TEXT, email TEXT, address TEXT, created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY, code TEXT UNIQUE, customer_id TEXT, status TEXT, total INTEGER, note TEXT,
        payment_method TEXT, payment_ref TEXT, va_number TEXT, shipping_address TEXT, created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id TEXT PRIMARY KEY, order_id TEXT, product_id TEXT, qty INTEGER, price INTEGER, subtotal INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (
        id TEXT PRIMARY KEY, customer_id TEXT, wa_number TEXT, visitor_name TEXT, source TEXT, status TEXT, created_at TEXT, updated_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id TEXT PRIMARY KEY, session_id TEXT, role TEXT, content TEXT, created_at TEXT
    )''')
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DB_PATH}")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()[:32]


def check_admin_auth(headers):
    cookie_header = headers.get('Cookie', '')
    if not cookie_header:
        return None
    cookie = SimpleCookie()
    try:
        cookie.load(cookie_header)
    except:
        return None
    token = cookie.get('admin_session')
    if not token or token.value not in SESSIONS:
        return None
    return SESSIONS[token.value]


def create_session(admin_data):
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = admin_data
    return token


def require_auth(headers):
    return check_admin_auth(headers)


def generate_va_number():
    prefix = "8077"
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    return f"{prefix}{random_part}"


def generate_order_code():
    now = datetime.now()
    ymd = now.strftime("%Y%m%d")
    rand = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    return f"ORD-{ymd}-{rand}"


# ===== HANDLER =====
class YKeyHandler(http.server.SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[{self.command}] {self.path}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html_content, status=200):
        body = html_content.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file_response(self, filepath, content_type):
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode('utf-8'))
        except:
            return {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # ===== ROUTING =====
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        next_url = query.get('next', ['/'])[0]

        # ===== PUBLIC ROUTES (no auth needed) =====
        # Login page
        if path == '/login':
            # Kalau udah login, redirect ke next_url
            if require_auth(self.headers):
                safe_next = next_url if next_url and next_url.startswith('/') else '/admin'
                self.redirect(safe_next)
            else:
                self.serve_template('login.html')
            return

        # Static files (CSS, JS) — boleh tanpa auth biar halaman login bisa load
        if path.startswith('/static/'):
            self.serve_static_file(path)
            return

        # API login check (public)
        if path == '/api/admin/check':
            admin = require_auth(self.headers)
            if admin:
                self.send_json({"authenticated": True, "admin": admin})
            else:
                self.send_json({"authenticated": False}, 401)
            return

        # ===== PROTECTED ROUTES (require auth) =====
        admin = require_auth(self.headers)
        if not admin:
            # Redirect ke login dengan parameter next=URL yang dituju
            self.redirect(f'/login?next={path}')
            return

        # === Authenticated routes ===
        if path == '/' or path == '/index.html':
            self.serve_template('index.html')
        elif path == '/admin' or path == '/admin/':
            self.serve_template('admin.html')
        elif path == '/api/products':
            self.api_get_products()
        elif path == '/api/admin/stats':
            self.api_admin_stats()
        elif path == '/api/admin/orders':
            self.api_admin_orders(parsed.query)
        elif path == '/api/admin/customers':
            self.api_admin_customers(parsed.query)
        elif path == '/api/admin/chats':
            self.api_admin_chats(parsed.query)
        elif path == '/api/admin/products':
            self.api_admin_products()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Public POST: login only
        if path == '/api/admin/login':
            self.api_admin_login()
            return

        # All other POST routes require auth
        if not require_auth(self.headers):
            self.send_json({"error": "Unauthorized. Silakan login dulu."}, 401)
            return

        if path == '/api/chat':
            self.api_chat()
        elif path == '/api/orders/quick':
            self.api_quick_order()
        elif path == '/api/admin/orders/update':
            self.api_admin_update_order()
        else:
            self.send_json({"error": "Endpoint not found"}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/admin/logout':
            self.api_admin_logout()
        else:
            self.send_json({"error": "Endpoint not found"}, 404)

    def serve_template(self, filename):
        filepath = os.path.join(TEMPLATES_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_html(content)
        except FileNotFoundError:
            self.send_html('<h1>404 - Template not found</h1>', 404)

    def serve_static_file(self, path):
        relative_path = path[len('/static/'):]
        filepath = os.path.join(STATIC_DIR, relative_path)
        ext = os.path.splitext(filepath)[1].lower()
        content_types = {
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.html': 'text/html; charset=utf-8',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
        }
        content_type = content_types.get(ext, 'application/octet-stream')
        self.send_file_response(filepath, content_type)

    def redirect(self, location):
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()

    # ===== PUBLIC APIs =====
    def api_get_products(self):
        conn = get_db()
        products = conn.execute('SELECT * FROM products ORDER BY category, price').fetchall()
        result = [dict(p) for p in products]
        conn.close()
        self.send_json({"products": result})

    def api_chat(self):
        body = self.read_body()
        message = body.get('message', '').strip()
        session_id = body.get('sessionId')
        visitor_name = body.get('visitorName')
        wa_number = body.get('waNumber')

        if not message:
            self.send_json({"error": "Message required"}, 400)
            return

        conn = get_db()
        session = None
        if session_id:
            session = conn.execute('SELECT * FROM chat_sessions WHERE id = ?', (session_id,)).fetchone()

        if not session:
            customer_id = None
            if wa_number:
                customer = conn.execute('SELECT id FROM customers WHERE whatsapp = ?', (wa_number,)).fetchone()
                if customer:
                    customer_id = customer['id']
            new_session_id = str(uuid.uuid4())
            conn.execute(
                'INSERT INTO chat_sessions (id, customer_id, wa_number, visitor_name, source, status) VALUES (?, ?, ?, ?, ?, ?)',
                (new_session_id, customer_id, wa_number, visitor_name, 'WEB', 'ACTIVE')
            )
            conn.commit()
            session_id = new_session_id
        else:
            session_id = session['id']

        msg_id = str(uuid.uuid4())
        conn.execute(
            'INSERT INTO chat_messages (id, session_id, role, content) VALUES (?, ?, ?, ?)',
            (msg_id, session_id, 'user', message)
        )
        conn.execute('UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (session_id,))

        phone_match = re.search(r'(?:62|0)8\d{8,12}', message)
        if phone_match:
            captured_wa = phone_match.group(0)
            if captured_wa.startswith('0'):
                captured_wa = '62' + captured_wa[1:]
            cust_id = f'cust-{captured_wa}'
            existing = conn.execute('SELECT id FROM customers WHERE id = ?', (cust_id,)).fetchone()
            if not existing:
                customer_name = visitor_name or f'Visitor {captured_wa[-4:]}'
                conn.execute(
                    'INSERT INTO customers (id, name, whatsapp) VALUES (?, ?, ?)',
                    (cust_id, customer_name, captured_wa)
                )
            conn.execute(
                'UPDATE chat_sessions SET customer_id = ?, wa_number = ? WHERE id = ?',
                (cust_id, captured_wa, session_id)
            )

        products = conn.execute('SELECT name, category, price, description, tags FROM products ORDER BY category, price').fetchall()
        from chatbot import get_reply
        reply = get_reply(message, [dict(p) for p in products])

        ai_msg_id = str(uuid.uuid4())
        conn.execute(
            'INSERT INTO chat_messages (id, session_id, role, content) VALUES (?, ?, ?, ?)',
            (ai_msg_id, session_id, 'assistant', reply)
        )
        conn.commit()
        conn.close()

        self.send_json({"sessionId": session_id, "reply": reply})

    def api_quick_order(self):
        body = self.read_body()
        product_id = body.get('productId')
        qty = body.get('qty', 1)
        visitor_name = body.get('visitorName')
        wa_number = body.get('waNumber')
        note = body.get('note')

        if not product_id or qty < 1:
            self.send_json({"error": "productId & qty wajib diisi"}, 400)
            return

        conn = get_db()
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if not product:
            self.send_json({"error": "Produk tidak ditemukan"}, 404)
            conn.close()
            return

        if product['stock'] < qty:
            self.send_json({"error": f"Stok tidak cukup. Tersedia: {product['stock']}"}, 400)
            conn.close()
            return

        customer_id = None
        if wa_number:
            normalized_wa = wa_number if wa_number.startswith('62') else '62' + wa_number.lstrip('0')
            cust_id = f'cust-{normalized_wa}'
            existing = conn.execute('SELECT id FROM customers WHERE id = ?', (cust_id,)).fetchone()
            if existing:
                customer_id = cust_id
                if visitor_name:
                    conn.execute('UPDATE customers SET name = ? WHERE id = ?', (visitor_name, cust_id))
            else:
                customer_name = visitor_name or f'Visitor {normalized_wa[-4:]}'
                conn.execute(
                    'INSERT INTO customers (id, name, whatsapp) VALUES (?, ?, ?)',
                    (cust_id, customer_name, normalized_wa)
                )
                customer_id = cust_id
        else:
            customer_id = f'cust-anon-{int(datetime.now().timestamp())}'
            customer_name = visitor_name or 'Walk-in Customer'
            conn.execute('INSERT INTO customers (id, name) VALUES (?, ?)', (customer_id, customer_name))

        subtotal = product['price'] * qty
        shipping = 15000
        total = subtotal + shipping
        order_code = generate_order_code()
        va_number = generate_va_number()
        order_id = str(uuid.uuid4())

        conn.execute(
            '''INSERT INTO orders (id, code, customer_id, status, total, note, payment_method, payment_ref, va_number, shipping_address)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (order_id, order_code, customer_id, 'PENDING', total,
             note or f'Order {qty}x {product["name"]}',
             'MIDTRANS_VA', f'MID-SIM-{order_code}', va_number,
             'Belum diisi (akan dikonfirmasi via WA)')
        )

        item_id = str(uuid.uuid4())
        conn.execute(
            'INSERT INTO order_items (id, order_id, product_id, qty, price, subtotal) VALUES (?, ?, ?, ?, ?, ?)',
            (item_id, order_id, product_id, qty, product['price'], subtotal)
        )

        conn.commit()
        conn.close()

        self.send_json({
            "order": {
                "id": order_id, "code": order_code, "status": "PENDING",
                "total": total, "vaNumber": va_number, "paymentMethod": "MIDTRANS_VA",
            },
            "customer": {"id": customer_id, "name": visitor_name or "Walk-in Customer"},
            "product": {"name": product['name'], "qty": qty, "price": product['price'], "subtotal": subtotal},
            "shipping": shipping,
            "instructions": [
                f"Bayar Rp{total:,} ke VA BCA: {va_number}",
                "Pembayaran akan dikonfirmasi otomatis dalam 1-5 menit",
                "Simpan kode order kamu untuk cek status",
            ]
        })

    # ===== ADMIN APIs =====
    def api_admin_login(self):
        body = self.read_body()
        username = body.get('username', '')
        password = body.get('password', '')
        next_url = body.get('next', '/admin')

        if not username or not password:
            self.send_json({"error": "Username & password wajib diisi"}, 400)
            return

        conn = get_db()
        admin = conn.execute('SELECT * FROM admin_users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if not admin:
            self.send_json({"error": "Username tidak ditemukan"}, 401)
            return

        if admin['password'] != hash_password(password):
            self.send_json({"error": "Password salah"}, 401)
            return

        token = create_session({
            "id": admin['id'], "username": admin['username'],
            "name": admin['name'], "role": admin['role'],
        })

        # Sanitize next_url - hanya boleh path relatif
        if not next_url or not next_url.startswith('/') or next_url.startswith('//'):
            next_url = '/admin'

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Set-Cookie', f'admin_session={token}; Path=/; HttpOnly; Max-Age=604800')
        body = json.dumps({"ok": True, "message": "Login berhasil", "next": next_url}).encode('utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def api_admin_logout(self):
        cookie_header = self.headers.get('Cookie', '')
        cookie = SimpleCookie()
        try:
            cookie.load(cookie_header)
            token = cookie.get('admin_session')
            if token and token.value in SESSIONS:
                del SESSIONS[token.value]
        except:
            pass

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Set-Cookie', 'admin_session=; Path=/; Max-Age=0')
        body = json.dumps({"ok": True}).encode('utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def api_admin_stats(self):
        if not require_auth(self.headers):
            self.send_json({"error": "Unauthorized"}, 401)
            return

        conn = get_db()
        total_customers = conn.execute('SELECT COUNT(*) as c FROM customers').fetchone()['c']
        total_orders = conn.execute('SELECT COUNT(*) as c FROM orders').fetchone()['c']
        total_products = conn.execute('SELECT COUNT(*) as c FROM products').fetchone()['c']
        total_chats = conn.execute('SELECT COUNT(*) as c FROM chat_sessions').fetch